import frappe
import requests
from pos_syc.utils import get_syc_settings 

def get_request(method: str, params=None):
    syc_settings = get_syc_settings()

    response = requests.get(
        url=syc_settings.sym_domain + "/api/method/" + method,
        params=params,
        headers={
            "Authorization": f"token {syc_settings.api_key}:{syc_settings.get_password(fieldname='api_secret')}"
        }
    )

    if response:
        return response
    else:
        return None

def post_request(method: str, data=None):
    syc_settings = get_syc_settings()

    response = requests.post(
        url=syc_settings.sym_domain + "/api/method/" + method,
        data=data,
        headers={
            "Authorization": f"token {syc_settings.api_key}:{syc_settings.get_password(fieldname='api_secret')}"
        }
    )

    if response:
        return response
    else:
        return None