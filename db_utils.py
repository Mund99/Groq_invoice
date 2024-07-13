import os
import json

DB_FOLDER = "database"
CUSTOMER_DB = "customer_db.json"
PRODUCT_DB = "product_db.json"
INVOICE_DB = "invoice_db.json"

def load_database(file_name):
    file_path = os.path.join(DB_FOLDER, file_name)
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_database(file_name, data):
    file_path = os.path.join(DB_FOLDER, file_name)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
