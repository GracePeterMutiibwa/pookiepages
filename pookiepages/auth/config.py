from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AuthConfig:
    mode: str = "account"
    loginPage: str = "/auth/login"
    redirectAfterLogin: str = "/"
    redirectAfterLogout: str = "/"
    allowedDomains: list[str] = field(default_factory=list)
    requireEmailVerification: bool = False


@dataclass
class SMTPConfig:
    host: str = ""
    port: int = 587
    user: str = ""
    password: str = ""
    useTLS: bool = True
    useSSL: bool = False
    defaultFrom: str = ""


@dataclass
class GoogleAuthConfig:
    clientId: str = ""
    clientSecret: str = ""
    allowedDomains: list[str] = field(default_factory=list)
    mode: str = "account"


@dataclass
class GithubAuthConfig:
    clientId: str = ""
    clientSecret: str = ""
    allowedDomains: list[str] = field(default_factory=list)
    mode: str = "account"
