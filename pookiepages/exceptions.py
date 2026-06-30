class PookiePagesError(Exception):
    """Base exception for all pookiepages framework errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message
