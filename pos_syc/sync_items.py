import frappe
from pos_syc.requests_api import get_request
from pos_syc.utils import get_syc_settings, create_sync_log


def sync_items():
    last_update = get_syc_settings().last_update

    try:
        res = get_request(
                method="pos_sym.api.get_items",
                params={"last_update": last_update}
            )

        if res:
            docs_list = res.json()["message"]

            for doc in docs_list:
                # create items
                create_item(doc)

    except Exception as e:
        print(e)
        create_sync_log(status="Error", data=frappe.get_traceback())



def create_item(item_dict):
    if not is_item_exist(item_dict):
        # Create Item
        try:
            item_dict["doctype"] = "Item"
            item_child_tables = item_dict["tables"]

            del item_dict["sym_publish_to_local_pos"]
            del item_dict["tables"]


            for child_table_key in item_child_tables:
                table_name = list(child_table_key.keys())[0]
                child_table_data = child_table_key[table_name]
            
                if len(child_table_data) > 0:
                    item_dict[child_table_data[0].get("parentfield")] = child_table_data

            new_item = frappe.get_doc(item_dict)
            new_item.flags.ignore_mandatory = True
            new_item.insert()
          
            log_data = f"""
                Doctype: Item
                DocName: {item_dict["name"]}
            """
            
            create_sync_log("Create", data=log_data)
        except Exception as e:
            create_sync_log("Error")
    
    else:
        # Update Item
        try:

            item_dict["doctype"] = "Item"
            item_child_tables = item_dict["tables"]

            del item_dict["sym_publish_to_local_pos"]
            del item_dict["tables"]


            for child_table_key in item_child_tables:
                table_name = list(child_table_key.keys())[0]
                child_table_data = child_table_key[table_name]
            
                if len(child_table_data) > 0:
                    item_dict[child_table_data[0].get("parentfield")] = child_table_data
            frappe.delete_doc_if_exists("Item", item_dict.get("name"), force=True)
            new_item = frappe.get_doc(item_dict)
            # new_item.flags.ignore_mandatory = True
            # new_item.flags.ignore_validate = True
            # frappe.flags.ignore_validate = True
            
            new_item.insert()            

            
            # log
            log_data = f"""
                Doctype: Item
                DocName: {item_dict["name"]}
            """
            create_sync_log("Update", data=log_data)
        except Exception as e:
            create_sync_log("Error")


def is_item_exist(item_dict):
    return frappe.db.exists("Item", item_dict.get("name"))