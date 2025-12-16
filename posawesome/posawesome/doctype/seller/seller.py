# Copyright (c) 2025, Nivedita  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Seller(Document):
	
	def validate(self):
		self.validate_unique_supplier()

	def validate_unique_supplier(self):
		mandatory_fields = [
			("supplier","Supplier"),
			("portal_user", "Portal User"),
            ("default_warehouse", "Default Warehouse"),
		]
  
		for fieldname, label in mandatory_fields:
			if not self.get(fieldname):
				frappe.throw(f"{label} is mandatory")

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
