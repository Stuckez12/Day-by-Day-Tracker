from passlib.context import CryptContext

pwd_hash = CryptContext(["argon2", "bcrypt", "pbkdf2_sha512", "sha512_crypt"])
