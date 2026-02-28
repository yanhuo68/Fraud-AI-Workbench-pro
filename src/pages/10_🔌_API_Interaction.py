# ==============================================================================
# Refactored API Interaction Entrypoint
# The heavy lifting has been moved to src/views/api_interaction/
# ==============================================================================
from views.api_interaction.render import render_api_interaction

# Execute the isolated render process
render_api_interaction()
