# Email

## SMTP

```python
from pookiepages.email.backends import SMTPEmailBackend
from pookiepages.email import configureEmail

configureEmail(SMTPEmailBackend(
    host="smtp.gmail.com",
    port=587,
    user="you@gmail.com",
    password="app-password",
    useTLS=True,
    defaultFrom="you@gmail.com",
))
```

## Provider (Brevo, Mailgun, Resend, Postmark, SendGrid)

```python
from pookiepages.email.backends import ProviderEmailBackend
from pookiepages.email import configureEmail

configureEmail(ProviderEmailBackend(
    provider="resend",
    apiKey="re_your_api_key",
    defaultFrom="noreply@yourapp.com",
))
```

Supported providers: `brevo`, `mailgun`, `postmark`, `resend`, `sendgrid`.

For Mailgun, also pass `domain="mg.yourapp.com"`.

## Send email

```python
from pookiepages.email import sendMail

await sendMail(
    to="user@example.com",
    subject="Welcome",
    body="Hello, welcome to our app.",
    html="<h1>Hello</h1><p>Welcome to our app.</p>",
    replyTo="support@yourapp.com",
)
```

## Error handling

All errors raise `PookiePagesError` with an actionable message that tells you what failed and what to check. For example:

```
Email sending failed via Resend. Provider returned 401: {"name":"missing_api_key"}.
Check your API key, sender address, and request payload.
```
