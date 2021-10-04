from typing import List, Any, Optional
import aiosmtplib
from email.mime.multipart import MIMEMultipart


class Email:
    def __init__(self, host: str, port: int, tls: bool) -> None:
        self.host = host
        self.port = port
        self.is_tls = tls
        self.sender_email = None
        self.server = aiosmtplib.SMTP(hostname=host, port=port, use_tls=tls, timeout=30)

    async def login(self, email: str, password: str) -> None:
        await self.server.connect()
        if self.is_tls:
            await self.server.starttls()
        self.sender_email = email
        await self.server.login(username=email, password=password)

    async def send(
        self, email: str, subject: str, attachments: Optional[List[Any]]
    ) -> None:
        message_form = MIMEMultipart()
        message_form.preamble = subject
        message_form["Subject"] = subject
        message_form["From"] = self.sender_email
        message_form["To"] = email
        for attachment in attachments:
            message_form.attach(attachment)
        await self.server.send_message(message=message_form)

    async def close(self) -> None:
        await self.server.quit(timeout=30)
