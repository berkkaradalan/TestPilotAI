import keyring
from typing import Optional

SERVICE_NAME = "openrouter"

def set_api_key(api_key: str) -> str:
    keyring.set_password(SERVICE_NAME, "api_key", api_key)
    return "✅ OpenRouter API key set successfully."

def get_api_key_for_user() -> Optional[str]:
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    return f"🔑 OpenRouter API key: {api_key}" if api_key else "❌ No API key found."

def get_api_key() -> Optional[str]:
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    return api_key if api_key else None

def delete_api_key() -> str:
    existing = keyring.get_password(SERVICE_NAME, "api_key")
    if existing:
        keyring.delete_password(SERVICE_NAME, "api_key")
        return "🗑️ OpenRouter API key deleted successfully."
    return "❌ No API key found to delete."

def set_default_model(model: str) -> str:
    keyring.set_password(SERVICE_NAME, "default_model", model)
    return f"✅ Default model set to {model}."

def get_default_model() -> Optional[str]:
    model = keyring.get_password(SERVICE_NAME, "default_model")
    return f"🎯 Default model: {model}" if model else "❌ No default model set."

def check_api_key() -> bool:
    return keyring.get_password(SERVICE_NAME, "api_key")