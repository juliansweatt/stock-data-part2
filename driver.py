#!/usr/bin/env python3
import argparse
import re
from stock import Tickers
from stock import Fetcher
from stock import Query

def __valid_time(s):
    """Argument filter for a string with a valid time of format HH:MM

    :param str s: The string to filter.
    :return: The given time string
    :rtype: str
    :raises ArgumentTypeError: If the time string is in an invalid format.
    """
    temp = re.findall(r'^([0-2][0-9]):([0-5][0-9])$', s)
    if len(temp) == 1 and len(temp[0]) == 2:
        return s
    else:
        raise argparse.ArgumentTypeError('Time Format Expected (HH:MM such that 00 < HH < 24 and 00 < MM < 59)')

def __int_in_range(i):
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
    parser.add_argument("--ticker", type=str, help="...", required=(parser.parse_known_args()[0].operation == "Query"))
    parser.add_argument("--ticker_count", type=__int_in_range, help="Number of Tickers to Retrieve (0 < ticker_count <= 110)", required=(parser.parse_known_args()[0].operation in ("Ticker","Fetcher")))
    parser.add_argument("--time", type=__valid_time, help="Specify Time to Query", required=(parser.parse_known_args()[0].operation == "Query"))
    parser.add_argument("--time_limit", type=int, help="...", required=(parser.parse_known_args()[0].operation == "Fetcher"))
    parser.add_argument("--db", type=str, help="...", required=(parser.parse_known_args()[0].operation in ("Query","Fetcher")))
    return parser.parse_args()

if __name__ == '__main__':
    # Parse Input
    args = parseInput()

    # Execute Cooresponding Operation
    if args.operation == "Ticker":
        Tickers(args.ticker_count).save_tickers()
    elif args.operation == "Fetcher":
        Fetcher(args.db).fetch(args.time_limit)
    elif args.operation == "Query":
        Query(args.time, args.db, args.ticker).fetch_and_print()