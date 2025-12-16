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