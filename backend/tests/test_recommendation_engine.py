from backend.services import recommendation_engine as recommendation_module
from backend.services.recommendation_engine import RecommendationEngine


class EmptyCursor:
    def execute(self, *_args, **_kwargs):
        return self

    def fetchone(self):
        return None


class EmptyConnection:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return EmptyCursor()


def test_no_recommendation_is_created_from_profile_defaults(monkeypatch):
    monkeypatch.setattr(
        recommendation_module,
        "get_student_profile",
        lambda _student_id: {
            "current_subject": "",
            "current_topic": "Example topic",
            "mastery_score": 10.0,
            "level": "Beginner",
        },
    )
    monkeypatch.setattr(recommendation_module, "get_db_connection", EmptyConnection)
    monkeypatch.setattr(recommendation_module, "list_revision_items", lambda **_kwargs: [])

    recommendation = RecommendationEngine().get_next_recommendation(student_id=42)

    assert recommendation is None


def test_recommendation_uses_recorded_repeated_mistakes(monkeypatch):
    class WeakAreaCursor(EmptyCursor):
        def fetchone(self):
            return {
                "topic": "Recorded quiz topic",
                "subject": "Mathematics",
                "mistake_count": 2,
            }

    class WeakAreaConnection(EmptyConnection):
        def cursor(self):
            return WeakAreaCursor()

    monkeypatch.setattr(
        recommendation_module,
        "get_student_profile",
        lambda _student_id: {"current_subject": "", "level": "Intermediate"},
    )
    monkeypatch.setattr(recommendation_module, "get_db_connection", WeakAreaConnection)

    recommendation = RecommendationEngine().get_next_recommendation(student_id=42)

    assert recommendation is not None
    assert recommendation["topic"] == "Recorded quiz topic"
    assert recommendation["subject"] == "Mathematics"
    assert recommendation["recommended_action"] == "REVIEW_MISTAKES"
