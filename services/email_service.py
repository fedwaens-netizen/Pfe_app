import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SENDER_NAME = os.getenv("SMTP_SENDER_NAME", "MoroGo")


def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Envoie un code OTP par email à l'utilisateur.
    Retourne True si succès, False sinon.
    """
    if not SMTP_USER or not SMTP_PASS:
        # En mode développement : affiche l'OTP dans les logs
        logger.warning(
            f"[DEV MODE] SMTP non configuré. OTP pour {to_email} : {otp}"
        )
        # On retourne True pour ne pas bloquer le flux en dev
        return True

    subject = "MoroGo – Code de réinitialisation de mot de passe"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
      <div style="max-width: 480px; margin: auto; background: white; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h2 style="color: #2563eb; margin-top: 0;">🌍 MoroGo</h2>
        <p style="color: #333;">Bonjour,</p>
        <p style="color: #333;">Vous avez demandé à réinitialiser votre mot de passe. Voici votre code de vérification :</p>
        <div style="text-align: center; margin: 28px 0;">
          <span style="
            display: inline-block;
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            color: #2563eb;
            background: #eff6ff;
            border-radius: 10px;
            padding: 16px 32px;
          ">{otp}</span>
        </div>
        <p style="color: #666; font-size: 14px;">Ce code expire dans <strong>10 minutes</strong>.</p>
        <p style="color: #666; font-size: 14px;">Si vous n'avez pas fait cette demande, ignorez cet email.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
        <p style="color: #aaa; font-size: 12px; text-align: center;">© 2026 MoroGo – Votre guide touristique au Maroc</p>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        logger.info(f"OTP email envoyé avec succès à {to_email}")
        return True
    except Exception as e:
        logger.error(f"Échec de l'envoi de l'email OTP à {to_email}: {e}")
        return False
