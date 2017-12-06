import aiohttp
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class Record:
    __slots__ = (
        'request',
        'method',
        'location',
        'resource',
        'status',
        'auth_id',
        'user_id',
        'sql_count',
        'sql_time',
        'http_count',
        'http_time',
        'cache_count',
        'cache_time',
        'cache_misses',
    )

    def __str__(self):
        return '<Record %s %s=%d %d:%d %s %d:%d %d:%d %d:%d:%d>' % (
            self.request,
            self.method,
            self.status,
            self.auth_id,
            self.user_id,
            self.resource,
            self.sql_count,
            self.sql_time,
            self.http_count,
            self.http_time,
            self.cache_count,
            self.cache_time,
            self.cache_misses,
        )

    @classmethod
    def from_log(cls, line):
        data = json.loads(line)

        self = cls()
        self.request = str(data['id'])
        self.method = str(data['m'])
        self.location = str(data['uri'])
        self.resource = str(data['tr'])
        self.status = int(data['s'])
        self.auth_id = int(data['aui'])
        self.user_id = int(data['ui'])
        self.sql_count = int(data['bsc'])
        self.sql_time = int(data['bst'])
        self.http_count = int(data['bhc'])
        self.http_time = int(data['bht'])
        self.cache_count = int(data['bcc'])
        self.cache_time = int(data['bct'])
        self.cache_misses = int(data['bcm'])

        return self


class Metric:
    __slots__ = (
        'sql_count',
        'sql_time',
        'http_count',
        'http_time',
        'cache_count',
        'cache_time',
        'cache_misses',
    )

    def __str__(self):
        return '<Metric %d:%d %d:%d %d:%d:%d>' % (
            self.sql_count,
            self.sql_time,
            self.http_count,
            self.http_time,
            self.cache_count,
            self.cache_time,
            self.cache_misses,
        )

    @classmethod
    def from_response(cls, response):
        self = cls()
        headers = response.headers
        self.sql_count = int(headers['X-Backend-Sql-Count'])
        self.sql_time = int(headers['X-Backend-Sql-Time'])
        self.http_count = int(headers['X-Backend-Http-Count'])
        self.http_time = int(headers['X-Backend-Http-Time'])
        self.cache_count = int(headers['X-Backend-Cache-Count'])
        self.cache_time = int(headers['X-Backend-Cache-Time'])
        self.cache_misses = int(headers['X-Backend-Cache-Misses'])
        return self


class Player:
    def __init__(self, prefix, log, filters=None):
        self._recgen = self._records(log, filters)
        self._prefix = prefix
        self._total_records = Metric()
        self._total_metrics = Metric()

    def start(self, count):
        loop = asyncio.get_event_loop()
        coros = [self._start() for _ in range(count)]
        loop.run_until_complete(asyncio.gather(*coros))
        return self._total_records, self._total_metrics

    def _records(self, log, filters=None):
        def filtered(record):
            for attr, value in filters.items():
                if getattr(record, attr) != value:
                    return True
            return False

        for line in log:
            try:
                record = Record.from_log(line)
            except Exception:
                continue
            if record.method != 'GET':
                continue
            if record.resource == '':
                continue
            if filters and filtered(record):
                continue
            yield record

    def _aggregate(self, record, metric):
        for key in Metric.__slots__:
            value = getattr(self._total_records, key, 0)
            current = getattr(record, key, 0)
            setattr(self._total_records, key, value + current)

        for key in Metric.__slots__:
            value = getattr(self._total_metrics, key, 0)
            current = getattr(metric, key, 0)
            setattr(self._total_metrics, key, value + current)

    async def _start(self):
        for record in self._recgen:
            metric = await self._fire(record)
            if metric:
                self._aggregate(record, metric)

    async def _fire(self, record):
        message = 'Firing record %s'
        logger.debug(message, record)

        location = self._prefix + record.location
        headers = {'X-Trg-Auth-User-Id': str(record.auth_id),
                   'X-Trg-User-Id': str(record.user_id)}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(location, headers=headers) as response:
                    await response.text()
        except Exception as exception:
            message = 'Firing failed: exception %r for record %s'
            logger.debug(message, exception, record)
            return None

        if response.status != record.status:
            message = 'Firing failed: incorrect status %s for record %s'
            logger.debug(message, response.status, record)
            return None

        metric = Metric.from_response(response)

        message = 'Fired record %s metric %s'
        logger.debug(message, record, metric)

        return metric
