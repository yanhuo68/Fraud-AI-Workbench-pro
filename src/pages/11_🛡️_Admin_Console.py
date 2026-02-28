# ==============================================================================
# Refactored Admin Console Entrypoint
# The heavy lifting has been moved to src/views/admin_console/
# ==============================================================================
from views.admin_console.render import render_admin_console

# Execute the isolated render process
render_admin_console()
