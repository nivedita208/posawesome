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

        # Fetch Item master
        item = frappe.get_doc("Item", row.item_code)

        # Seller must be set in Item
        if not item.custom_seller:
            frappe.throw(
                f"Seller not set in Item master for {row.item_code}"
            )

        # Set seller on SO item
        row.custom_seller = item.custom_seller

        # Fetch Seller
        seller = frappe.get_doc("Seller", item.custom_seller)

        # Seller must have default warehouse
        if not seller.default_warehouse:
            frappe.throw(
                f"Default Warehouse missing for Seller {seller.name}"
            )

        # Set warehouse on SO item
        row.custom_seller_warehouse = seller.default_warehouse
        
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
                # "amount": so_item.amount,
                "so_item_ref": so_item.name
            })

        seller_order.insert(ignore_permissions=True)
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


'''
done work:
1.on submitting sales order seller orders getting created
2.based on item,seller if item a has 1b eller and item 2 has 2b seller then 2 seller order get created
3.amended form again submit then seller order creaton blocked
4.msg is showing on submitting and i mean after creation of seller order
 



'''