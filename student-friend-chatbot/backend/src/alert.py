import os
import smtplib
from email.message import EmailMessage


async def _send(to: str | None, subject: str, body: str) -> str:
    if not to:
        return "no_contact"

    host = os.getenv("SMTP_HOST")
    if not host:
        print(f"[ALERT -> {to}] {subject}\n{body}")
        return "logged"

    message = EmailMessage()
    message["From"] = os.getenv("SMTP_FROM", "friendbot@example.com")
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as transport:
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASS")
        if user:
            transport.login(user, password or "")
        transport.send_message(message)
    return "sent"


async def alert_parent(student: dict) -> dict:
    body = (
        f"Bonjour,\n\nVotre enfant {student['name']} a peut-être besoin de soutien. "
        "Merci de lui parler aujourd'hui, avec calme et bienveillance.\n"
        "En cas de danger immédiat, contactez les services d'urgence.\n\nStudent Friend"
    )
    status = await _send(
        student.get("parent_email"),
        "Votre enfant a besoin de soutien",
        body,
    )
    counselor_email = os.getenv("COUNSELOR_EMAIL")
    if counselor_email:
        await _send(
            counselor_email,
            f"Alerte élève: {student['name']}",
            "Une alerte a été envoyée au parent. Merci de faire un suivi.",
        )
    return {"sentTo": student.get("parent_email"), "status": status}
