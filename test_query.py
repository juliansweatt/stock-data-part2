from stock import Query

def test_query_init():
    testTime = "10:55"
    testDB = "test.db"
    testTicker = "AAPL"
    testQuery = Query(testTime, testDB, testTicker)
    assert testQuery.time == testTime

def test_query_fetch():
    testTime = "16:32"
    testDB = "stocks.db"
    testTicker = "YI"
    testQuery = Query(testTime, testDB, testTicker)
    fetch_result = testQuery.fetch()
    assert fetch_result[0][0] == testTime

def test_query_fetch_print_invalid():
    testTime = "01:01"
    testDB = "stocks.db"
    testTicker = "JULIAN"
    testQuery = Query(testTime, testDB, testTicker)
    testQuery.fetch_and_print()

def test_cov_query_fetch_print():
    testTime = "16:32"
    testDB = "stocks.db"
    testTicker = "YI"
    testQuery = Query(testTime, testDB, testTicker)
    testQuery.fetch_and_print()