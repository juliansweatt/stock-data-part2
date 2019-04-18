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

    def __init__(self, outfile="stocks_new.db"):
        """Construct a fetcher object.

        :param str outfile: The name/path of the database file to save fetch information to.
        """
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

    def fetch_all_data(self, timeLimit):
        """Fetch tickers from the tickerFile every minute for a set period of time.

        :param int timeLimit: The set period of time to fetch tickers for (in seconds).
        """
        # Collect Stock Tickers
        tickerSet = self.getTickers()

        # Setup for Print File
        dbConnection = sqlite3.connect(self.outfile)
        dbCursor = dbConnection.cursor()
        dbCursor.execute('''CREATE TABLE IF NOT EXISTS stocks
            (Time text, Ticker text, Low real, High real, Open real, Close real, Volume long, Price real)''')

        # Timed Execution
        endTime = time.time() + timeLimit
        currentMinute = datetime.datetime.now().minute
        firstPass = True
        insert_sql = ''' INSERT INTO stocks(Time, Ticker, Low, High, Open, Close, Volume, Price)
                            VALUES(?,?,?,?,?,?,?,?) '''
        while time.time() < endTime:
            if firstPass or (datetime.datetime.now().minute != currentMinute):
                if firstPass:
                    print("Retrieving Stock Data")
                    firstPass = False
                else:
                    print("Updating Stock Data at", datetime.datetime.now().time())
                # Execute Update
                for ticker in tickerSet:
                    tickInfo = Stock(ticker).quote()
                    inject_load = (self.makeTimeString(datetime.datetime.now().hour, datetime.datetime.now().minute),ticker,tickInfo["low"],tickInfo["high"],tickInfo["open"],tickInfo["close"],tickInfo["latestVolume"],tickInfo["latestPrice"])
                    dbCursor.execute(insert_sql, inject_load)
                currentMinute = datetime.datetime.now().minute
                dbConnection.commit()
        print("Time Limit Has Expired at", datetime.datetime.now().time())
        dbConnection.close()

class Query:
    """Class used to query a database of stock information.
    """
    def __init__(self, time, db, ticker):
        """Construct a query object.

        :param str time: The time to query in HH:MM format.
        :param str db: The name/path of the database file being queried.
        :param str ticker: The ticker (uppercase) to query.
        """
        self.time = time
        self.db = db
        self.ticker = ticker

    def fetch(self):
        """Fetch the query target.

        :return: Fetched database row
        :rtype: array
        """
        dbConnection = sqlite3.connect(self.db)
        dbCursor = dbConnection.cursor()
        dbCursor.execute("SELECT * FROM stocks WHERE Ticker=\'"+ self.ticker +"\' AND Time=\'" + self.time + "\'")
        fetch_result = dbCursor.fetchall()
        dbConnection.close()
        return fetch_result
    
    def fetch_and_print(self):
        """Print the result of a fetch, if any.
        """
        fetch_result = self.fetch()
        if fetch_result:
            fetch_result = fetch_result[0]
            print("Time:",fetch_result[0])
            print("Ticker:",fetch_result[1])
            print("Latest Price:",fetch_result[2])
            print("Latest Volume:",fetch_result[3])
            print("Close:",fetch_result[4])
            print("Open:",fetch_result[5])
            print("Low:",fetch_result[6])
            print("High:",fetch_result[7])
        else:
            print("No Query Results Found.")