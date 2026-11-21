import { useEffect, useRef } from "react";

export default function useTelemetry(studentId, sessionId) {
  const started = useRef(Date.now());

  useEffect(() => {
    return () => {
      const elapsedMinutes = (Date.now() - started.current) / 60000;
      fetch("http://localhost:8000/chat/telemetry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          session_id: sessionId,
          elapsed_minutes: elapsedMinutes,
          hints_used: 0,
          mistakes: 0,
        }),
      }).catch(() => {});
    };
  }, [studentId, sessionId]);
}
