from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ProgressState(StrEnum):
    ON_TRACK = "on_track"
    DUE = "due"
    OVERDUE = "overdue"


class CourseDeliveryRequest(BaseModel):
    learner_ref: str = Field(min_length=1, description="Opaque learner identifier")
    course_title: str = Field(min_length=1)
    lesson_title: str = Field(min_length=1)
    learning_objective: str = Field(min_length=1)
    deadline: datetime
    observed_at: datetime
    completed: bool = False


class EducatorReport(BaseModel):
    learner_ref: str
    progress: ProgressState
    needs_attention: bool
    note: str


class CourseDeliveryResponse(BaseModel):
    learner_ref: str
    lesson_title: str
    lesson: str
    deadline: datetime
    educator_report: EducatorReport
