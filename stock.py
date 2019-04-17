#!/usr/bin/env python3
import sys
import requests
import re
import datetime
import os
import time
import sqlite3
from iex import Stock

class Tickers:
    """Class used to save tickers to a file.

    :var str nasdaq_url: The National Association of Securities Dealers Automated Quotations URL to be crawled to retrieve tickers. - Default *http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQrender=download*
    :var str outfile: File path to write tickers to. - Default: *tickers.txt*
    """

    # Ticker Settings
    def __init__(self, max_tickers):
        """Construct a ticker object.

        :param max_tickers: The maximum number of tickers to retrieve.
        :type max_tickers: 0 <= int <= 110
        """
        self.__NASDAQ_URL = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQrender=download"
        self.__OUTFILE = "tickers.txt"
        self.__PATTERN_SYMBOLS = re.compile(r'symbol/([a-z]*)')
        self.__PATTERN_NEXT_PAGE = re.compile(r'<a href="(.{90,105})" id="main_content_lb_NextPage"')
        self.maximum = max_tickers

    @property
    def outfile(self):
        return self.__OUTFILE

    @outfile.setter
    def outfile(self,of):
        self.__OUTFILE = of

    @property
    def nasdaq_url(self):
        return self.__NASDAQ_URL

    @nasdaq_url.setter
    def nasdaq_url(self,url):
        self.__NASDAQ_URL = url

    def print_to_file(self, outFile, tickerSet):
        """Prints a set to a file.

        :Details: Prints a set to an output file, such that each element of the set is a new line of the file.
        :param int outfile: The name/path of the output file
        :param set tickerSet: Set to print to the outfile
        """

        f = open(outFile, "w")
        for ticker in tickerSet:
            f.write(ticker + "\n")
        f.close()

    def get_tickers_from_url(self, url, currentTickers):
        """Gets stock tickers from a specified NASDAQ url.

        :Details: Function retrieves a maximum amount of tickers from a specified URL. A *NASDAQ URL* is expected. The maximum quantity takes in to account the current amount of tickers already found outside the function. The function will return whenever the maximum is reached or the page tickers are exhausted. The intent is to feed this function each successive page URL.
        :param str url: URL to retrieve stock data from.
        :param int currentTickers: The current amount of tickers already retrieved.
        :return: Retrieved tickers.
        :rtype: set of str
        """

        # Get Initial Web Page
        response = requests.get(url)

        # Harvest Tickers
        tickers = set(re.findall(self.__PATTERN_SYMBOLS, response.text))

        # Check Tickers for Validity & Limit
        validTickers = set()
        for ticker in tickers:
            if len(validTickers)+currentTickers >= self.maximum:
                print(len(validTickers)+currentTickers,"Valid Ticker(s) Found. User Specified Limit Reached.")
                break
            try:
                Stock(ticker).price()
                validTickers.add(ticker.upper())
            except:
                print("Invalid Ticker:", ticker)

        return validTickers

    def save_tickers(self):
        """Save a specified quantity of tickers to an output file.

        :Details: Saves a maximum number of tickers to an output file, suchthat each line in the output file is a ticker string.
        """
        # Initialize
        validTickers = set()
        currentURL = self.__NASDAQ_URL

        while len(validTickers) < self.maximum:
            # Collect Tickers
            validTickers.update(self.get_tickers_from_url(currentURL,len(validTickers)))

            # Collect New Page URL
            response = requests.get(currentURL)
            currentURL = re.findall(self.__PATTERN_NEXT_PAGE,response.text)[0]

            # Print Valid Ticker Set to Output File
            self.print_to_file(self.__OUTFILE, validTickers)

            # Announce Page Change
            if len(validTickers) < self.maximum:
                print("Moving to Next Page", currentURL, "Valid Ticker(s) Found:", len(validTickers),)

class Fetcher:
    """Class used to periodically fetch stock information from a list of known tickers.

    :var str tickerFile: File path to read tickers from. - Default: *tickers.txt*
    :var str outfile: Output database file.
    """

    # Ticker Settings
    def __init__(self, outfile="stocks_new.db"):
        # Do something
        self.tickerFile ="tickers.txt"
        self.outfile = outfile

    def getTickers(self):
        """Retrieve a set of tickers from a text file.

        :Details: Retrieves a set of tickers from the tickerFile which is a text file such that each line of the text file is a new ticker represented as a string.
        :return: Valid tickers.
        :rtype: set
        """
        tickers = set()

        try:
            f = open(self.tickerFile, "r")
            for line in f:
                tickers.add(line[:-1])
            f.close()
        except:
            print("Error While Accessing the Ticker File.")
            return

        return tickers

    def makeTimeString(self, hour, minute):
        """Makes a time string (HH:MM) from hour and minute.

        :param int hour: The hour of the time.
        :param int minute: The minute of the time.
        :return: Time in the form HH:MM, substituting 0 as needed.
        :rtype: str
        """

        timeString = str()
        hourString = str()
        minuteString = str()

        if hour < 10:
            hourString = "0" + str(hour)
        else:
            hourString = str(hour)

        if minute < 10:
            minuteString = "0" + str(minute)
        else:
            minuteString = str(minute)
        
        timeString = hourString + ":" + minuteString

        return timeString

    def fetch(self, timeLimit):
        """Fetch tickers from the tickerFile every minute for a set period of time.

        :param int timeLimit: The set period of time to fetch tickers for (in seconds).
        """
        # Collect Stock Tickers
        tickerSet = self.getTickers()

        # Setup for Print File
        dbConnection = sqlite3.connect(self.outfile)
        dbCursor = dbConnection.cursor()
        dbCursor.execute('''CREATE TABLE IF NOT EXISTS stocks
            (Time text, Ticker text, latestPrice real, latestVolume long, Close real, Open real, low real, high real)''')

        # Timed Execution
        endTime = time.time() + timeLimit
        currentMinute = datetime.datetime.now().minute
        firstPass = True
        while time.time() < endTime:
            if firstPass or (datetime.datetime.now().minute != currentMinute):
                # 
                if firstPass:
                    print("Retrieving Stock Data")
                    firstPass = False
                else:
                    print("Updating Stock Data at", datetime.datetime.now().time())

                # Execute Update Here
                for ticker in tickerSet:
                    tickInfo = Stock(ticker).quote()
                    tickStr = "\'" + str(self.makeTimeString(datetime.datetime.now().hour, datetime.datetime.now().minute) + "\'" + "," + "\'" + ticker + "\'" + "," + str(tickInfo["latestPrice"]) + ",")
                    tickStr = tickStr + str(tickInfo["latestVolume"]) + "," + str(tickInfo["close"]) + "," + str(tickInfo["open"]) + ","
                    tickStr = tickStr + str(tickInfo["low"]) + "," + str(tickInfo["high"]) + "\n"
                    dbCursor.execute("INSERT INTO stocks VALUES(" + tickStr + ")")
                currentMinute = datetime.datetime.now().minute
                dbConnection.commit()
        print("Time Limit Has Expired at", datetime.datetime.now().time())
        dbConnection.close()
