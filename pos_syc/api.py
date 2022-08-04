import json
import frappe
from pos_syc.requests_api import post_request
from pos_syc.utils import syc_clear_pull_logs, syc_create_pull_log, syc_get_pull_logs, syc_get_settings

def periodic_sync_hook_5min():
    if frappe.get_single("SYC Settings").periodic_sync == "5":
        syc_pull_backlogs()

def periodic_sync_hook_10min():
    if frappe.get_single("SYC Settings").periodic_sync == "10":
        syc_pull_backlogs()
        
def periodic_sync_hook_20min():
    if frappe.get_single("SYC Settings").periodic_sync == "20":
        syc_pull_backlogs()
        
def periodic_sync_hook_30min():
    if frappe.get_single("SYC Settings").periodic_sync == "30":
        syc_pull_backlogs()

def periodic_sync_hook_60min():
    if frappe.get_single("SYC Settings").periodic_sync == "60":
        syc_pull_backlogs()


@frappe.whitelist(allow_guest=False, methods=["POST"])
def _syc_pull_backlogs():
    syc_pull_backlogs()


def syc_pull_backlogs():
    try:
        # first send success confirmation
        syc_confirm_pull_logs()

        # pull sym backlogs
        res = post_request(
            method="pos_sym.api.pull_backlogs",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )
        if res:

            backlogs = res.json()["message"]
            if backlogs:

                # remove local pull logs
                # syc_clear_pull_logs()

                # insert received backlogs
                for bl in backlogs:
                    syc_create_pull_log(
                        backlog_name=bl.get("name"),
                        event_type=bl.get("event"),
                        status=bl.get("status"),
                        doctype=bl.get("ref_doctype"),
                        docname=bl.get("ref_docname"),
                        data=bl.get("data")
                    )
                
                # evaluate pull logs
                # syc_eval_pull_logs()

                return True
            else:
                return False
        else:
            return False

    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")

@frappe.whitelist(allow_guest=False, methods=["POST"])
def syc_eval_pull_logs():
    pull_logs = frappe.get_all(
        "SYC Pull Log",
        fields="*",
        order_by="modified asc",
        limit_page_length=10

    )

    for plog in pull_logs:
        print(f"Event: {plog.event} Status: {plog.status} Name: {plog.name}")
        if plog.status == "Success": 
            print(f"Skiping: {plog.name}")
            continue

        if plog.status == "Failed":
            print(f"Breaking due to: {plog.name}")
            break

        if plog.event == "Init" or plog.event == "Insert":
            try:
                
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype
                
                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname)

                new_insert = frappe.get_doc(parsed_log_data) 
                new_insert.insert()
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)

                
            except Exception as e:
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Failed", update_modified=False)
                print(e)
        elif plog.event == "Update":
            try:
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype
                
                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname)

                new_insert = frappe.get_doc(parsed_log_data) 
                new_insert.insert()
                
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)

                
            except Exception as e:
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Failed", update_modified=False)
                print(e)

        # send confirmation when sync finish
        syc_confirm_pull_logs()
        
def syc_confirm_pull_logs():
    try:
        success_pull_logs = frappe.get_all(
            "SYC Pull Log",
            fields=["sym_backlog_name"],
            order_by="modified asc"
        )
        res = post_request(
            method="pos_sym.api.sym_confirm_backlogs",
            data={
                "client_id": syc_get_settings().get("client_id"),
                "success_pull_logs": frappe.as_json(success_pull_logs)
            }
        )
        if res:
            print(res)
    except Exception as e:
        print(frappe.get_traceback())
# def syc_confirm_backlogs(sym_backlog_name):
#     try:
#         res = post_request(
#             method="pos_sym.api.sym_confirm_backlog",
#             data={
#                 "client_id": syc_get_settings().get("client_id"),
#                 "backlog_name": sym_backlog_name
#             }
#         )
#     except Exception as e:
#         print(e)
# @frappe.whitelist(allow_guest=False, methods=["GET"])
# def syc_reset_last_update():
#     syc_settings = get_syc_settings()
#     syc_settings.last_update = None

#     syc_settings.save()
#     frappe.db.commit()

#     return syc_settings.last_update



