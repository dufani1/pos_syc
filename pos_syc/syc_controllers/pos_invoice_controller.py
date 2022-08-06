import frappe
from pos_syc.utils import syc_create_backlog

CONTROLLER_DOCTYPE = "POS Invoice"

def doc_event(event_doc, event_name):
    if event_doc.doctype == CONTROLLER_DOCTYPE:
        if event_name == "validate":
            if not frappe.db.exists(event_doc.doctype, event_doc.name):
                # create doc
                create_insert_backlog(event_doc)
            else:
                # update doc
                create_update_backlog(event_doc)
        elif event_name == "on_trash":
            # trash doc
            create_delete_backlog(event_doc)

def create_insert_backlog(event_doc):

    # create insert backlogs 
        syc_create_backlog(
            doctype=CONTROLLER_DOCTYPE,
            docname=event_doc.name,
            data=event_doc.as_json(),
            event_type="Insert",
            status="Pending"
        )    

def create_update_backlog(event_doc):
    syc_create_backlog(
        doctype=CONTROLLER_DOCTYPE,
        docname=event_doc.name,
        data=event_doc.as_json(),
        event_type="Update",
        status="Pending"
    )

def create_delete_backlog(event_doc):
    syc_create_backlog(
        doctype=CONTROLLER_DOCTYPE,
        docname=event_doc.name,
        data=event_doc.as_json(),
        event_type="Delete",
        status="Pending"
    )    


def prepare():
    try:
        cond_filters = {}
        print("PREPARE SYC POS INVOICE")
        _entries = frappe.get_all(
            CONTROLLER_DOCTYPE,
            fields=["name"],
            filters=cond_filters,
            order_by="modified asc"
        )

        for entry in _entries:
            doc_orm = frappe.get_doc(CONTROLLER_DOCTYPE, entry.name)

            syc_create_backlog(
                doctype=CONTROLLER_DOCTYPE,
                docname=doc_orm.name,
                data=doc_orm.as_json(),
                event_type="Init",
                status="Pending"
            ) 
        return None
    except Exception as e:
        print(e)


# any extra validations below