# Copyright (c) 2025, Nivedita  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Seller(Document):
	
	def validate(self):
		self.validate_unique_supplier()

	def validate_unique_supplier(self):
		if not self.supplier:
			return

		existing_seller = frappe.db.exists(
		"Seller",
		{
			"supplier": self.supplier,
			"name": ["!=", self.name]
		}
		)

		if existing_seller:
			frappe.throw(
				f"Seller already exists for Supplier {self.supplier}"
			)
