# Copyright (c) 2025, Nivedita  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice

class SellerOrder(Document):
	def validate(self):
     
		total_qty = 0        
		total_amount = 0

		for item in self.items:            
			item.amount = item.qty * item.rate #each row amount
			total_qty =  total_qty + item.qty
			total_amount = total_amount + item.amount

		self.total_qty = total_qty
		self.total_amount = total_amount


###############deliver button code ########################

@frappe.whitelist()
def make_dn_from_seller_order(seller_order_name):

	# Get Seller Order
	seller_order = frappe.get_doc("Seller Order", seller_order_name)
 
	# Get linked Sales Order
	sales_order = frappe.get_doc("Sales Order", seller_order.sales_order)
	if seller_order.delivery_note:
		frappe.throw("Delivery Note already created")
	if seller_order.status != "Open":
		frappe.throw("Delivery Note can only be created when status is Open")
 
	# Validate Sales Order link
	if not seller_order.sales_order:
		frappe.throw("Sales Order not linked with Seller Order")

	# Permission check 
	if (
	    frappe.session.user != seller_order.seller_user
	    and "System Manager" not in frappe.get_roles()
	):
	    frappe.throw("You are not allowed to create Delivery Note")

	# Create Delivery Note
	dn = frappe.new_doc("Delivery Note")
	dn.customer = seller_order.customer
	dn.sales_order = seller_order.sales_order
	dn.set_warehouse = seller_order.seller_warehouse
	dn.custom_seller_order_ = seller_order.name
	dn.company = sales_order.company    

	# Add items only from Seller Order
	for item in seller_order.items:
		if not item.uom:
			frappe.throw("UOM is mandatory")
     
		dn.append("items", {
			"item_code": item.item,
			"qty": item.qty,
			"rate": item.rate,
			"uom": item.uom,
			"amount": item.amount,
			"warehouse": seller_order.seller_warehouse,
			"so_detail": item.so_item_ref,
			"against_sales_order": sales_order.name
		})

	# Save & Submit DN
	dn.insert(ignore_permissions=True)
	dn.submit()

	# Update Seller Order
	seller_order.db_set("delivery_note", dn.name)
	seller_order.db_set("status", "Delivered")
	seller_order.save(ignore_permissions=True)

	return dn.name

#############################################

@frappe.whitelist()
def make_si_from_seller_order(seller_order_name):

	# Get Seller Order
	seller_order = frappe.get_doc("Seller Order", seller_order_name)

	# Validations
	if not seller_order.delivery_note:
		frappe.throw("Delivery Note not created yet")

	if seller_order.sales_invoice:
		frappe.throw("Sales Invoice already created")

	# Permission check
	# if (
	# 	frappe.session.user != seller_order.seller_user
	# 	and "System Manager" not in frappe.get_roles()
	# ):
	# 	frappe.throw("You are not allowed to create Sales Invoice")

	# Get Delivery Note
	dn = frappe.get_doc("Delivery Note", seller_order.delivery_note)

	if dn.docstatus != 1:
		frappe.throw("Delivery Note must be submitted")

	# Create Sales Invoice from DN (STANDARD ERPNext METHOD)
	si = make_sales_invoice(dn.name)

	
	si.custom_seller_order = seller_order.name

	# Insert & Submit SI
	si.insert(ignore_permissions=True)
	si.submit()

	# Update Seller Order
	seller_order.db_set("sales_invoice",si.name)
	seller_order.db_set("status","Invoiced")
	seller_order.save(ignore_permissions=True)

	return si.name

