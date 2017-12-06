import aiohttp
import asyncio
import logging
import json

from replay.structs import Record, Metric

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, prefix, log, filters=None):
        self._source = self._records(log, filters)
        self._prefix = prefix
        self._reference = Metric()
        self._gathered = Metric()

    def start(self, count):
        loop = asyncio.get_event_loop()
        coros = [self._start() for _ in range(count)]
        loop.run_until_complete(asyncio.gather(*coros))
        return self._reference, self._gathered

    def _records(self, log, filters=None):
        def filtered(record):
            for attr, value in filters.items():
                if getattr(record, attr) != value:
                    return True
            return False

        for line in log:
            try:
                entry = json.loads(line)
                record = Record.from_entry(entry)
                metric = Metric.from_entry(entry)
            except Exception:
                continue
            if record.method != 'GET':
                continue
            if record.resource == '':
                continue
            if filters and filtered(record):
                continue
            yield record, metric

    def _aggregate(self, reference, gathered):
        for key in Metric.__slots__:
            value = getattr(self._reference, key, 0)
            current = getattr(reference, key, 0)
            setattr(self._reference, key, value + current)

        for key in Metric.__slots__:
            value = getattr(self._gathered, key, 0)
            current = getattr(gathered, key, 0)
            setattr(self._gathered, key, value + current)

    async def _start(self):
        for record, reference in self._source:
            gathered = await self._fire(record, reference)
            if gathered:
                self._aggregate(reference, gathered)

    async def _fire(self, record, reference):
        message = 'Firing record %s with %s'
        logger.debug(message, record, reference)

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

        message = 'Fired record %s got %s'
        logger.debug(message, record, metric)

        return metric
