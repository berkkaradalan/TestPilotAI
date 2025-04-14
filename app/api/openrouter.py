from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import requests



def select_model(models):
    return inquirer.fuzzy(
        message="Select a model (fuzzy search):",
        choices=models,
        default=None,
    ).execute()

def get_openrouter_models(api_key: str):
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    models = data.get("data", [])
    model_ids = [model["id"] for model in models if "id" in model]
    return model_ids