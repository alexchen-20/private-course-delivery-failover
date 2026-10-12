from .infrai_course_writer import CourseWriter
from .models import (
    CourseDeliveryRequest,
    CourseDeliveryResponse,
    EducatorReport,
    ProgressState,
)


def progress_for(request: CourseDeliveryRequest) -> ProgressState:
    if request.completed:
        return ProgressState.ON_TRACK
    if request.observed_at > request.deadline:
        return ProgressState.OVERDUE
    return ProgressState.DUE


def deliver_course(
    request: CourseDeliveryRequest, writer: CourseWriter
) -> CourseDeliveryResponse:
    progress = progress_for(request)
    needs_attention = progress is ProgressState.OVERDUE

    # Keep learner identity local. The model receives course content only.
    prompt = (
        f"Course: {request.course_title}\n"
        f"Lesson: {request.lesson_title}\n"
        f"Learning objective: {request.learning_objective}"
    )
    lesson = writer.write_lesson(prompt)

    note = (
        "Deadline passed; contact the learner."
        if needs_attention
        else "No educator action is required."
    )
    report = EducatorReport(
        learner_ref=request.learner_ref,
        progress=progress,
        needs_attention=needs_attention,
        note=note,
    )
    return CourseDeliveryResponse(
        learner_ref=request.learner_ref,
        lesson_title=request.lesson_title,
        lesson=lesson,
        deadline=request.deadline,
        educator_report=report,
    )
