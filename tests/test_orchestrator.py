from personal_ai_team.orchestrator import Orchestrator


def test_travel_route():
    result = Orchestrator().route("Find a hotel for my trip")
    assert result.agent == "travel"


def test_employer_route():
    result = Orchestrator().route("Find direct solar employers in Germany")
    assert result.agent == "employer_sourcing"


def test_unknown_route():
    result = Orchestrator().route("Something unrelated")
    assert result.agent == "orchestrator"
