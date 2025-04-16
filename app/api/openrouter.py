from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import requests
import json
from typing import List

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

def send_request_to_openrouter(api_key: str, model_name: str, prompt: str):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
      "Authorization": f"Bearer {api_key}",
    },
    data=json.dumps({
        "model": model_name,
        "messages": [
        {
            "role": "user",
            "content": prompt,
        }
        ]
    })
    )

    return response.json()['choices'][0]['message']['content']

def parse_scenarios(scenarioes:str):
    result = []
    buffer = []
    cleaned_scenarioes = scenarioes.strip().strip('`').strip()
    for line in cleaned_scenarioes.strip().splitlines():
        if line.startswith("testcase_"):
            if buffer:
                result.append("\n".join(buffer).strip())
                buffer = []
        buffer.append(line)
    if buffer:
        result.append("\n".join(buffer).strip())
    return result

def select_scenarios_to_run(scenarios: List[str]) -> List[str]:
    return inquirer.checkbox(
        message="Select scenarios:",
        choices=scenarios,
        instruction="(Use space to select, enter to confirm)",
        validate=lambda result: len(result) > 0,
    ).execute()