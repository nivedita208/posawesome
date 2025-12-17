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



	
