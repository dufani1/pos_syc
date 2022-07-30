import json
import frappe
import requests
from pos_syc.utils import create_sync_log, syc_get_settings 

def get_request(method: str, params=None):
    syc_settings = syc_get_settings()

    try:
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
            log_data = f"""
                url: {response.url}
                method: {response.request.method}
                status: {response.status_code}
                content: {response.content}
                reason: {response.reason}
                text: {response.text}
            """
            print(log_data)
            create_sync_log("Request Error", data = log_data)

            return None
    except Exception as e:
        print(e)
        create_sync_log("Error", data = frappe.get_traceback())
def post_request(method: str, data=None):
    syc_settings = syc_get_settings()

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
        log_data = f"""
            url: {response.url}
            method: {response.request.method}
            status: {response.status_code}
            content: {response.content}
            reason: {response.reason}
            text: {response.text}
        """
        print(log_data)
        create_sync_log("Request Error", data = log_data)
        return None