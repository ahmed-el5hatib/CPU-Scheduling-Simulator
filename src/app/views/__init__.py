"""Views package."""

from app.views.comparison import ComparisonView
from app.views.dashboard import DashboardView
from app.views.guide import GuideView
from app.views.process_manager import ProcessManagerView
from app.views.simulator import SimulatorView

__all__ = [
    "DashboardView",
    "ProcessManagerView",
    "SimulatorView",
    "ComparisonView",
    "GuideView",
]
