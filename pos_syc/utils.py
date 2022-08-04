import frappe
from frappe.utils.data import nowdate

def syc_get_settings():
    return  frappe.get_single("SYC Settings")

def syc_get_pull_logs():
    pull_logs = frappe.get_all(
        "SYC Pull Log",
        fields="*",
        filters={},
        order_by="modified asc"
    )

    return pull_logs

def syc_create_pull_log(backlog_name, event_type, status, doctype=None, docname=None, data=None):
    try:
        new_backlog = frappe.get_doc(
            {
                "doctype": "SYC Pull Log",
                "sym_backlog_name": backlog_name,
                "event": event_type,
                "status": status,
                "ref_doctype": doctype,
                "ref_docname": docname,
                "data": data,
                "date": nowdate()
            }
        )

        new_backlog.insert()
    except Exception as e:
        print("SYC Error", e)


def syc_clear_pull_logs():

    # TODO: delete records using sql
    _entries = frappe.get_all(
        "SYC Pull Log",
        fields=["name"]
    )
    # for entry in _entries:
    frappe.db.delete("SYC Pull Log")