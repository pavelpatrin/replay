import logging

from replay.player import Player, Metric

logger = logging.getLogger(__name__)


def main(target, parallel, log):
    player = Player(target, log)
    records, metrics = player.start(parallel)

    for x in Metric.__slots__:
        message = 'Result metric %s: %d %d'
        record = getattr(records, x, 0)
        metric = getattr(metrics, x, 0)
        logger.info(message, x, record, metric)
