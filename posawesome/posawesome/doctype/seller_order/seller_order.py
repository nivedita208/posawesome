# Copyright (c) 2025, Nivedita  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

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


###############deluver button code #########################

import frappe

@frappe.whitelist()
def make_dn_from_seller_order(seller_order_name):

	# Get Seller Order
	seller_order = frappe.get_doc("Seller Order", seller_order_name)
	# Get linked Sales Order
	sales_order = frappe.get_doc("Sales Order", seller_order.sales_order)
	# Validate Sales Order link
	if not seller_order.sales_order:
		frappe.throw("Sales Order not linked with Seller Order")

	# Permission check (temporarily commented safely)
	# if (
	#     frappe.session.user != seller_order.seller_user
	#     and not frappe.has_role("System Manager")
	# ):
	#     frappe.throw("You are not allowed to create Delivery Note")

	# Create Delivery Note
	dn = frappe.new_doc("Delivery Note")
	dn.customer = seller_order.customer
	dn.sales_order = seller_order.sales_order
	dn.set_warehouse = seller_order.seller_warehouse
	dn.custom_seller_order = seller_order.name
	dn.company = sales_order.company    

	# Add items only from Seller Order
	for item in seller_order.items:
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
	seller_order.delivery_note = dn.name
	seller_order.status = "Delivered"
	seller_order.save(ignore_permissions=True)

	return dn.name

# done work : delivery note creating 
# pending : fetching uom its mandatory in delivery note 
# delivery note date and posting date changing i mean we are directly submitting the doc so?
