# Copyright (c) 2025, Nivedita  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Buyer(Document):
    def validate(self):
        if not self.customer:
            frappe.throw("Customer is mandatory")
            
        if not self.portal_user:
            frappe.throw("Portal User is mandatory ")
        
    
    
	
      
 
     
     
