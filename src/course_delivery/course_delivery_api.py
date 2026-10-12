from fastapi import FastAPI

from .delivery_service import deliver_course
from .infrai_course_writer import InfraiCourseWriter
from .models import CourseDeliveryRequest, CourseDeliveryResponse

app = FastAPI(title="Private course delivery")


@app.post("/deliveries", response_model=CourseDeliveryResponse)
def create_delivery(request: CourseDeliveryRequest) -> CourseDeliveryResponse:
    return deliver_course(request, InfraiCourseWriter())
