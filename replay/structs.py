class Record:
    __slots__ = (
        'request',
        'method',
        'location',
        'resource',
        'status',
        'auth_id',
        'user_id',
    )

    def __str__(self):
        return '<Record %s %s=%d %d:%d %s>' % (
            self.request,
            self.method,
            self.status,
            self.auth_id,
            self.user_id,
            self.resource,
        )

    @classmethod
    def from_entry(cls, entry):
        self = cls()
        self.request = str(entry['id'])
        self.method = str(entry['m'])
        self.location = str(entry['uri'])
        self.resource = str(entry['tr'])
        self.status = int(entry['s'])
        self.auth_id = int(entry['aui'])
        self.user_id = int(entry['ui'])

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
    def from_entry(cls, entry):
        self = cls()
        self.sql_count = int(entry['bsc'])
        self.sql_time = int(entry['bst'])
        self.http_count = int(entry['bhc'])
        self.http_time = int(entry['bht'])
        self.cache_count = int(entry['bcc'])
        self.cache_time = int(entry['bct'])
        self.cache_misses = int(entry['bcm'])

        return self

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
