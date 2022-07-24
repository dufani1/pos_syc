import frappe

def get_syc_settings():
    return  frappe.get_single("SYC Settings")


def update_last_sync_time():
    syc_settings = get_syc_settings()
    syc_settings.last_update = frappe.utils.now()

    syc_settings.save()


def create_sync_log(status, data=None):
    tb = frappe.get_traceback()
    new_doc = frappe.get_doc(
        {
            "doctype": "SYC Sync Logs",
            "status": status,
            "data": data or tb
        }
    )
    new_doc.insert()
    print(tb)
