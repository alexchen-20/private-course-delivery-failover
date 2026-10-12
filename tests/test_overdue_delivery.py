from datetime import datetime, timezone

from course_delivery.delivery_service import deliver_course
from course_delivery.models import CourseDeliveryRequest, ProgressState


class RecordingWriter:
    def __init__(self) -> None:
        self.prompt = ""

    def write_lesson(self, prompt: str) -> str:
        self.prompt = prompt
        return "# Dose calculations\nCheck units before calculating.\n\nWhat is the first check?"


def test_overdue_delivery_flags_report_without_disclosing_learner_ref() -> None:
    writer = RecordingWriter()
    request = CourseDeliveryRequest(
        learner_ref="learner-7f2c",
        course_title="Medication safety",
        lesson_title="Dose calculations",
        learning_objective="Check units before calculating a dose",
        deadline=datetime(2026, 9, 5, 9, 0, tzinfo=timezone.utc),
        observed_at=datetime(2026, 9, 6, 9, 0, tzinfo=timezone.utc),
    )

    result = deliver_course(request, writer)

    assert result.educator_report.progress is ProgressState.OVERDUE
    assert result.educator_report.needs_attention is True
    assert result.educator_report.note == "Deadline passed; contact the learner."
    assert result.learner_ref == "learner-7f2c"
    assert "learner-7f2c" not in writer.prompt
    assert "Medication safety" in writer.prompt
