from stock import Tickers
import os

def test_ticker_init():
    for val in {0,1,50,110}:
        ticker = Tickers(val)
        assert ticker.maximum == val

def test_save_tickers():
    test_max = 5
    test_outfile = "test_tickers.txt"
    ticker = Tickers(test_max)
    ticker.outfile = test_outfile
    ticker.save_tickers()
    assert len(open(test_outfile).readlines()) <= test_max

def test_save_tickers_long():
    test_max = 100
    test_outfile = "test_tickers_2.txt"
    ticker = Tickers(test_max)
    ticker.outfile = test_outfile
    ticker.save_tickers()
    assert len(open(test_outfile).readlines()) <= test_max

def test_cleanup():
    os.remove("test_tickers.txt")
    os.remove("test_tickers_2.txt")