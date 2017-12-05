import logging

from replay.player import Player

logger = logging.getLogger(__name__)

metrics = (
    'sql_count',
    'sql_time',
    'http_count',
    'http_time',
    'cache_count',
    'cache_time',
    'cache_misses',
)


def main(target, log):
    recorded = {x: 0 for x in metrics}
    measured = {x: 0 for x in metrics}
    gen = Player(target, log).start()

    for index, (record, metric) in enumerate(gen):
        if not metric:
            message = 'Failed to get metric for %s'
            logger.warning(message, record)
            continue

        message = 'Got metric for %s: %s'
        logger.info(message, record, metric)

        for x in metrics:
            recorded[x] += getattr(record, x)
            measured[x] += getattr(metric, x)

    for x in metrics:
        message = 'Result metric %s: %d %d'
        logger.info(message, x, recorded[x], measured[x])
