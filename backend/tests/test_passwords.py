from backend.app.security.passwords import hash_password, verify_password

def test_password_hash_is_one_way():
    raw='TestPassword!2026'
    hashed=hash_password(raw)
    assert raw not in hashed
    assert hashed.startswith('$argon2id$')
    assert verify_password(raw,hashed)
    assert not verify_password('bad',hashed)
