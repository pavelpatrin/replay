import logging

from replay.player import Player
from replay.structs import Metric

logger = logging.getLogger(__name__)


def main(target, parallel, logfile, filters):
    player = Player(target, logfile, filters)
    reference, gathered = player.start(parallel)

    for x in Metric.__slots__:
        message = 'Result metric %s: %d %d'
        record = getattr(reference, x, 0)
        metric = getattr(gathered, x, 0)
        logger.info(message, x, record, metric)
