import argparse
import logging
import json

from replay.control import main
from replay.logging import configure


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--target',
        dest='target',
        required=True,
        type=str,
    )

    parser.add_argument(
        '--parallel',
        dest='parallel',
        default=1,
        type=int,
    )

    parser.add_argument(
        '--log-file',
        dest='logfile',
        required=True,
        type=argparse.FileType('r'),
    )

    parser.add_argument(
        '--logging',
        dest='logging',
        type=str,
        default=logging.INFO,
    )

    parser.add_argument(
        '--filters',
        dest='filters',
        type=json.loads,
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    configure(args.logging)
    main(
        args.target,
        args.parallel,
        args.logfile,
        args.filters
    )
