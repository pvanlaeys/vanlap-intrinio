import os
import datetime
import xml.etree.ElementTree as ET

import selection
import _data as data
import _requests as req
from _state_manager import State


def build_company_list(endpoint, params=None):
    if params is None:
        params = {}

    with State() as state:
        file_name = os.path.join(data.get_script_dir(),
                                 "data",
                                 endpoint.split("/")[0] + ".txt")
        with open(file_name, "w") as file:
            r = req.make_intrinio_request(state, endpoint, params)
            company_list = r.json()

            total_pages = int(company_list["total_pages"])
            write_company_list_page(company_list)

            if total_pages > 1:
                for page_number in range(2, total_pages + 1):
                    params["page_number"] = str(page_number)
                    r = req.make_intrinio_request(state, endpoint, params)
                    write_company_list_page(r.json())


def update_fundamentals():
    with State() as state:
        tickers = req.request_screened_tickers(state)
        updated_tickers = req.request_updated_tickers(state)

        with open(os.path.join(data.get_script_dir(),
                               "data", "ticker_list.txt"), "w") as file:
            for ticker in tickers:
                if (not data.has_data(ticker, "balance_sheet") or
                        ticker in updated_tickers):
                    req.request_statement(state, ticker, "balance_sheet")
                file.write(ticker)


def update_next_company_chunk():
    with State() as state:
        ticker_index = state.get_last_ticker_index()
        tickers = data.get_company_list()

        while(state.is_under_request_limit()):
            if (ticker_index + 1) == len(tickers):
                ticker_index = -1

            ticker = tickers[ticker_index + 1]

            if not data.has_data(ticker, "balance_sheet"):
                req.request_statement(state, ticker, "balance_sheet")

            ticker_index = ticker_index + 1

        state.set_last_ticker_index(ticker_index)


def main():
    weekday = datetime.datetime.today().weekday()
    if weekday == 6:  # Sunday
        # The day of rest        
        return

    if weekday == 5:  # Saturday
        update_funamentals()
    else:
        matches = selection.get_selection()


main()
print(selection.get_selection())