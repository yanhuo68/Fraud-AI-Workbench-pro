# ==============================================================================
# Refactored ML Workflow Module Entrypoint
# The heavy lifting has been moved to src/views/ml_workflow/
# ==============================================================================
from views.ml_workflow.render import render_ml_workflow

# Execute the isolated render process
render_ml_workflow()
