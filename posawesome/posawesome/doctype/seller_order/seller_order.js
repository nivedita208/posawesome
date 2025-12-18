// Copyright (c) 2025, Nivedita  and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seller Order', {
	refresh: function(frm) {

		if (frm.doc.status === "Open" && !frm.doc.delivery_note) {

			let deliver_btn = frm.add_custom_button(__('Deliver'), function () {
				frappe.confirm(
					"Are you sure you want to create & submit Delivery Note?",
					function () {
						frappe.call({
							method: "posawesome.posawesome.doctype.seller_order.seller_order.make_dn_from_seller_order",
							args: {
								seller_order_name: frm.doc.name
							},
							callback: function (r) {
								if (!r.exc) {
									frappe.msgprint("Delivery Note created successfully");
									frm.reload_doc();
								}
							}
						});
					}
				);
			}, __('Create'));

			let Invoice_btn = frm.add_custom_button(__('Invoice'), function () {
				frappe.msgprint("Invoice button clicked");
			}, __('Create'));

			deliver_btn.addClass('btn-primary');
			Invoice_btn.addClass('btn-primary');

		}
	}
});

frappe.ui.form.on('Seller Order Item', {

	qty(frm, cdt, cdn) {
		calculate_totals(frm);
	},

	rate(frm, cdt, cdn) {
		calculate_totals(frm);
	},

	items_remove(frm) {
		calculate_totals(frm);
	}
});

function calculate_totals(frm) {

	let total_qty = 0;
	let total_amount = 0;

	(frm.doc.items || []).forEach(item => {

		//  Row-level amount calculation
		item.amount = (item.qty || 0) * (item.rate || 0);

		//  Totals
		total_qty += item.qty || 0;
		total_amount += item.amount || 0;
	});

	//  Refresh child table so amount shows
	frm.refresh_field("items");

	//  Set parent totals
	frm.set_value("total_qty", total_qty);
	frm.set_value("total_amount", total_amount);
}

	