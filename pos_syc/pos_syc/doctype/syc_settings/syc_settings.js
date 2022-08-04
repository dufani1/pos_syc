// Copyright (c) 2022, . and contributors
// For license information, please see license.txt

frappe.ui.form.on('SYC Settings', {
	refresh: function(frm) {
		var eval_button = frm.add_custom_button("Eval Pull Logs", function() {
			
			frappe.call({
				method: "pos_syc.api.syc_eval_pull_logs",
				callback: function(r) {
					if (r.message) {

					} else {
					}
				}
			})
		});

		var sync_button = frm.add_custom_button("Pull Backlogs", function() {
			
			frappe.call({
				method: "pos_syc.api._syc_pull_backlogs",
				callback: function(r) {
					if (r.message) {
						frappe.show_alert("SYC: Sync in Progress", 8);
						sync_button.prop("disabled", true);
						setTimeout(()=> {
							sync_button.prop("disabled", false);
						}, 8000);
					} else {
						frappe.show_alert("SYC: Sync Failed to Start", 8);
					}
				}
			})
		});

		// prepare pos
		var prepare_pos = frm.add_custom_button("Prepare POS", function() {
			frappe.call({
				type: "POST",
				method: "pos_syc.syc_prepare_pos.prepare",
				callback: function(r) {
					console.log(r.message);
					if(r.message) {
						frm.doc.is_prepared = 1;
						frm.refresh_field("is_prepared");
						frm.refresh_field("preparation_date");
						frappe.show_alert("SYC: POS Prepared Successfully!", 8);
					} else {
						frappe.show_alert("SYC: POS Prepare Failed!", 8);
					}
					if(!frm.doc.is_prepared) {
						sync_button.prop("disabled", true);
						prepare_pos.prop("disabled", false);
						revoke_pos.prop("disabled", true);
					} else {
						sync_button.prop("disabled", false);
						prepare_pos.prop("disabled", true);
						revoke_pos.prop("disabled", false);
					}
				}
			})
		})

		// revoke preparations
		var revoke_pos = frm.add_custom_button("Revoke Preparations", function() {
			// frappe.confirm("SYC: This will Revoke all the SYM Backlogs for this client, Are you Sure ?", () => {
				frappe.call({
					type: "POST",
					method: "pos_syc.syc_prepare_pos.revoke",
					callback: function(r) {
						console.log(r.message);
						if(r.message) {
							frm.doc.is_prepared = 0;
							frm.refresh_field("is_prepared");
							frappe.show_alert("SYC: POS Preparations Revoked Successfully!", 8);
						} else {
							frappe.show_alert("SYC: POS Revoke Failed!", 8);
						}
						if(!frm.doc.is_prepared) {
							sync_button.prop("disabled", true);
							prepare_pos.prop("disabled", false);
							revoke_pos.prop("disabled", true);
						} else {
							sync_button.prop("disabled", false);
							prepare_pos.prop("disabled", true);
							revoke_pos.prop("disabled", false);
						}
					}
				})
			// })
		})

		if(!frm.doc.is_prepared) {
			sync_button.prop("disabled", true);
			prepare_pos.prop("disabled", false);
			revoke_pos.prop("disabled", true);
		} else {
			sync_button.prop("disabled", false);
			prepare_pos.prop("disabled", true);
			revoke_pos.prop("disabled", false);
		}
	}
});
