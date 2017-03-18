import os
import datetime
from time import sleep
import _data as data


def make_intrinio_request(state, endpoint, params=None):
    sleep(.01)  # Ensure max 100 requests per second
    r = state.session.get(("https://api.intrinio.com/" + endpoint), params=params)
    state.increment_request_count()
    r.raise_for_status()
    return r


def request_company_statement(state, ticker, statement):
    r = make_intrinio_request(state, "financials/standardized", {
        "identifier": ticker,
        "statement": statement,
        "type": "QTR",
        "date": datetime.date.today().strftime("%Y-%m-%d")})
    return r.text


def request_income_statement(state, ticker, year):
    r = make_intrinio_request(state, "financials/standardized", {
            "identifier":ticker,
            "statement":"income_statement",
            "fiscal_period": "FY",
            "fiscal_year": str(year)})
    data.save_income_statement(ticker, year, r.text)


def update_company_data(state, ticker):
    company_path = get_company_path(ticker)
    if not os.path.exists(company_path):
        os.makedirs(company_path)
    
    update_company_statement(state, ticker, "calculations", company_path)

    if data.adequate_size(ticker):
        update_company_statement(state, ticker, "balance_sheet", company_path)    


def update_company_statement(state, ticker, statement, path):
    result = request_company_statement(state, ticker, statement)

    with open(os.path.join(path, statement + ".txt"), "w") as file:
        file.write(result)
