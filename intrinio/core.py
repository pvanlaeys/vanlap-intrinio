import os
import datetime
from dateutil.relativedelta import relativedelta
from math import sqrt
import requests
import json
import _data as data
import _requests as req


def get_ticker_list():
    return data.read_list_from_file("ticker_list.txt")    


def get_current_price(ticker, state=None):    
    if not state is None and not data.has_current_data(ticker, "price"):
        req.request_price(state, ticker)
    return data.get_price(ticker)


def adequate_size(ticker):
    # total market value >= $2 billion
    return (data.get_market_cap(ticker) > 2000000000)


def strong_financial_condition(ticker):
    # Current assets >= 2*Current liabilities &&
    # long-term debt <= net current assets (i.e.  working capital)
    if not data.has_data(ticker, "balance_sheet"):
        return False

    current_assets = data.get_current_assets(ticker)
    current_liabilities = data.get_current_liabilities(ticker)
    
    # Original
    if current_assets < (current_liabilities * 2):
        return False

    # Tweaked
    #if current_assets < (current_liabilities * 1.5):
    #    return False

    return data.get_longterm_debt(ticker) <= data.get_working_capital(ticker)


def verify_earnings_loaded(state, ticker):
    if not state is None and not data.has_data(ticker, "basiceps"):
        req.request_earnings_data(state, ticker)


def earnings_stability(ticker, state=None):
    # EPS > 0 for the last 10 Years on the basis that companies that have
    # maintained at least some level of earnings are more likely to be stable
    # going forward.

    verify_earnings_loaded(state, ticker)
    return data.has_historical_data(ticker, "basiceps", 10)


def dividend_record(ticker, state=None):
    # uninterrupted payments for >= past 20 years

    if not state is None and not data.has_data(ticker, "cashdividendspershare"):
        req.request_dividend_data(state, ticker)

    return data.has_historical_data(ticker, "cashdividendspershare", 20)


def earnings_growth(ticker, state=None):
    # >= 1/3 increase in EPS in the past 10 years using 3-year
    # averages at the beginning and end
    # i.e.  Take average of EPS over first 3 years (10th,9th,and 8th
    # year ago) and ensure average
    # EPS over last 3 years was 33% or more higher
    # Revised:
    #	33% -> 50%

    verify_earnings_loaded(state, ticker)

    start_average = data.get_earnings_average(ticker, True)
    if start_average is None:
        return False

    end_average = data.get_earnings_average(ticker)

    percent_change = ((end_average - start_average) / start_average) * 100

    #return percent_change >= 33

    # Tweaked
    return percent_change >= 50



def moderate_price_to_earnings(ticker, state=None):
    # Current price <= 15*average earnings (EPS) of past 3 years
    current_price = get_current_price(ticker, state)
    if current_price is None: 
        raise Exception("Price is None for " + ticker)               

    verify_earnings_loaded(state, ticker)    
    return current_price <= (15 * data.get_earnings_average(ticker))


def get_modifier(ticker):
    return sqrt(22.5 * data.get_earnings_average(ticker) * data.get_book_value(ticker))


def moderate_price_to_assets(ticker, state=None):
    # Current price <= 1.5*last reported book value

    # "The Multiplier"*ratio of price to book value <=22.5

    # i.e.

    # price to assets (a.k.a price-to-book-value ratio) <=1.5

    # P/E * price-to-book ratio

    # Revised:
    #	Maybe 1.5 -> 2.5?
    if not state is None and not data.has_current_data(ticker, "calculations"):
        req.request_statement(state, ticker, "calculations")

    current_price = get_current_price(ticker, state)    
    if current_price is None:
        return False
        
    if current_price > (2.5 * data.get_book_value(ticker)):
        return False
        
    verify_earnings_loaded(state, ticker)
    if current_price > get_modifier(ticker):
        return False

    #if ((current_price / data.get_earnings_average(ticker)) * 
    #    data.get_price_to_book(ticker)) > 22.5:
    #    return False

    return True


def institutional_holdings(ticker):
    # <=60% of shares are owned by institutions
    return True


def get_value_ratio(ticker):
    return get_modifier(ticker) / get_current_price(ticker)