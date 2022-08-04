import frappe
from frappe.utils.data import nowdate
from pos_syc.requests_api import post_request
from pos_syc.utils import syc_clear_pull_logs, syc_get_settings
from pos_syc.api import syc_pull_backlogs


@frappe.whitelist(allow_guest=False, methods=["POST"])
def prepare():
    try:
        res = post_request(
            method="pos_sym.sym_prepare_pos.prepare",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )
        print(res)
        if res:
            if res.json()["message"]:
                syc_settings = syc_get_settings()
                syc_settings.is_prepared = 1
                syc_settings.save()
                
                # pull backlogs on preparation success
                # syc_pull_backlogs()
                
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")


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
                syc_settings.preparation_date = nowdate()
                syc_settings.save()

                syc_clear_pull_logs()

                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")
