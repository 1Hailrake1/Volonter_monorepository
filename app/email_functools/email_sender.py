import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import settings
from typing import Optional
from loguru import logger


class EmailSender:

    async def send_verification_code(
            self, email, code
    ) -> bool:
        subject = "Код верификации — Волонтёрская Платформа"

        # HTML версия письма
        html_body = f"""
               <!DOCTYPE html>
               <html>
               <head>
                   <meta charset="UTF-8">
                   <style>
                       body {{
                           font-family: Arial, sans-serif;
                           line-height: 1.6;
                           color: #333;
                       }}
                       .container {{
                           max-width: 600px;
                           margin: 0 auto;
                           padding: 20px;
                       }}
                       .header {{
                           background-color: #4CAF50;
                           color: white;
                           padding: 20px;
                           text-align: center;
                           border-radius: 5px 5px 0 0;
                       }}
                       .content {{
                           background-color: #f9f9f9;
                           padding: 30px;
                           border-radius: 0 0 5px 5px;
                       }}
                       .code {{
                           font-size: 32px;
                           font-weight: bold;
                           color: #4CAF50;
                           text-align: center;
                           padding: 20px;
                           background-color: #e8f5e9;
                           border-radius: 5px;
                           margin: 20px 0;
                           letter-spacing: 5px;
                       }}
                       .footer {{
                           text-align: center;
                           margin-top: 20px;
                           color: #666;
                           font-size: 14px;
                       }}
                   </style>
               </head>
               <body>
                   <div class="container">
                       <div class="header">
                           <h1>Волонтёрская Платформа</h1>
                       </div>
                       <div class="content">
                           <h2>Код верификации</h2>
                           <p>Здравствуйте!</p>
                           <p>Ваш код для подтверждения email:</p>

                           <div class="code">{code}</div>

                           <p>Код действителен в течение <strong>{settings.VERIFY_CODE_EXPIRE} минут</strong>.</p>

                           <p>Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>
                       </div>
                       <div class="footer">
                           <p>С уважением,<br>Команда Волонтёрской Платформы</p>
                           <p style="font-size: 12px; color: #999;">
                               Это автоматическое письмо, не отвечайте на него.
                           </p>
                       </div>
                   </div>
               </body>
               </html>
               """

        text_body = f"""
               Волонтёрская Платформа

               Код верификации: {code}

               Ваш код для подтверждения email: {code}

               Код действителен в течение {settings.VERIFY_CODE_EXPIRE} минут.

               Если вы не запрашивали этот код, просто проигнорируйте это письмо.

               С уважением,
               Команда Волонтёрской Платформы
               """

        return await self._send_email(
            to_email=email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )

    async def _send_email(
            self,
            to_email: str,
            subject: str,
            html_body: str,
            text_body: Optional[str] = None
    ) -> bool:
        """
        Отправить email (внутренний метод)

        Args:
            to_email: Email получателя
            subject: Тема письма
            html_body: HTML версия письма
            text_body: Текстовая версия (fallback)

        Returns:
            True если отправлено успешно
        """
        try:
            # Создаем multipart сообщение
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.SMTP_FROM} <{settings.SMTP_USER}>"
            message["To"] = to_email

            # Добавляем текстовую версию
            if text_body:
                text_part = MIMEText(text_body, "plain", "utf-8")
                message.attach(text_part)

            # Добавляем HTML версию
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)

            # Отправляем через SMTP
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )

            logger.info(f"📧 Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False


