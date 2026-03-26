"""Brand colour constants for the TDM Streamlit app."""

INDIGO_600   = "#4F46E5"
INDIGO_100   = "#E0E7FF"
GREEN_600    = "#16A34A"
GREEN_100    = "#DCFCE7"
RED_600      = "#DC2626"
RED_100      = "#FEE2E2"
AMBER_500    = "#F59E0B"
AMBER_100    = "#FEF3C7"
GRAY_800     = "#1F2937"
GRAY_500     = "#6B7280"
GRAY_100     = "#F3F4F6"

STATUS_COLORS = {
    "SUCCESS":  GREEN_600,
    "RUNNING":  INDIGO_600,
    "FAILED":   RED_600,
    "PENDING":  AMBER_500,
    "SKIPPED":  GRAY_500,
    "QUEUED":   AMBER_500,
    "COMPLETE": GREEN_600,
}
