from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import requests
import json
from typing import List, Dict
from ..prompts.prompts import FastApiPrompts

class OpenRouter:
    def __init__(self, api_key: str):
        pass

    def select_model(models):
        return inquirer.fuzzy(
            message="Select a model (fuzzy search):",
            choices=models,
            default=None,
        ).execute()

    #todo - add retry annotation
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

    #todo - add retry annotation
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

    def convert_scenarios_dict_to_list(scenarios_dict: Dict[str, Dict[str, str]]):
        formatted_scenarios = []
        for endpoint, content in scenarios_dict.items():
            parsed_info = content["parsed_open_api_string"]
            test_scenario = content["test_scenario"]
            relative_endpoints = content["relative_paths"]
            formatted_scenarios.append(
                {
                    "endpoint": endpoint,
                    "parsed_info": parsed_info,
                    "test_scenario": test_scenario,
                    "relative_paths": relative_endpoints
                })
        return formatted_scenarios

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

    def select_scenarios_to_run(scenarios: List[Dict[str, str]]) -> List[Dict[str, str]]:
        choices = [Choice(name=item["test_scenario"], value=item) for item in scenarios]
        return inquirer.checkbox(
            message="Select scenarios:",
            choices=choices,
            instruction="(Use space to select, enter to confirm)",
            validate=lambda result: len(result) > 0,
        ).execute()


    def user_selection_fuzzy(given_choices: List[str]):
        selected = inquirer.fuzzy(
            message="Select auth login endpoint [Optional]: (fuzzy search):",
            choices=given_choices,
            default=None,
        ).execute()
        return None if selected == "[None]" else selected

    def user_selection_checkbox(given_choices: List[str]):
        selected = inquirer.checkbox(
            message="Select auth register endpoint [Optional]: (fuzzy search):",
            choices=given_choices,
            default=None,
        ).execute()
        return None if selected == "[None]" else selected

    def get_relative_endpoints(endpoint_path:str, openapi_data: dict, api_key: str, open_router_model: str) -> List[str]:
        prompt = FastApiPrompts.semantic_endpoint_extraction_prompt + "\n\n" + "Endpoint : " + endpoint_path + "\n\n" + "OpenAPI Data: " + str(openapi_data)
        return OpenRouter.send_request_to_openrouter(api_key=api_key, model_name=open_router_model, prompt=prompt)