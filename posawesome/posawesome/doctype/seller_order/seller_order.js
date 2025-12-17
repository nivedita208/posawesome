// Copyright (c) 2025, Nivedita  and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seller Order', {
	refresh: function(frm) {

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

	