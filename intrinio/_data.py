import os
import json
import datetime


def get_script_dir():
    return os.path.dirname(__file__)


def get_company_path(ticker):
    return os.path.join(get_script_dir(), "data/companies/" + ticker)


def get_company_list():
    with open(os.path.join(get_script_dir(), "data/securities.txt")) as f:
        tickers = f.read().splitlines()
    if len(tickers) <= 1:
        raise Exception("company list is not populated")
    return tickers


def get_data_path(ticker, type):
    return os.path.join(
        get_script_dir(), "data/companies", ticker, type + ".txt")


def has_data(ticker, type):
    file_path = get_data_path(ticker, type)
    return os.path.exists(file_path)


def has_current_data(ticker, type):
    file_path = get_data_path(ticker, type)
    if not os.path.exists(file_path):
        return False

    file_instant = os.path.getmtime(file_path)
    return (datetime.datetime.fromtimestamp(file_instant).date() ==
            datetime.date.today())


def get_file_object(ticker, type):
    file_path = get_data_path(ticker, type)

    if not os.path.exists(file_path):
        raise Exception("Missing " + type + " data for " + ticker)

    with open(file_path) as f:
        return json.load(f)


def get_data(ticker, type):
    return get_file_object(ticker, type)["data"]


def get_data_value(ticker, statement, tag):
    data = get_data(ticker, statement)
    for data_point in data:
        if data_point["tag"] == tag:
            value = data_point["value"]
            if isinstance(value, float):
                return value
            return 0
    return 0


def get_price(ticker):
    return get_file_object(ticker, "price")["value"]
    

def get_market_cap(ticker):
    return get_data_value(ticker, "calculations", "marketcap")


def get_book_value(ticker):
    return get_data_value(ticker, "calculations", "bookvaluepershare")


def get_price_to_book(ticker):
    return get_data_value(ticker, "calculations", "pricetobook")


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


def save_data(ticker, item, data):
    company_path = get_company_path(ticker)
    if not os.path.exists(company_path):
        os.makedirs(company_path)
    with open(os.path.join(company_path, item + ".txt"), "w") as file:
        file.write(data)


def has_historical_data(ticker, type, years):
    year_count = 0
    data = get_data(ticker, type)
    for year in reversed(data):
        if float(year["value"]) <= 0:
            return False
        year_count = year_count + 1
        if year_count == years:
            break
    return (year_count > (2 * years/3))


def get_earnings_average(ticker, is_start_average=False):
    years_data = get_data(ticker, "basiceps")
    if len(years_data) < 3:
        return 0

    total_eps = 0
    years_list = years_data[-3:] if is_start_average else years_data[:3]

    for year in years_list:
        eps = year["value"]
        if not isinstance(eps, float):
            return None
        total_eps = total_eps + eps
    return total_eps / 3


def read_list_from_file(child_path):
    with open(os.path.join(get_script_dir(), "data", child_path)) as f:        
        content = f.readlines()    
    return [x.strip() for x in content]


def write_list_to_file(child_path, selection):    
    with open(os.path.join(get_script_dir(), "data", child_path), 'w') as file:
        for ticker in selection:
            file.write(ticker + "\n")