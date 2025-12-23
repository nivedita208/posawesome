import frappe


def is_marketplace_order(doc, method):

    # Only for marketplace orders
    if not doc.custom_is_marketplace_order:
        return

    # Buyer must be set
    if not doc.custom_marketplace_buyer:
        frappe.throw("Marketplace Buyer is mandatory")

    # Validate each item
    for row in doc.items:

        # Fetch Item 
        item = frappe.get_doc("Item", row.item_code)

        # Seller must be set in Item
        if not item.custom_seller:
            frappe.throw(
                f"Seller not set in Item  for {row.item_code}"
            )

        # Set seller on SO item
        row.custom_seller = item.custom_seller

        seller_name = item.custom_seller  # Seller document name

        warehouse = frappe.db.get_value(
            "Seller",
            seller_name,
            "default_warehouse"
        )

        if not warehouse:
            frappe.throw(
                f"Default Warehouse missing for Seller {seller_name}"
            )

        row.custom_seller_warehouse = warehouse
        
        
###################################



def create_seller_orders(doc, method):
    
    # prevent creation for amended form
    if doc.amended_from:
        return
    
    so = frappe.get_doc("Sales Order", doc.name)

    seller_items_map = {}
    created_seller_orders = []

    for item in so.items:
        if not item.custom_seller:
            frappe.throw(f"Seller not set for item {item.item_code}")

        seller_items_map.setdefault(item.custom_seller, []).append(item)

    for custom_seller, items in seller_items_map.items():
        
        
        
        seller_doc = frappe.get_doc("Seller", custom_seller)
        
        seller_order = frappe.new_doc("Seller Order")

        seller_order.seller = custom_seller
        seller_order.customer = so.customer
        seller_order.sales_order = so.name
        seller_order.transaction_date = so.transaction_date
        seller_order.seller_user = seller_doc.portal_user
        seller_order.seller_warehouse = seller_doc.default_warehouse

        for so_item in items:
            seller_order.append("items", {
                "item": so_item.item_code,
                "qty": so_item.qty,
                "rate": so_item.rate,
                "uom":so_item.uom,
                # "amount": so_item.amount,
                "so_item_ref": so_item.name
            })

        seller_order.insert(ignore_permissions=True)
        seller_order.submit()
        created_seller_orders.append(seller_order.name)

        for so_item in items:
            frappe.db.set_value(
                "Sales Order Item",
                so_item.name,
                "custom_seller_order",
                seller_order.name
            )
            
    if created_seller_orders:
        frappe.msgprint(
            f"Seller Order created successfully:<br><b>{', '.join(created_seller_orders)}</b>"
        )


