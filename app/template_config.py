"""
Precision VRT Solo — Instância compartilhada de Jinja2Templates

TODOS os roteadores web devem importar `templates` daqui para garantir
que os globals registrados (has_permission, filter_menu, SIDEBAR_MENU_STRUCTURE)
estejam disponíveis em TODOS os templates.
"""
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
