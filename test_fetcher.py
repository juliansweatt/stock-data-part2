from stock import Fetcher

def test_fetcher_init():
    testName = "file.db"
    ticker = Fetcher(testName)
    assert ticker.outfile == testName

def test_fetcher_makeTimeString_minor():
    time_string = Fetcher().makeTimeString(2,1)
    assert time_string == "02:01"

def test_fetcher_makeTimeString_major():
    time_string = Fetcher().makeTimeString(22,55)
    assert time_string == "22:55"

def test_fetcher_fetch_all_data():
    testName = "test.db"
    Fetcher(testName).fetch_all_data(10)