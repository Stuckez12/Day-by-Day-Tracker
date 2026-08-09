from passlib.context import CryptContext


pwd_hash = CryptContext(["argon2", "bcrypt"])
