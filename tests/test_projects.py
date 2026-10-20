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
