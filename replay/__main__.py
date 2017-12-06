import argparse
import logging

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
        dest='log',
        required=True,
        type=argparse.FileType('r'),
    )

    parser.add_argument(
        '--logging',
        dest='logging',
        type=str,
        default=logging.INFO,
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    configure(args.logging)
    main(args.target, args.parallel, args.log)
