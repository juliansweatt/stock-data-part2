#!/usr/bin/env python3
import argparse
from stock import Tickers
from stock import Fetcher

def __int_in_range__(i):
    """Argument filter for an integer between 0 and 110.

    :param str i: The number to filter.
    :return: The given number.
    :rtype: int
    :raises ArgumentTypeError: If the number is not an integer between 0 and 110.
    """
    inti = int(i)
    if inti < 0 or inti > 110:
        raise argparse.ArgumentTypeError("0 < ticker_count <= 110 is not satisfied by %d" % i)
    return inti

def parseInput():
    """Parse arguments from standard input.

    :return: Parsed arguments.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", type=str, choices=("Ticker","Fetcher","Query"), help="Operation to perform.", required=True)
    parser.add_argument("--ticker_count", type=__int_in_range__, help="Number of Tickers to Retrieve (0 < ticker_count <= 110)", required=(parser.parse_known_args()[0].operation in ("Ticker","Fetcher")))
    return parser.parse_args()

if __name__ == '__main__':
    # Parse Input
    args = parseInput()

    # Execute Cooresponding Operation
    if args.operation == "Ticker":
        Tickers(args.ticker_count).save_tickers()
    elif args.operation == "Fetcher":
        Fetcher().fetch(60) #bookmark testing as class wihout DB