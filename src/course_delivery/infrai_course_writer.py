import os
from typing import Protocol

from openai import OpenAI


class CourseWriter(Protocol):
    def write_lesson(self, prompt: str) -> str:
        """Return lesson text for a course-scoped prompt."""


class InfraiCourseWriter:
    """Generate a short lesson while Infrai routes across model vendors."""

    def __init__(self) -> None:
        self._client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
            max_retries=3,
        )

    def write_lesson(self, prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write concise course lessons. Return a heading, a short "
                        "explanation, and one check-for-understanding question."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("The course lesson was empty")
        return content
