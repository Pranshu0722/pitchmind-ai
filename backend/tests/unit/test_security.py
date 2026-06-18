import pytest
from jose import JWTError

from pitchmind.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_roundtrip():
    plain = "SuperSecret1"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)


def test_verify_wrong_password():
    hashed = hash_password("CorrectPassword1")
    assert not verify_password("WrongPassword1", hashed)


def test_access_token_decode():
    token = create_access_token(user_id="abc-123", role="user")
    payload = decode_token(token)
    assert payload["sub"] == "abc-123"
    assert payload["type"] == "access"
    assert payload["role"] == "user"
    assert "jti" in payload
    assert "exp" in payload


def test_refresh_token_decode():
    token = create_refresh_token(user_id="abc-123")
    payload = decode_token(token)
    assert payload["sub"] == "abc-123"
    assert payload["type"] == "refresh"


def test_tampered_token_raises():
    token = create_access_token(user_id="abc-123", role="user")
    tampered = token[:-4] + "xxxx"
    with pytest.raises(JWTError):
        decode_token(tampered)


def test_access_and_refresh_tokens_are_different():
    uid = "abc-123"
    access = create_access_token(uid, "user")
    refresh = create_refresh_token(uid)
    assert access != refresh
