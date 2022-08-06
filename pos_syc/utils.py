import frappe
from frappe.utils.data import nowdate

def syc_get_settings():
    return  frappe.get_single("SYC Settings")

def syc_get_backlogs():
    # we send only Pending backlogs
    backlogs = []
    _backlogs = frappe.get_all(
        "SYC Backlog",
        fields="*",
        order_by="modified asc"
    )

    for bl in _backlogs:
        if bl.status == "Success":
            continue
        if bl.status == "Failed":
            break
        
        backlogs.append(
            bl
        )
    return backlogs

def syc_create_backlog(doctype, docname, data, event_type, status="Pending"):
    new_backlog = frappe.get_doc(
        {
            "doctype": "SYC Backlog",
            "ref_doctype": doctype,
            "ref_docname": docname,
            "data": data,
            "event": event_type,
            "status": status,
            "create": nowdate()
        }
    )

    new_backlog.insert()

def syc_clear_backlogs():

    # TODO: delete records using sql
    _entries = frappe.get_all(
        "SYC Backlog",
        fields=["name"]
    )
    for entry in _entries:
        frappe.db.delete(
            "SYC Backlog",
            filters={
                "name": entry.name
            }
        )

def syc_clear_pull_logs():

    # TODO: delete records using sql
    _entries = frappe.get_all(
        "SYC Pull Log",
        fields=["name"]
    )
    for entry in _entries:
        frappe.db.delete(
            "SYC Pull Log",
            filters={
                "name": entry.name
            }
        )

def syc_get_pull_logs():
    pull_logs = frappe.get_all(
        "SYC Pull Log",
        fields="*",
        filters={},
        order_by="modified asc"
    )

    return pull_logs

def syc_create_pull_log(sym_backlog_name, event_type, status, doctype=None, docname=None, data=None):
    try:
        pull_log_exist = frappe.get_all(
            "SYC Pull Log",
            filters={
                "sym_backlog_name": sym_backlog_name
            }
        )
        if len(pull_log_exist) == 0:
            new_backlog = frappe.get_doc(
                {
                    "doctype": "SYC Pull Log",
                    "sym_backlog_name": sym_backlog_name,
                    "event": event_type,
                    "status": status,
                    "ref_doctype": doctype,
                    "ref_docname": docname,
                    "data": data,
                    "create": nowdate()
                }
            )

            new_backlog.insert()
    except Exception as e:
        print("SYC Error", frappe.get_traceback())

