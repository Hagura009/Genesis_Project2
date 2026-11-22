import os
import uuid
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "clave-temporal-insegura-cambia-en-env",
)


class PasswordClass:
    @staticmethod
    def createPw(pw: str) -> str:
        salt = bcrypt.gensalt()
        pw_bytes = pw.encode("utf-8")
        hashed = bcrypt.hashpw(pw_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def checkPw(pw_source: str, pw_target: str | bytes) -> bool:
        pw_bytes = pw_source.encode("utf-8")
        target_bytes = (
            pw_target.encode("utf-8") if isinstance(pw_target, str) else pw_target
        )
        return bcrypt.checkpw(pw_bytes, target_bytes)

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())


PW = PasswordClass()