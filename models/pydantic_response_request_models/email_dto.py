from pydantic import BaseModel, EmailStr


class SendCodeRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: int

class VerifyCodeResponse(BaseModel):
    """Ответ после проверки кода"""
    message: str
    verification_token: str
    expires_in_seconds: int
