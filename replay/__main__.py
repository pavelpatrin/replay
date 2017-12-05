import argparse
import logging

from replay.control import main


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--target',
        dest='target',
        required=True,
        type=str,
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

    format = '[%(asctime)s %(levelname)s %(name)s] %(message)s'
    logging.basicConfig(format=format, level=args.logging)

    main(args.target, args.log)
