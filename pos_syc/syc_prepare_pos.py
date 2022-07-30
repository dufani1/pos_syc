import frappe
from frappe.utils import data
from pos_syc.requests_api import get_request, post_request
from pos_syc.utils import create_sync_log, syc_get_settings

@frappe.whitelist(allow_guest=False, methods=["POST"])
def prepare():
    try:
        res = post_request(
            method="pos_sym.sym_prepare_pos.prepare",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )

        if res:
            if res.json()["message"]:
                syc_settings = syc_get_settings()
                syc_settings.is_prepared = 1
                syc_settings.save()

                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        create_sync_log(status="Error", data=frappe.get_traceback())

@frappe.whitelist(allow_guest=False, methods=["POST"])
def revoke():
    try:
        res = post_request(
            method="pos_sym.sym_prepare_pos.revoke",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )

        if res:
            if res.json()["message"]:
                syc_settings = syc_get_settings()
                syc_settings.is_prepared = 0
                syc_settings.save()

                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        create_sync_log(status="Error", data=frappe.get_traceback())