from __future__ import annotations
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
import httpx
from pookiepages.exceptions import PookiePagesError


VALID_PROVIDERS = ("brevo", "mailgun", "postmark", "resend", "sendgrid")


class SMTPEmailBackend:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        useTLS: bool = False,
        useSSL: bool = False,
        defaultFrom: str = "",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.useTLS = useTLS
        self.useSSL = useSSL
        self.defaultFrom = defaultFrom

    def send(self, to: str | list[str], subject: str, body: str, html: str | None = None, replyTo: str | None = None):
        recipients = [to] if isinstance(to, str) else to
        fromAddr = self.defaultFrom or self.user

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = fromAddr
        message["To"] = ", ".join(recipients)
        if replyTo:
            message["Reply-To"] = replyTo

        message.attach(MIMEText(body, "plain"))
        if html:
            message.attach(MIMEText(html, "html"))

        try:
            if self.useSSL:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                    server.login(self.user, self.password)
                    server.sendmail(fromAddr, recipients, message.as_string())
            elif self.useTLS:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    try:
                        server.login(self.user, self.password)
                    except smtplib.SMTPAuthenticationError as authErr:
                        raise PookiePagesError(
                            f"Email sending failed via SMTP at {self.host}:{self.port}. "
                            f"SMTP credentials were rejected by {self.host}: {authErr}. "
                            f"Check your SMTP username and password in your email config."
                        )
                    server.sendmail(fromAddr, recipients, message.as_string())
            else:
                with smtplib.SMTP(self.host, self.port) as server:
                    if self.user and self.password:
                        try:
                            server.login(self.user, self.password)
                        except smtplib.SMTPAuthenticationError as authErr:
                            raise PookiePagesError(
                                f"Email sending failed via SMTP at {self.host}:{self.port}. "
                                f"SMTP credentials were rejected by {self.host}: {authErr}. "
                                f"Check your SMTP username and password in your email config."
                            )
                    server.sendmail(fromAddr, recipients, message.as_string())

        except PookiePagesError:
            raise
        except (ConnectionRefusedError, OSError, TimeoutError) as connErr:
            raise PookiePagesError(
                f"Email sending failed via SMTP. "
                f"Could not connect to {self.host}:{self.port}: {connErr}. "
                f"Check that your SMTP host and port are correct and reachable."
            )
        except smtplib.SMTPRecipientsRefused as refusedErr:
            raise PookiePagesError(
                f"Email sending failed via SMTP at {self.host}:{self.port}. "
                f"Recipient address '{', '.join(recipients)}' was refused: {refusedErr}. "
                f"Verify the recipient address and your SMTP server's sending permissions."
            )
        except smtplib.SMTPException as smtpErr:
            raise PookiePagesError(
                f"Email sending failed via SMTP at {self.host}:{self.port}. "
                f"SMTP error: {smtpErr}. "
                f"Check your SMTP configuration and server logs."
            )


class ProviderEmailBackend:
    def __init__(
        self,
        provider: str,
        apiKey: str,
        defaultFrom: str,
        domain: str = "",
    ):
        providerNorm = provider.lower().strip()
        if providerNorm not in VALID_PROVIDERS:
            raise PookiePagesError(
                f"Email backend setup failed. "
                f"Unknown provider '{provider}'. "
                f"Valid providers are: {', '.join(VALID_PROVIDERS)}."
            )
        self.provider = providerNorm
        self.apiKey = apiKey
        self.defaultFrom = defaultFrom
        self.domain = domain

    async def send(self, to: str | list[str], subject: str, body: str, html: str | None = None, replyTo: str | None = None):
        recipients = [to] if isinstance(to, str) else to

        if self.provider == "brevo":
            await self._sendBrevo(recipients, subject, body, html, replyTo)
        elif self.provider == "mailgun":
            await self._sendMailgun(recipients, subject, body, html, replyTo)
        elif self.provider == "resend":
            await self._sendResend(recipients, subject, body, html, replyTo)
        elif self.provider == "postmark":
            await self._sendPostmark(recipients, subject, body, html, replyTo)
        elif self.provider == "sendgrid":
            await self._sendSendgrid(recipients, subject, body, html, replyTo)

    def _handleHttpError(self, response: httpx.Response, provider: str):
        statusCode = response.status_code
        if 400 <= statusCode < 500:
            raise PookiePagesError(
                f"Email sending failed via {provider}. "
                f"Provider returned {statusCode}: {response.text}. "
                f"Check your API key, sender address, and request payload."
            )
        if statusCode >= 500:
            raise PookiePagesError(
                f"Email sending failed via {provider}. "
                f"Provider returned {statusCode} (server error): {response.text}. "
                f"Check {provider}'s status page for outages."
            )

    def _handleConnError(self, error: Exception, provider: str):
        raise PookiePagesError(
            f"Email sending failed via {provider}. "
            f"The {provider} API endpoint was unreachable: {error}. "
            f"Check your network connection and {provider}'s service status."
        )

    async def _sendBrevo(self, recipients: list[str], subject: str, body: str, html: str | None, replyTo: str | None):
        payload: dict = {
            "sender": {"email": self.defaultFrom},
            "to": [{"email": addr} for addr in recipients],
            "subject": subject,
            "textContent": body,
        }
        if html:
            payload["htmlContent"] = html
        if replyTo:
            payload["replyTo"] = {"email": replyTo}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=payload,
                    headers={"api-key": self.apiKey, "Content-Type": "application/json"},
                    timeout=30,
                )
            if response.status_code not in (200, 201):
                self._handleHttpError(response, "Brevo")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            self._handleConnError(connErr, "Brevo")

    async def _sendMailgun(self, recipients: list[str], subject: str, body: str, html: str | None, replyTo: str | None):
        if not self.domain:
            raise PookiePagesError(
                "Email sending failed via Mailgun. "
                "Mailgun requires a domain. "
                "Set 'domain' in your ProviderEmailBackend config."
            )
        formData = {
            "from": self.defaultFrom,
            "to": ", ".join(recipients),
            "subject": subject,
            "text": body,
        }
        if html:
            formData["html"] = html
        if replyTo:
            formData["h:Reply-To"] = replyTo

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.mailgun.net/v3/{self.domain}/messages",
                    data=formData,
                    auth=("api", self.apiKey),
                    timeout=30,
                )
            if response.status_code not in (200, 201, 202):
                self._handleHttpError(response, "Mailgun")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            self._handleConnError(connErr, "Mailgun")

    async def _sendResend(self, recipients: list[str], subject: str, body: str, html: str | None, replyTo: str | None):
        payload: dict = {
            "from": self.defaultFrom,
            "to": recipients,
            "subject": subject,
            "text": body,
        }
        if html:
            payload["html"] = html
        if replyTo:
            payload["reply_to"] = replyTo

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.apiKey}", "Content-Type": "application/json"},
                    timeout=30,
                )
            if response.status_code not in (200, 201):
                self._handleHttpError(response, "Resend")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            self._handleConnError(connErr, "Resend")

    async def _sendPostmark(self, recipients: list[str], subject: str, body: str, html: str | None, replyTo: str | None):
        payload: dict = {
            "From": self.defaultFrom,
            "To": ", ".join(recipients),
            "Subject": subject,
            "TextBody": body,
        }
        if html:
            payload["HtmlBody"] = html
        if replyTo:
            payload["ReplyTo"] = replyTo

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.postmarkapp.com/email",
                    json=payload,
                    headers={"X-Postmark-Server-Token": self.apiKey, "Content-Type": "application/json"},
                    timeout=30,
                )
            if response.status_code not in (200, 201):
                self._handleHttpError(response, "Postmark")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            self._handleConnError(connErr, "Postmark")

    async def _sendSendgrid(self, recipients: list[str], subject: str, body: str, html: str | None, replyTo: str | None):
        payload: dict = {
            "personalizations": [{"to": [{"email": addr} for addr in recipients]}],
            "from": {"email": self.defaultFrom},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        }
        if html:
            payload["content"].append({"type": "text/html", "value": html})
        if replyTo:
            payload["reply_to"] = {"email": replyTo}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.apiKey}", "Content-Type": "application/json"},
                    timeout=30,
                )
            if response.status_code not in (200, 202):
                self._handleHttpError(response, "SendGrid")
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            self._handleConnError(connErr, "SendGrid")
