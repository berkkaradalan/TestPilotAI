import keyring
from typing import Optional

SERVICE_NAME = "openrouter"

def set_api_key(api_key: str) -> str:
    keyring.set_password(SERVICE_NAME, "api_key", api_key)
    return " OpenRouter API key set successfully."

def get_api_key_for_user() -> Optional[str]:
    try:
        api_key = keyring.get_password(SERVICE_NAME, "api_key")
        return f"🔑 OpenRouter API key: {api_key}" if api_key else "❌ No API key found."
    except keyring.errors.InitError as e:
        return f"❌ Keyring backend failed to initialize: {e}"
    except keyring.errors.KeyringError as e:
        return f"❌ Keyring error occurred: {e}"
    except Exception as e:
        return f"❌ Unexpected error while retrieving API key: {e}"

def get_api_key() -> Optional[str]:
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    return api_key if api_key else None

def delete_api_key() -> str:
    try:
        existing = keyring.get_password(SERVICE_NAME, "api_key")
        if existing:
            keyring.delete_password(SERVICE_NAME, "api_key")
            return "🗑️ OpenRouter API key deleted successfully."
        return "❌ No API key found to delete."
    except keyring.errors.InitError as e:
        return f"❌ Keyring backend failed to initialize: {e}"
    except keyring.errors.KeyringError as e:
        return f"❌ Keyring error occurred: {e}"
    except Exception as e:
        return f"❌ Unexpected error while deleting API key: {e}"

def set_default_model(model: str) -> str:
    keyring.set_password(SERVICE_NAME, "default_model", model)
    return f"✅ Default model set to {model}."

def get_default_model() -> Optional[str]:
    model = keyring.get_password(SERVICE_NAME, "default_model")
    return f"🎯 Default model: {model}" if model else "❌ No default model set."

def check_api_key() -> bool:
    return keyring.get_password(SERVICE_NAME, "api_key")

def set_max_attempts(max_attempts: int) -> str:
    keyring.set_password(SERVICE_NAME, "max_attempts", str(max_attempts))
    return f"✅ Maximum attempts set to {max_attempts}."

def get_max_attempts() -> Optional[int]:
    max_attempts = keyring.get_password(SERVICE_NAME, "max_attempts")
    return int(max_attempts) if max_attempts else 10