import os
import datetime
import requests
import json
import jobs
import _requests as req
from _state_manager import State

script_dir = os.path.dirname(__file__)


def get_companies():
    with open(os.path.join(script_dir, "data/company_data.txt")) as f:
        companies = json.load(f)
    if len(companies) <= 1:
        raise Exception("companies object is not populated")
    return companies


with State() as s:
    r = req.make_intrinio_request(s, "historical_data", {
        "identifier":"T", 
        "item":"basiceps",
        "start_date":"2007-01-01",        
        "type":"FY"
        })
    print(r.status_code)
    print(r.text)

#jobs.update_next_company_chunk(s)
    