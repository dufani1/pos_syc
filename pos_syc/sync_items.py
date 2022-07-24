import frappe
from pos_syc.requests_api import get_request
from pos_syc.utils import get_syc_settings, create_sync_log, update_last_sync_time


def sync_items():
    last_update = get_syc_settings().last_update

    try:
        res = get_request(
                method="pos_sym.api.get_items_for_sync",
                params={"last_update": last_update}
            )

        if res:
            docs_list = res.json()["message"]

            for doc in docs_list:
                # create items
                create_item(doc)

                # update last sync time if finish without problems
                update_last_sync_time()
    except Exception as e:
        print(e)
        create_sync_log(status="Error", data=frappe.get_traceback())



def create_item(item_dict):

    if not is_item_exist(item_dict):
        try:
            item_dict["doctype"] = "Item"
            new_item = frappe.get_doc(item_dict)
            new_item.flags.ignore_mandatory = True
            new_item.insert()
          
            log_data = f"""
                Doctype: Item
                DocName: {item_dict["name"]}
            """
            
            create_sync_log("Create", data=log_data)
            print("post")
        except Exception as e:
            create_sync_log("Error")

    else:
        try:
            del item_dict["item_code"]
            del item_dict["item_name"]
            if "attributes" in item_dict:
                del item_dict["attributes"]
            frappe.db.set_value(
                "Item",
                item_dict["name"],
                item_dict,
                update_modified=True)

            log_data = f"""
                Doctype: Item
                DocName: {item_dict["name"]}
            """
            create_sync_log("Update", data=log_data)
        except Exception as e:
            create_sync_log("Error")


def is_item_exist(item_dict):
    return frappe.db.exists("Item", item_dict.get("name"))