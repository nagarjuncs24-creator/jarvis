from uuid import uuid4

import pytest

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


def test_password_is_hashed_and_verifiable() -> None:
    hashed = hash_password("a-long-test-password")

    assert hashed != "a-long-test-password"
    assert verify_password("a-long-test-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_token_has_type_and_subject() -> None:
    user_id = uuid4()

    assert decode_token(create_access_token(user_id), "access") == user_id
    assert decode_token(create_refresh_token(user_id), "refresh") == user_id


def test_wrong_token_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        decode_token(create_refresh_token(uuid4()), "access")
