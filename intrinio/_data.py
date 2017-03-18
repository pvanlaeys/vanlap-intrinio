import os
import json
import datetime


def get_script_dir():
    return os.path.dirname(__file__)


def get_company_path(ticker):
    return os.path.join(get_script_dir(), "data/companies/" + ticker)


def get_company_list():
    with open(os.path.join(get_script_dir(), "data/company_list.txt")) as f:
        tickers = f.read().splitlines()
    if len(tickers) <= 1:
        raise Exception("company list is not populated")
    return tickers


def get_data_value(ticker, statement, tag):    
    with open(os.path.join(get_script_dir(), "data/companies", ticker, statement + ".txt")) as f:
        data = json.load(f)["data"]
    for data_point in data:                
        if data_point["tag"] == tag:
            value = data_point["value"]            
            if isinstance(value, float):
                return value 
            return 0
    return 0


def get_market_cap(ticker):
    return get_data_value(ticker, "calculations", "marketcap")


def get_current_assets(ticker):
    return get_data_value(ticker, "balance_sheet", "totalcurrentassets")


def get_current_liabilities(ticker):
    return get_data_value(ticker, "balance_sheet", "totalcurrentliabilities")


def get_longterm_debt(ticker):
    return get_data_value(ticker, "balance_sheet", "longtermdebt")


def get_working_capital(ticker):    
    return (get_current_assets(ticker) - get_current_liabilities(ticker))


def get_earnings_per_share(ticker, year):
    return get_data_value(ticker, "income_statements/" + str(year), "basiceps")


def adequate_size(ticker):
    # total market value >= $2 billion
    return (get_market_cap(ticker) > 2000000000)


def strong_financial_condition(ticker):
    # Current assets >= 2*Current liabilities &&
    # long-term debt <= net current assets (i.e.  working capital)
    current_assets = get_current_assets(ticker)    
    current_liabilities = get_current_liabilities(ticker)
    if current_assets < (current_liabilities * 2):            
        return False

    return get_longterm_debt(ticker) <= get_working_capital(ticker)    


def earnings_stability(ticker):
    # EPS > 0 for the last 10 Years on the basis that companies that have maintained at least some level of earnings are more likely to be stable going forward.
    current_year = datetime.date.today().year
    for year in range(current_year-1, current_year-11, -1):        

        if not is_income_statement_loaded(ticker, year):
            raise Exception("missing earnings data for " + ticker)

        if get_earnings_per_share(ticker, year) <= 0:            
            return False
        
    return True


def dividend_record(ticker):
    # uninterrupted payments for >= past 20 years
    return


def earnings_growth(ticker):
    # >= 1/3 increase in EPS in the past 10 years using 3-year
    # averages at the beginning and end
    # i.e.  Take average of EPS over first 3 years (10th,9th,and 8th
    # year ago) and ensure average
    # EPS over last 3 years was 33% or more higher
    # Revised:
    #	33% -> 50%
    return


def moderate_price_to_earnings(ticker):
    # Current price <= 15*average earnings (EPS) of past 3 years
    # 
    return


def moderate_price_to_assets(ticker):
    # Current price <= 1.5*last reported book value

    # "The Multiplier"*ratio of price to book value <=22.5

    # i.e.

    # price to assets (a.k.a price-to-book-value ratio) <=1.5

    # P/E * price-to-book ratio

    # Revised:
    #	Maybe 1.5 -> 2.5?
    return


def institutional_holdings(ticker):
    # <=60% of shares are owned by institutions
    return


def get_income_path(ticker):
    return os.path.join(get_company_path(ticker), "income_statements")

def get_income_statement_path(ticker, year):        
    return os.path.join(get_income_path(ticker), str(year) + ".txt")


def is_income_statement_loaded(ticker, year):    
    return os.path.exists(get_income_statement_path(ticker, year))
        

def save_income_statement(ticker, year, data):
    income_path = get_income_path(ticker)
    if not os.path.exists(income_path):
        os.makedirs(income_path)

    with open(get_income_statement_path(ticker, year), "w") as file:
        file.write(data)