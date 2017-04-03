import os
import datetime
from dateutil.relativedelta import relativedelta
from time import sleep
import _data as data


def make_intrinio_request(state, endpoint, params=None):
    sleep(.01)  # Ensure max 100 requests per second
    r = state.session.get(
        ("https://api.intrinio.com/" + endpoint), params=params)
    state.increment_request_count()
    r.raise_for_status()
    return r


def request_ticker_list(state, endpoint, params=None):
    if params is None:
        params = {}    
    
    ticker_list = []    
    r = make_intrinio_request(state, endpoint, params)
    company_list = r.json()

    total_pages = int(company_list["total_pages"])
    for company in company_list["data"]:
        ticker_list.append(company["ticker"])

    if total_pages > 1:
        for page_number in range(2, total_pages + 1):
            params["page_number"] = str(page_number)
            r = make_intrinio_request(state, endpoint, params)
            for company in r.json()["data"]:
                ticker_list.append(company["ticker"])            
    return ticker_list


def request_screened_tickers(state):
    return request_ticker_list(state, "securities/search", {
        "conditions": "marketcap~gt~2000000000"})


def request_updated_tickers(state):
    start_date = datetime.date.today() - relativedelta(weeks=4)
    return request_ticker_list(state, "companies", {
        "latest_filing_date": start_date.strftime("%Y-%m-%d")})


def request_statement(state, ticker, statement):
    r = make_intrinio_request(state, "financials/standardized", {
        "identifier": ticker,
        "statement": statement,
        "type": "QTR",
        "date": datetime.date.today().strftime("%Y-%m-%d")})
    data.save_data(ticker, statement, r.text)
    return r.text


def request_income_statement(state, ticker, year):
    r = make_intrinio_request(state, "financials/standardized", {
        "identifier": ticker,
        "statement": "income_statement",
        "fiscal_period": "FY",
        "fiscal_year": str(year)})
    data.save_income_statement(ticker, year, r.text)


def request_historical_data(state, ticker, item, years):
    start_date = datetime.date.today() - relativedelta(years=(years + 1))    
    r = make_intrinio_request(state, "historical_data", {
        "identifier": ticker,
        "item": item,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "type": "FY"
    })
    data.save_data(ticker, item, r.text)


def request_earnings_data(state, ticker):
    request_historical_data(state, ticker, "basiceps", 10)


def request_dividend_data(state, ticker):
    request_historical_data(state, ticker, "cashdividendspershare", 20)


def request_price(state, ticker):    
    r = make_intrinio_request(state, "data_point", {
            "ticker": ticker,
            "item": "last_price"
            })
    data.save_data(ticker, "price", r.text)