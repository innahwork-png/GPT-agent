from personal_ai_team.projects import PROJECTS, route_project

def test_four_workspaces():
    assert len(PROJECTS) == 4

def test_project_routing():
    examples = {
        "Book a hotel in Tokyo": "travel_assistant",
        "Analyze my ETF portfolio": "trading_investment",
        "Analyze bitcoin trading": "trading_investment",
        "Prepare Instagram Reels for Camilla": "youtube_instagram_development",
        "Write an email to close my account": "general_assistant",
        "Explain this general question": "general_assistant",
    }
    for task, expected in examples.items():
        assert route_project(task).project == expected

def test_project_api_endpoints():
    from fastapi.testclient import TestClient
    from personal_ai_team.main import app
    client = TestClient(app)
    # Auth is configured in production; in tests use a temporary known token.
    import os
    from unittest.mock import patch
    with patch.dict(os.environ, {"AGENT_API_TOKEN": "test-project-route-token"}):
        headers = {"x-api-key": "test-project-route-token"}
        projects = client.get("/projects", headers=headers)
        assert projects.status_code == 200
        assert len(projects.json()["projects"]) == 4
        routed = client.post("/project-route", json={"task": "Analyze bitcoin trading"}, headers=headers)
        assert routed.status_code == 200
        assert routed.json()["project"] == "trading_investment"
        unauthorized = client.get("/projects")
        assert unauthorized.status_code == 401
