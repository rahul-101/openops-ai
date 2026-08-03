from app.infrastructure.governance.data_privacy import (
    DataPrivacyService,
)


def test_detect_email():

    service = DataPrivacyService()

    found = service.detect("contact alice@example.com now")

    assert "email" in found
    assert "alice@example.com" in found["email"]


def test_detect_ssn():

    service = DataPrivacyService()

    found = service.detect("ssn is 123-45-6789")

    assert "ssn" in found
    assert "123-45-6789" in found["ssn"]


def test_detect_credit_card():

    service = DataPrivacyService()

    found = service.detect("card 4111 1111 1111 1111")

    assert "credit_card" in found


def test_detect_api_key():

    service = DataPrivacyService()

    found = service.detect("key sk-abcdefghijklmnopqrstuvwxyz")

    assert "api_key" in found


def test_detect_phone_and_ip():

    service = DataPrivacyService()

    found = service.detect(
        "call 555-123-4567 from 192.168.1.10"
    )

    assert "phone" in found
    assert "ip_address" in found


def test_detect_clean_text_returns_empty():

    service = DataPrivacyService()

    assert service.detect("nothing sensitive here") == {}


def test_mask_redacts_sensitive_values():

    service = DataPrivacyService()

    masked = service.mask(
        "email alice@example.com ssn 123-45-6789"
    )

    assert "alice@example.com" not in masked
    assert "123-45-6789" not in masked
    assert masked.count("[REDACTED]") == 2


def test_mask_empty_string():

    service = DataPrivacyService()

    assert service.mask("") == ""


def test_mask_sensitive_returns_tuple():

    service = DataPrivacyService()

    masked, detected = service.mask_sensitive(
        "contact bob@corp.io"
    )

    assert "bob@corp.io" not in masked
    assert detected["email"] == ["bob@corp.io"]


def test_mask_keeps_clean_text_unchanged():

    service = DataPrivacyService()

    text = "service is degrading on node-1"

    assert service.mask(text) == text
