import os
import _data as data
import jobs
from _state_manager import State


def screen_company(state, ticker):
    if not data.adequate_size(ticker):
        return False
        
    if not data.strong_financial_condition(ticker):
        return False
    
    jobs.update_earnings_data(state, ticker)

    if not data.earnings_stability(ticker):
        return False

count = 0
total = 0
with State() as state:
    for ticker in next(os.walk(os.path.join(data.get_script_dir(), "data/companies")))[1]:
        total = total + 1
        
        if screen_company(state, ticker):
            print(ticker)
            count = count + 1
            break

print(str(count) + " / " + str(total))
