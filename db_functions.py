import json
from db_utils import load_database, save_database, CUSTOMER_DB, PRODUCT_DB, INVOICE_DB
from models import Customer, Product, InvoiceItem, Invoice, InvoiceCreationState
from typing import Tuple, Dict, List, Any
from fuzzywuzzy import process

# ---------------------------------#
# Customer Database
# Read
def read_customer_db(dummy_param: str = "") -> str:
    """
    Run this function when user requests to read all entries in the customer database.

    Parameters:
    dummy_param (str): A dummy parameter to satisfy function call requirements.

    Returns:
    str: The listing of all entries in the customer database.
    """
    return json.dumps(load_database(CUSTOMER_DB), indent=4, sort_keys=False)


def read_specific_customer(company_name: str) -> str:
    """
    Run this function to read a specific customer entry by company name.

    Parameters:
    company_name (str): The name of the company to search for.

    Returns:
    str: The customer information if found, otherwise a message indicating that the company was not found.
    """
    database = load_database(CUSTOMER_DB)
    for customer in database:
        if customer['company_name'].lower() == company_name.lower():
            return json.dumps(customer, indent=4, sort_keys=False)
    return json.dumps({"message": "Company not found"}, indent=4, sort_keys=False)


def validate_customer(customer_name: str) -> Tuple[str, Dict]:
    """
    Validate and retrieve a customer from the customer database.

    Args:
        customer_name (str): The name of the customer to validate.

    Returns:
        Tuple[str, Dict]: A tuple containing a status message and 
        a dictionary of customer data if found, or an empty dict if not found.
    """
    customers = load_database(CUSTOMER_DB)
    
    # Check for exact match
    for customer_data in customers:
        if customer_data['company_name'].lower() == customer_name.lower():
            return "Customer found", Customer(**customer_data).to_dict()
    
    # Check for partial match using fuzzy matching
    customer_names = [c['company_name'] for c in customers]
    best_matches: List[Tuple[str, int]] = process.extractBests(customer_name, customer_names, limit=3, score_cutoff=60)
    
    if best_matches:
        match_names = [match[0] for match in best_matches]
        match_list = ", ".join(match_names)
        return f"Did you mean one of these: {match_list}? Please confirm the customer name again.", None
    
    return "Customer not found", None


# ---------------------------------#
# Product Database
# Read
def read_product_db(dummy_param: str = "") -> str:
    """
    Run this function when user requests to read all entries in the product database.

    Parameters:
    dummy_param (str): A dummy parameter to satisfy function call requirements.

    Returns:
    str: The listing of all entries in the product database.
    """
    return json.dumps(load_database(PRODUCT_DB), indent=4, sort_keys=False)


# def validate_product(product_name: str) -> Tuple[str, Dict | None]:
#     """
#     Validate and retrieve a product from the product database.

#     Args:
#         product_name (str): The name of the product to validate.

#     Returns:
#         Tuple[str, Dict | None]: A tuple containing a status message and 
#         a dictionary of product data if found, or None if not found.
#     """
#     products = load_database(PRODUCT_DB)
    
#     # Check for exact match
#     for product_data in products:
#         if product_data['name'].lower() == product_name.lower():
#             return "Product found", Product(**product_data).to_dict()

#     # Check for partial match using fuzzy matching
#     product_names = [p['name'] for p in products]
#     best_matches: List[Tuple[str, int]] = process.extractBests(product_name, product_names, limit=3, score_cutoff=60)
    
#     if best_matches:
#         match_names = [match[0] for match in best_matches]
#         match_list = ", ".join(match_names)
#         return f"Did you mean one of these: {match_list}? Please confirm the product name again.", None
    
#     return "Product not found", None


# ---------------------------------#
# Invoice Database
# Read
def read_invoice_db(dummy_param: str = "") -> str:
    """
    Run this function when user requests to read all entries in the invoice database.

    Parameters:
    dummy_param (str): A dummy parameter to satisfy function call requirements.

    Returns:
    str: The listing of all entries in the invoice database.
    """
    return json.dumps(load_database(INVOICE_DB), indent=4, sort_keys=False)

def save_invoice(customer: str, product_items: str) -> str:
    """
    Save the user input details to invoice database, supporting multiple product_items.
    
    Parameters:
    customer (str): The customer of the invoice.
    product_items (str): A string representation of items, each item separated by semicolons (;), and each item's properties separated by commas (,) in the order:
        item_name,uom,unit_price,quantity
        Example:    "Sarawak Laksa (small),bowl,10.00,2;
                    Nasi Lemak,plate,15.00,1"
    
    Returns:
    str: Confirmation message including invoice details.
    """
    invoice_db = load_database("invoice_db.json")

    # Generate a new invoice ID in the format INV_0001
    new_invoice_id = f"INV_{len(invoice_db) + 1:04d}"

    # Parse items string into a list of dictionaries
    item_list = []
    total = 0
    for item_str in product_items.split(';'):
        item_name, uom, unit_price, quantity = item_str.split(',')
        unit_price = float(unit_price)
        quantity = int(quantity)
        subtotal = unit_price * quantity
        total += subtotal
        item_list.append({
            "product_name": item_name,
            "product_uom": uom,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        })

    # Create the invoice details
    invoice_details = {
        "recipient": customer,
        "items": item_list,
        "total": total
    }

    # Save the new invoice
    invoice_db[new_invoice_id] = invoice_details
    save_database("invoice_db.json", invoice_db)

    return f"Invoice {new_invoice_id} with {len(item_list)} item(s) saved successfully. Total: ${total:.2f}"



# ---------------------------------#
# Handle Invoice Creation

# def create_invoice(customer_name=None, product_name=None, uom=None, quantity=None) -> Tuple[str]:
#     """
#     Create a new invoice and manage the creation process.

#     Returns:
#     """
    


def calculate_subtotal(quantity: float, unit_price: float) -> float:
    """
    Calculate the subtotal based on the quantity and price of an item.

    Parameters:
    quantity (float): The quantity of the item.
    unit_price (float): The unit price of the item.

    Returns:
    float: The calculated subtotal.

    Raises:
    ValueError: If unit_price is None.
    """
    if unit_price is None:
        raise ValueError("Unit price cannot be None")
    return quantity * unit_price