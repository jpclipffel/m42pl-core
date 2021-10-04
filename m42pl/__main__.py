import argparse
import logging, logging.handlers

from m42pl.mains import commands


def main():
    # Root parser and subparser
    parser = argparse.ArgumentParser('m42pl')
    subparser = parser.add_subparsers(dest='command')
    subparser.required = True
    # Actions (subparser's parsers) setup
    _commands = [
        cmd(subparser) for cmd in commands
    ]
    # Parse arguments
    args = parser.parse_args()
    # Setup logging
    # logger = logging.getLogger('m42pl')
    logger = logging.getLogger()
    logger.setLevel(args.log_level.upper())
    handler = logging.StreamHandler()
    handler.setLevel(args.log_level.upper())
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s() - %(message)s'
    ))
    logger.addHandler(handler)
    # Run
    args.func(args)


if __name__ == "__main__":
    main()
