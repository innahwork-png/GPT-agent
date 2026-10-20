"""Four user-facing project workspaces layered over existing specialist agents.

This module does not replace the SDK's specialist delegation.
"""
from dataclasses import dataclass
from .orchestrator import Orchestrator

PROJECTS = {
    "travel_assistant": ("travel",),
    "trading_investment": ("investment",),
    "youtube_instagram_development": ("content",),
    "general_assistant": ("general", "admin", "employer_sourcing", "cinemood"),
}

@dataclass(frozen=True)
class ProjectRoute:
    project: str
    specialist: str
    reason: str

def route_project(task: str) -> ProjectRoute:
    """Map a user request to one of four projects, retaining the specialist."""
    text = task.casefold()
    if any(k in text for k in ("crypto", "trading", "bitcoin", "крипт", "трейд", "биткоин")):
        return ProjectRoute("trading_investment", "investment", "Trading-specific terms")
    if any(k in text for k in ("reels", "shorts", "рилс", "камилл", "camilla")):
        return ProjectRoute("youtube_instagram_development", "content", "Video-specific terms")
    route = Orchestrator().route(task)
    for project, specialists in PROJECTS.items():
        if route.agent in specialists:
            return ProjectRoute(project, route.agent, route.reason)
    return ProjectRoute("general_assistant", "general", "Default general project")
