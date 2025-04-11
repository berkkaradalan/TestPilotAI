from typing import Optional
import keyring

def set_api_key(provider=str, api_key=str):
    if provider and api_key:
        keyring.set_password(provider, "api_key", api_key)
        return f"✅ API key for {provider} set successfully."
    else:
        return "⚠️ Provider and API key are required."
    
def get_api_key(provider: str) -> Optional[str]:
    if provider:
        api_key = keyring.get_password(provider, "api_key")
        return f"🔑 API key for {provider}: {api_key}" if api_key else "❌ No API key found."
    return "⚠️ Provider is required."

def delete_api_key(provider: str):
    if provider:
        existing = keyring.get_password(provider, "api_key")
        if existing:
            keyring.delete_password(provider, "api_key")
            return f"🗑️ API key for {provider} deleted successfully."
        else:
            return "❌ No API key found to delete."
    else:
        return "⚠️ Provider is required."

def set_default_provider(provider: str):
    if provider:
        keyring.set_password("default", "provider", provider)
        return f"✅ Default provider set to {provider}."
    else:
        return "⚠️ Provider is required to set default."

def get_default_provider():
    provider = keyring.get_password("default", "provider")
    if provider:
        return provider
    else:
        return "❌ No default provider set."

