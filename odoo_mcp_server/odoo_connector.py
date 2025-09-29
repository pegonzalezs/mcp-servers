# odoo_connector.py
import os
import json
import re
import xmlrpc.client
import sys

CONFIG_FILE = "odoo_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def normalize_vat(vat: str) -> str:
    """
    Cleans and standardizes a VAT/Tax ID string.
    - Converts to uppercase.
    - Removes all non-alphanumeric characters.
    Example: 'US-123.456.73' -> 'US12345673'
    """
    if not vat:
        return ""
    return re.sub(r'[^A-Z0-9]', '', vat.upper())

class OdooConnector:
    def __init__(self):
        self.config = self._get_config_or_fail()
        self.url = self.config.get("ODOO_URL")
        self.db = self.config.get("ODOO_DB")
        self.username = self.config.get("ODOO_USERNAME")
        self.password = self.config.get("ODOO_PASSWORD")
        self.uid = None
        self.connect()

    def _get_config_or_fail(self):
        config = load_config()
        if not config:
            raise FileNotFoundError(f"'{CONFIG_FILE}' not found.")
        return config

    def connect(self):
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                print(f"Odoo auth failed for '{self.username}'.", file=sys.stderr)
        except Exception as e:
            print(f"Failed to connect to Odoo: {e}", file=sys.stderr)
            self.uid = None

    def search_read(self, model, domain, fields):
        if not self.uid:
            raise ConnectionError("Not authenticated in Odoo.")
        try:
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            return models.execute_kw(self.db, self.uid, self.password, model, 'search_read', [domain], {'fields': fields})
        except Exception as e:
            raise Exception(f"Odoo API call error: {e}")