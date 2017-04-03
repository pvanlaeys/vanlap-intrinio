import core
from _state_manager import State


def screen_company(state, ticker):

    if not core.strong_financial_condition(ticker):
        return False
    
    if not core.earnings_stability(ticker, state):
        return False
    
    # if not core.dividend_record(ticker, state):
    #     return False
    
    if not core.earnings_growth(ticker):
        return False
    
    if not core.moderate_price_to_earnings(ticker, state):
        return False
    
    if not core.moderate_price_to_assets(ticker, state):
        return False
    
    return True


def get_selection():
    results = []
    with State() as state:
        for ticker in core.get_ticker_list():                        
            if screen_company(state, ticker):
                results.append(ticker)

            if not state.is_under_request_limit():
                break
    return results



# ToDo:
# - use last price instead of close price
# - use updated calculation to check marketcap (in case existing company falls below threshold)
# - Update basiceps if latest data point is more than a year old