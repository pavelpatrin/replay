import json
import logging

import requests

logger = logging.getLogger(__name__)


class Record:
    __slots__ = (
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
        return '<Record %s=%d %d:%d %s %d:%d %d:%d %d:%d:%d>' % (
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
    def from_json(cls, line):
        data = json.loads(line)

        self = cls()
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
    def __init__(self, url, log):
        self._url = url
        self._log = log

    def start(self):
        for line in self._log:
            try:
                record = Record.from_json(line)
            except Exception:
                continue
            else:
                if record.method != 'GET':
                    continue

            yield record, self.fire(record)

    def fire(self, record):
        url = self._url + record.location

        try:
            response = requests.get(url, headers={
                'X-Trg-Auth-User-Id': str(record.auth_id),
                'X-Trg-User-Id': str(record.user_id),
            })
        except Exception as e:
            message = 'Firing failed: unhandled exception'
            logger.debug(message, extra={
                'record': record,
                'exception': e,
            })
            return None

        if response.status_code != record.status:
            message = 'Firing failed: incorrect status'
            logger.debug(message, extra={
                'record': record,
                'response': response,
            })
            return None

        logger.debug('Firing ok', extra={
            'record': record,
            'response': response,
        })

        return Metric.from_response(response)
