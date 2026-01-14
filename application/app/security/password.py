import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хешу.

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хешированный пароль из БД

    Returns:
        True если пароль соответствует хешу, иначе False
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Возвращает хеш пароля.

    Args:
        password: Пароль в открытом виде

    Returns:
        Хешированный пароль
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")
