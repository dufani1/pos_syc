import frappe
from pos_syc.requests_api import get_request
from pos_syc.utils import get_syc_settings, create_sync_log


def sync_customers():
    last_update = get_syc_settings().last_update
    try:
        res = get_request(
                method="pos_sym.api.get_customers",
                params={"last_update": last_update}
            )

        print(res.content)
        if res:
            docs_list = res.json()["message"]

            for doc in docs_list:
                # create customers
                create_customer(doc)

    except Exception as e:
        print(e)
        create_sync_log(status="Error", data=frappe.get_traceback())

def create_customer(item_dict):
    # Create Customer
    if not frappe.db.exists("Customer", item_dict.get("name")):
        try:
            item_dict["doctype"] = "Customer"
            item_child_tables = item_dict["tables"]

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
                Doctype: Customer
                DocName: {item_dict["name"]}
            """
            
            create_sync_log("Create", data=log_data)
        except Exception as e:
            create_sync_log("Error")
    
    else:
        # Update Customer
        try:

            item_dict["doctype"] = "Customer"
            item_child_tables = item_dict["tables"]

            del item_dict["tables"]


            for child_table_key in item_child_tables:
                table_name = list(child_table_key.keys())[0]
                child_table_data = child_table_key[table_name]
            
                if len(child_table_data) > 0:
                    item_dict[child_table_data[0].get("parentfield")] = child_table_data
            frappe.delete_doc_if_exists("Customer", item_dict.get("name"), force=True)
            print("insert", item_dict)
            new_item = frappe.get_doc(item_dict)
            # new_item.flags.ignore_mandatory = True
            # new_item.flags.ignore_validate = True
            # frappe.flags.ignore_validate = True
            
            new_item.insert()            

            
            # log
            log_data = f"""
                Doctype: Customer
                DocName: {item_dict["name"]}
            """
            create_sync_log("Update", data=log_data)
        except Exception as e:
            create_sync_log("Error")
