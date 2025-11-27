import secrets
from datetime import datetime, timedelta
from typing import Dict
from dataclasses import dataclass
from settings import settings
import pytz
from datetime import timezone

MOSCOW_TZ = pytz.timezone('Europe/Moscow')


@dataclass
class VerifyCode:
    code: int
    expires_at: datetime


class VerifyCodesStorage:
    """In-memory хранилище кодов верификации"""

    def __init__(self):
        self._codes: Dict[str, VerifyCode] = {}

    def put_code(self, email: str) -> int:
        """Сгенерировать и сохранить код. Возвращает код для отправки."""
        self._clear_expired()

        code = secrets.randbelow(900000) + 100000
        print(code)
        now_moscow = datetime.now(MOSCOW_TZ)

        self._codes[email] = VerifyCode(
            code=code,
            expires_at=now_moscow + timedelta(minutes=settings.VERIFY_CODE_EXPIRE)
        )
        return code

    def verify_code(self, email: str, code: int) -> bool:
        """Проверить код. Удаляет при успехе."""
        self._clear_expired()

        stored = self._codes.get(email)
        if not stored:
            return False

        if stored.code != code:
            return False

        del self._codes[email]
        return True

    def _clear_expired(self) -> None:
        """Очистить истекшие коды"""
        now = datetime.now(MOSCOW_TZ)

        expired = [email for email, vc in self._codes.items() if vc.expires_at < now]
        for email in expired:
            del self._codes[email]


codes_storage = VerifyCodesStorage()