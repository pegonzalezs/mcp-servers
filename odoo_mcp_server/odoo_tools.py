# odoo_tools.py
import asyncio
import json
import re
from typing import Dict, Any, List, Optional
import mcp.types as types
from odoo_connector import OdooConnector, save_config, normalize_vat
import sys


class OdooTools:
    def __init__(self, odoo_connector: Optional[OdooConnector]):
        self.connector = odoo_connector

    async def configure_odoo(self, args: Dict[str, Any]) -> List[types.TextContent]:
        def sync_logic():
            prompt = args["connection_string"]
            parts = prompt.split("|")
            if len(parts) != 4: return "❌ Incorrect format. Expected URL|DB|USER|PASSWORD"
            
            url, db, username, password = parts
            config = {"ODOO_URL": url.strip(), "ODOO_DB": db.strip(), "ODOO_USERNAME": username.strip(), "ODOO_PASSWORD": password.strip()}
            save_config(config)
            
            try:
                self.connector = OdooConnector()
                return f"✅ Config saved. Connection status: {'OK (UID: ' + str(self.connector.uid) + ')' if self.connector and self.connector.uid else 'Failed'}"
            except Exception as e:
                return f"❌ Error reconnecting: {e}"
        
        result = await asyncio.to_thread(sync_logic)
        return [types.TextContent(type="text", text=result)]
    
    async def get_contact_info(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """
        Gets information about an Odoo contact using their VAT.
        If you don't specify any particular fields, it will default to returning a summary of all available information.
        You can ask for specific fields using keywords like 'address', 'phone', 'email', 'job', or 'website'.
        If multiple contacts share the same VAT, you can add a name to the prompt to disambiguate.
        Example (Specific): 'get the job and phone for Addison Olson with vat US12345673'
        Example (Full Details): 'get the full details for vat US12345673'
        Example (Default): 'info for vat US12345673'
        """
       
        def sync_logic():
            prompt = args["prompt"]
            if not self.connector or not self.connector.uid:
                return "❌ Error: Not connected to Odoo. Use 'configure_odoo' first."

            vat_match = re.search(r'\b([A-Z0-9-]{7,15})\b', prompt, re.IGNORECASE)
            if not vat_match:
                return "Could not extract a VAT/Tax ID from the prompt text."
            normalized_vat_prompt = normalize_vat(vat_match.group(1))

            prompt_lower = prompt.lower()
            fields_to_query = {'name', 'vat'}
            
            field_map = {
                'address': ['contact_address_complete'],
                'phone': ['phone', 'mobile'],
                'email': ['email'],
                'job': ['function'],
                'website': ['website']
            }
            for keyword, odoo_fields in field_map.items():
                if keyword in prompt_lower:
                    fields_to_query.update(odoo_fields)
            
            if any(k in prompt_lower for k in ['all', 'full', 'details']):
                for odoo_fields in field_map.values():
                    fields_to_query.update(odoo_fields)
                    
            if len(fields_to_query) <= 2:
                print("No specific keywords found. Defaulting to 'full details'.", file=sys.stderr)
                for odoo_fields in field_map.values():
                    fields_to_query.update(odoo_fields)

            try:
                search_term = normalized_vat_prompt[-6:]
                candidates = self.connector.search_read('res.partner', [['vat', 'ilike', search_term]], list(fields_to_query))
                
                found_partners = [p for p in candidates if normalize_vat(p.get('vat')) == normalized_vat_prompt]

                if not found_partners:
                    return f"No contact found with the exact VAT '{normalized_vat_prompt}'."

                if len(found_partners) > 1:
                    for i, partner in enumerate(found_partners):
                        if partner.get('name') and partner['name'].lower().split()[0] in prompt_lower:
                            found_partners = [found_partners[i]]
                            break
                
                responses = []
                for partner in found_partners:
                    info = f"Information for {partner.get('name')} (VAT: {normalized_vat_prompt}):\n"
                    for field, value in partner.items():
                        if field in ['id', 'name', 'vat']: continue
                        
                        value_str = ""
                        if value:
                            if isinstance(value, list) and len(value) == 2: value_str = value[1]
                            elif not isinstance(value, list): value_str = str(value)
                        
                        if value_str and value_str != 'False':
                            field_label = field.replace('_', ' ').capitalize()
                            if field == 'function': field_label = "Job position"
                            if field == 'contact_address_complete': field_label = "Address"
                            info += f"  - {field_label}: {value_str}\n"
                    responses.append(info)

                return "\n---\n".join(responses)

            except Exception as e:
                return f"❌ Error while querying Odoo: {e}"

        # --- Bridge between ASYNC y SYNC ---
        result = await asyncio.to_thread(sync_logic)
        
        # --- Return the result as a TextContent ---
        return [types.TextContent(type="text", text=result)]
                
