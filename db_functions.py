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
        return f"Did you mean one of these: {match_list}? Please confirm the customer name again.", {}
    
    return "Customer not found", {}


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


# ---------------------------------#
# Handle Invoice Creation
