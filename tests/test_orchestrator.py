from personal_ai_team.orchestrator import Orchestrator
from personal_ai_team.sdk_agents import SPECIALIZED_AGENTS


def test_travel_route():
    result = Orchestrator().route("Find a hotel for my trip")
    assert result.agent == "travel"


def test_employer_route():
    result = Orchestrator().route("Find direct solar employers in Germany")
    assert result.agent == "employer_sourcing"


def test_investment_route():
    result = Orchestrator().route("Analyze my ETF portfolio")
    assert result.agent == "investment"


def test_admin_route():
    result = Orchestrator().route("Write an email to close my account")
    assert result.agent == "admin"


def test_content_route():
    result = Orchestrator().route("Analyze why my YouTube channel is not growing")
    assert result.agent == "content"


def test_unknown_route():
    result = Orchestrator().route("Something unrelated")
    assert result.agent == "orchestrator"


def test_all_specialized_sdk_agents_exist():
    assert set(SPECIALIZED_AGENTS) == {
        "travel",
        "investment",
        "admin",
        "content",
        "employer_sourcing",
    }
