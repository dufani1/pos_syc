// Copyright (c) 2022, . and contributors
// For license information, please see license.txt

frappe.ui.form.on('SYC Settings', {
	refresh: function(frm) {
		var sync_button = frm.add_custom_button("Sync", function() {
			sync_button.prop("disabled", true)
			setTimeout(()=> {
				sync_button.prop("disabled", false)
			}, 3000);
	
			frappe.call({
				method: "pos_syc.api.syc_sync_main",
				callback: function(r) {
					if (r.message) {
						frappe.show_alert("SYC: Sync in Progress", 3)
					} else {
						frappe.show_alert("SYC: Sync Failed to Start", 3)
					}
				}
			})
		})
		frm.add_custom_button("Reset Last Update", function() {
			frappe.call({
				type: "GET",
				method: "pos_syc.api.syc_reset_last_update",
				callback: function(r) {
					frm.doc.last_update = undefined;
					frm.refresh_field("last_update")
					frappe.show_alert("SYC: Last Update Reseted", 3)
				}
			})
		})
	}
});
