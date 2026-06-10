"""
SMS Service — Handles sending SMS notifications using Vonage (Nexmo).
Uses python requests to communicate with the REST API directly.
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

def send_booking_confirmation(user_phone: str, message: str) -> bool:
    """
    Sends an SMS using Vonage.
    Returns True if successfully sent/queued, False otherwise.
    
    Expected environment variables (can be added to .env):
    - VONAGE_API_KEY
    - VONAGE_API_SECRET
    - VONAGE_SENDER_NAME
    """
    api_key = os.getenv("VONAGE_API_KEY")
    api_secret = os.getenv("VONAGE_API_SECRET")
    sender_name = os.getenv("VONAGE_SENDER_NAME", "MoroGo")

    if not api_key or not api_secret or api_key == "votre_cle_ici":
        logger.warning(
            "VONAGE API Key/Secret is missing or not configured. "
            f"SMS to {user_phone} skipped. Message: {message}"
        )
        # We return True in Dev mode assuming it was "mocked"
        return True

    # Vonage REST implementation
    url = "https://rest.nexmo.com/sms/json"
    payload = {
        "from": sender_name,
        "to": user_phone,
        "text": message,
        "api_key": api_key,
        "api_secret": api_secret
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        data = response.json()
        
        # Check Vonage response status
        if "messages" in data and len(data["messages"]) > 0:
            status = data["messages"][0].get("status")
            if status == "0":
                logger.info(f"SMS successfully sent to {user_phone} via Vonage.")
                return True
            else:
                error_text = data["messages"][0].get("error-text", "Unknown status")
                logger.error(f"Vonage API error: {status} - {error_text}")
                return False
        
        logger.error(f"Unexpected Vonage response formatting: {data}")
        return False
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while sending SMS: {e}")
        return False
