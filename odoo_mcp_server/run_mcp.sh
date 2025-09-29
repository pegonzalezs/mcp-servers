#!/bin/bash

# Activa tu entorno virtual
source /opt/odoo/venv/bin/activate

# Ve al directorio raíz de tu nuevo proyecto modular
cd /opt/odoo/mcp-servers/odoo_mcp_server

# Ejecuta el punto de entrada
python main.py