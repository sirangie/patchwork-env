import pytest
from patchwork_env.encryptor import (
    encrypt_value,
    decrypt_value,
    is_encrypted,
    encrypt_env,
    decrypt_env,
)

PASS = "s3cr3t-passphrase"


def test_encrypt_produces_marker_prefix():
    token = encrypt_value("hello", PASS)
    assert token.startswith("enc:")


def test_round_trip_simple_value():
    original = "my_password_123"
    token = encrypt_value(original, PASS)
    assert decrypt_value(token, PASS) == original


def test_round_trip_empty_string():
    token = encrypt_value("", PASS)
    assert decrypt_value(token, PASS) == ""


def test_round_trip_long_value():
    original = "x" * 200
    assert decrypt_value(encrypt_value(original, PASS), PASS) == original


def test_wrong_passphrase_gives_garbage():
    token = encrypt_value("secret", PASS)
    result = decrypt_value(token, "wrong-pass")
    assert result != "secret"


def test_decrypt_non_token_raises():
    with pytest.raises(ValueError, match="Not an encrypted token"):
        decrypt_value("plaintext", PASS)


def test_is_encrypted_true():
    assert is_encrypted(encrypt_value("val", PASS))


def test_is_encrypted_false():
    assert not is_encrypted("plain_value")


def test_encrypt_env_all_keys():
    env = {"A": "alpha", "B": "beta"}
    result = encrypt_env(env, PASS)
    assert is_encrypted(result["A"])
    assert is_encrypted(result["B"])


def test_encrypt_env_selective_keys():
    env = {"SECRET": "s", "PUBLIC": "p"}
    result = encrypt_env(env, PASS, keys=["SECRET"])
    assert is_encrypted(result["SECRET"])
    assert result["PUBLIC"] == "p"


def test_encrypt_env_skips_already_encrypted():
    env = {"A": encrypt_value("already", PASS)}
    result = encrypt_env(env, PASS)
    assert result["A"] == env["A"]


def test_decrypt_env_round_trip():
    env = {"X": "foo", "Y": "bar"}
    encrypted = encrypt_env(env, PASS)
    decrypted = decrypt_env(encrypted, PASS)
    assert decrypted == env


def test_decrypt_env_leaves_plain_values():
    env = {"PLAIN": "no-encrypt"}
    assert decrypt_env(env, PASS) == env
