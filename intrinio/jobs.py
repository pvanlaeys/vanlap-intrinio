import os
import datetime
import xml.etree.ElementTree as ET

import _data as data
import _requests as req
from _state_manager import State


def write_company_list_page(file, company_list_page):
    for company in company_list_page["data"]:
        file.write(company["ticker"])
        file.write("\n")


def build_company_list(session):
    with open(os.path.join(script_dir, "data/company_list.txt"), "w") as file:
        r = req.make_intrinio_request(session, "companies")
        company_list = r.json()

        total_pages = int(company_list["total_pages"])
        write_company_list_page(file, company_list)

        if total_pages > 1:
            for page_number in range(2, total_pages + 1):
                r = req.make_intrinio_request(session, "companies", {
                    "page_number": str(page_number)})
                write_company_list_page(file, r.json())


def update_next_company_chunk():
    with State() as state:
        ticker_index = state.get_last_ticker_index()
        tickers = data.get_company_list()
        
        while(state.is_under_request_limit()):
            if (ticker_index + 1) == len(tickers):
                ticker_index = -1

            req.update_company_data(state, tickers[ticker_index + 1])
            ticker_index = ticker_index + 1        

        state.set_last_ticker_index(ticker_index)
    

def update_earnings_data(state, ticker):        
    current_year = datetime.date.today().year
    for year in range(current_year-1, current_year-11, -1):        

        if data.is_income_statement_loaded(ticker, year):
            continue

        req.request_income_statement(state, ticker, year)


