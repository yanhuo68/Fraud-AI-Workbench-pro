# ==============================================================================
# Refactored Data Hub Module Entrypoint
# The heavy lifting has been moved to src/views/data_hub/
# ==============================================================================
import streamlit as st
from views.data_hub.render import render_data_hub

# Execute the isolated render process
render_data_hub()
