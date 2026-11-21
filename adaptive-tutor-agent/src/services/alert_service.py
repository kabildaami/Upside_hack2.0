from datetime import datetime, timezone
from threading import Lock

from pydantic import BaseModel, Field


class SeriousAlert(BaseModel):
    alert_id: str
    student_id: str
    session_id: str
    reason: str
    created_at: str
    audiences: list[str] = Field(default_factory=lambda: ["parent", "school_counselor"])


class AlertService:
    def __init__(self):
        self._alerts: list[SeriousAlert] = []
        self._lock = Lock()

    def create_serious_alert(
        self,
        student_id: str,
        session_id: str,
        reason: str,
    ) -> SeriousAlert:
        alert = SeriousAlert(
            alert_id=f"{session_id}:{datetime.now(timezone.utc).timestamp()}",
            student_id=student_id,
            session_id=session_id,
            reason=reason,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._alerts.append(alert)
        print(
            f"SERIOUS-RISK ALERT | student={student_id} "
            f"session={session_id} audiences=parent,school_counselor"
        )
        return alert

    def list_for_student(self, student_id: str) -> list[SeriousAlert]:
        with self._lock:
            return [alert.model_copy(deep=True) for alert in self._alerts if alert.student_id == student_id]
