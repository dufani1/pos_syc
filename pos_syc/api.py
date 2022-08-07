import json
import importlib
import frappe
import pos_syc.syc_controllers as syc_controllers
from frappe.utils.data import nowdate
from pos_syc.requests_api import post_request
from pos_syc.utils import syc_clear_backlogs, syc_clear_pull_logs, syc_create_pull_log, syc_get_backlogs, syc_get_pull_logs, syc_get_settings

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
def enqueue_sync_job():
    frappe.enqueue(method=_syc_push_backlogs, enqueue="long", job_name="SYC Sync Main")
    # _syc_push_backlogs()
    return True

@frappe.whitelist(allow_guest=False, methods=["POST"])
def _syc_pull_backlogs():
    syc_pull_backlogs()


def syc_pull_backlogs():
    try:
        # first send success confirmation
        syc_confirm_pull_logs()

        # pull sym backlogs
        res = post_request(
            method="pos_sym.api.send_backlogs",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )

        if res:

            backlogs = res.json()["message"]

            if backlogs:
                # syc_clear_pull_logs()
                # insert received backlogs
                for bl in backlogs:
                    syc_create_pull_log(
                        sym_backlog_name=bl.get("name"),
                        event_type=bl.get("event"),
                        status=bl.get("status"),
                        doctype=bl.get("ref_doctype"),
                        docname=bl.get("ref_docname"),
                        data=bl.get("data")
                    )
                
                # evaluate pull logs
                syc_eval_pull_logs()

                return True
            else:
                return False
        else:
            return False

    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")


@frappe.whitelist(allow_guest=False, methods=["POST"])
def _syc_push_backlogs():
    syc_push_backlogs()


def syc_push_backlogs():
    try:
        # push syc backlogs
        syc_backlogs = syc_get_backlogs()

        res = post_request(
            method="pos_sym.api.receive_backlogs",
            data={
                "client_id": syc_get_settings().get("client_id"),
                "backlogs": frappe.as_json(syc_backlogs)
            }
        )

        if res:
            # pull sym backlogs and evaluate them
            syc_pull_backlogs()

            success_pull_logs = res.json()["message"]
            # receive success sym pull logs and confirm them on syc backlogs
            if success_pull_logs:
                syc_confirm_backlogs(success_pull_logs)
    


    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")

@frappe.whitelist(allow_guest=False, methods=["POST"])
def syc_eval_pull_logs():
    syc_settings = syc_get_settings()
    
    pull_logs = syc_get_pull_logs()

    for plog in pull_logs:
        if plog.status == "Success": 
            continue
        if plog.event == "Init" or plog.event == "Insert":
            try:
                # if plog.ref_docname == "tax 1 template - ET":
                #     frappe.throw("Doctype XYZ is required")
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype

                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname, force=True)

                new_insert = frappe.get_doc(parsed_log_data) 
                new_insert.insert(ignore_links=(not syc_settings.debug_mode), ignore_mandatory=(not syc_settings.debug_mode))
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)
                
                
            except Exception as e:
                frappe.db.set_value(
                    "SYC Pull Log",
                    dn=plog.name,
                    field={
                        "status": "Failed",
                        "fail_reason": frappe.get_traceback()
                    },
                update_modified=False
                )
                frappe.msgprint(f"SYC: Failed to Eval Pull Log: {plog.name}")
                break

        elif plog.event == "Update":
            try:
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype
                print("Update for: ", plog.name)
                
                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname, force=True)

                new_insert = frappe.get_doc(parsed_log_data)
                new_insert.insert(ignore_links=(not syc_settings.debug_mode), ignore_mandatory=(not syc_settings.debug_mode))
                
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)

                
            except Exception as e:
                frappe.db.set_value(
                    "SYC Pull Log",
                    dn=plog.name,
                    field={
                        "status": "Failed",
                        "fail_reason": frappe.get_traceback()
                    },
                update_modified=False
                )
                frappe.msgprint(f"SYC: Failed to Eval Pull Log: {plog.name}")
                break
        elif plog.event == "Delete":
            try:
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype
                
                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname, force=(not syc_settings.debug_mode))
                
                frappe.db.set_value("SYC Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)

                
            except Exception as e:
                frappe.db.set_value(
                    "SYC Pull Log",
                    dn=plog.name,
                    field={
                        "status": "Failed",
                        "fail_reason": frappe.get_traceback()
                    },
                update_modified=False
                )
                frappe.msgprint(f"SYC: Failed to Eval Pull Log: {plog.name}")
                break
        # send confirmation when sync finish
        syc_confirm_pull_logs()

# dev api for testing
@frappe.whitelist(allow_guest=False, methods=["POST"])
def syc_prepare():
    try:
        # prepare syc backlogs
        syc_clear_backlogs()

        for idx, syc_ctl in enumerate(syc_controllers.__all__):
            module_spec = importlib.util.spec_from_file_location(syc_ctl[idx], syc_controllers.modules[idx])
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module) 
            module.prepare()

    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")

@frappe.whitelist(allow_guest=False, methods=["POST"])
def prepare():
    try:
        # prepare syc first
        syc_prepare()

        res = post_request(
            method="pos_sym.api.prepare",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )

        if res:
            if res.json()["message"]:
                syc_settings = syc_get_settings()
                syc_settings.is_prepared = 1
                syc_settings.preparation_date = nowdate()
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
            method="pos_sym.api.revoke",
            data={
                "client_id": syc_get_settings().get("client_id")
            }
        )

        if res:
            if res.json()["message"]:
                syc_settings = syc_get_settings()
                syc_settings.is_prepared = 0
                syc_settings.preparation_date = None
                syc_settings.save()

                # clear all logs
                syc_clear_backlogs()
                syc_clear_pull_logs()

                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        frappe.log_error(frappe.get_traceback(), title="SYC Error")

def syc_confirm_pull_logs():
    try:
        success_pull_logs = frappe.get_all(
            "SYC Pull Log",
            fields=["sym_backlog_name"],
            filters={"status": "Success"},
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

def syc_confirm_backlogs(pull_log_names):
    try:
        for plog_name in pull_log_names:
            frappe.db.set_value("SYC Backlog", dn=plog_name, field="status", val="Success", update_modified=False)

    except Exception as e:
        print(frappe.get_traceback())

# notify all controllers of doc events
def syc_doc_event(doc, event):
    for idx, syc_ctl in enumerate(syc_controllers.__all__):
        module_spec = importlib.util.spec_from_file_location(syc_ctl[idx], syc_controllers.modules[idx])
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module) 
        # call each controller doc_event method
        module.doc_event(doc, event)