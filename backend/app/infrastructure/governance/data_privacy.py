import re
from typing import Pattern


class DataPrivacyService:
    """
    Detects and masks sensitive data before AI calls.

    Sensitive patterns are detected with regular expressions
    and replaced with redaction placeholders so that PII and
    secrets are never sent to a model.
    """

    PATTERNS: dict[str, str] = {
        "email": (
            r"[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        ),
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": (
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}"
            r"[-\s]?\d{4}\b"
        ),
        "phone": (
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?"
            r"[-.\s]?\d{3}[-.\s]?\d{4}\b"
        ),
        "api_key": (
            r"\b(?:sk|pk|AKIA|AIza)[A-Za-z0-9_\-]{15,}\b"
        ),
        "ip_address": (
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ),
    }

    REDACTION_PLACEHOLDER = "[REDACTED]"

    def __init__(self) -> None:

        self._compiled: dict[str, Pattern[str]] = {
            name: re.compile(pattern)
            for name, pattern in self.PATTERNS.items()
        }

    def detect(
        self,
        text: str,
    ) -> dict[str, list[str]]:
        """
        Returns sensitive categories with their matches.
        """

        if not text:
            return {}

        found: dict[str, list[str]] = {}

        for name, pattern in self._compiled.items():

            matches = pattern.findall(text)

            if matches:
                found[name] = matches

        return found

    def mask(
        self,
        text: str,
    ) -> str:
        """
        Replaces all detected sensitive values with a
        redaction placeholder.
        """

        if not text:
            return text

        masked = text

        for pattern in self._compiled.values():
            masked = pattern.sub(
                self.REDACTION_PLACEHOLDER,
                masked,
            )

        return masked

    def mask_sensitive(
        self,
        text: str,
    ) -> tuple[str, dict[str, list[str]]]:
        """
        Returns (masked_text, detected) together.
        """

        detected = self.detect(text)

        return self.mask(text), detected
