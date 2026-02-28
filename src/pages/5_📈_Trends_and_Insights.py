# ==============================================================================
# Refactored Trends and Insights Module Entrypoint
# The heavy lifting has been moved to src/views/trends/
# ==============================================================================
from views.trends.render import render_trends_and_insights

# Execute the isolated render process
render_trends_and_insights()
