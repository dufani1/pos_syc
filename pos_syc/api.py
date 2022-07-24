import json
from urllib import response
import frappe
from pos_syc.sync_items import sync_items
from pos_syc.utils import get_syc_settings, update_last_sync_time

import requests

from frappe.frappeclient import FrappeClient

def periodic_sync_hook_5min():
    if frappe.get_single("SYC Settings").periodic_sync == "5":
        # syc_sync_main()
        pass

def periodic_sync_hook_10min():
    if frappe.get_single("SYC Settings").periodic_sync == "10":
        # syc_sync_main()
        pass
        
def periodic_sync_hook_20min():
    if frappe.get_single("SYC Settings").periodic_sync == "20":
        # syc_sync_main()
        pass
        
def periodic_sync_hook_30min():
    if frappe.get_single("SYC Settings").periodic_sync == "30":
        # syc_sync_main()
        pass

def periodic_sync_hook_60min():
    if frappe.get_single("SYC Settings").periodic_sync == "60":
        # syc_sync_main()
        pass

@frappe.whitelist()
def syc_sync_main():
    # frappe.enqueue(_sync_main, queue="long", is_async=True, job_name="SYC Main Sync")
    _sync_main()
    return True

def _sync_main():
    # sart syncing items
    sync_items()



@frappe.whitelist(allow_guest=False, methods=["GET"])
def syc_reset_last_update():
    syc_settings = get_syc_settings()
    syc_settings.last_update = None

    syc_settings.save()
    frappe.db.commit()

    return syc_settings.last_update



