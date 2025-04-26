from app.api.openrouter import send_request_to_openrouter
import json
from tqdm import tqdm
from typing import Optional, Dict, Any
from app.api.prompts import pytest_test_scenarios_prompt

def parse_open_api(openapi_data: dict, api_key: Optional[str] = None, open_router_models: Optional[str] = None) -> None:
    #todo - add api_key and open router model check method here
    parsed_open_api_data = {}

    for path in tqdm(openapi_data["paths"], desc="👷 Generating Test Scenarios", unit="endpoint"):
        methods = openapi_data["paths"][path]
        parsed_open_api_string = f"Path: {path}\n"

        for method, method_data in methods.items():
            parsed_open_api_string += f"  Method: {method.upper()}\n"
            parsed_open_api_string += f"    Summary: {method_data.get('summary', 'No summary available')}"
            parsed_open_api_string += f"\n    Operation ID: {method_data.get('operationId', 'No operation ID available')}\n"
            if 'requestBody' in method_data:
                request_schema_ref = (
                    method_data["requestBody"]
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                    .get("$ref")
                )
                parsed_open_api_string += f"    Request Body Schema: {request_schema_ref}\n"
            if 'security' in method_data:
                parsed_open_api_string += "    Security Requirements:\n"
                for security_req in method_data['security']:
                    for scheme_name, scopes in security_req.items():
                        parsed_open_api_string += f"      - Scheme: {scheme_name}, Scopes: {', '.join(scopes) if scopes else 'None'}\n"
            # Responses
            parsed_open_api_string += "    Responses:\n"
            for status_code, response in method_data.get("responses", {}).items():
                parsed_open_api_string += f"      {status_code}: {response.get('description', '')}\n"
                
                content = response.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})
                ref = schema.get("$ref")
                
                if ref:
                    parsed_open_api_string += f"        Response Schema Ref: {ref}\n"
                    parsed_open_api_string += f"        Response Schema:\n"
                    parsed_open_api_string += get_response_schema(openapi_data=openapi_data, schema_name=ref.split("/")[-1])
            if 'parameters' in method_data:
                parsed_open_api_string += "    Parameters:\n"
                for param in method_data["parameters"]:
                    parsed_open_api_string += f"      - Name: {param['name']}, In: {param['in']}, Type: {param['schema']['type']}\n"
            parsed_open_api_string += "\n"

        parsed_string_prompt = pytest_test_scenarios_prompt + "\n\n" + parsed_open_api_string
        test_scenario = send_request_to_openrouter(
            api_key=api_key,
            model_name=open_router_models,
            prompt=parsed_string_prompt
        )

        parsed_open_api_data[path] = {
            "parsed_open_api_string": parsed_open_api_string,
            "test_scenario": test_scenario
        }

    json_output = json.dumps(parsed_open_api_data, indent=2)
    return json_output

def parse_endpoints(openapi_data: dict) -> None:
    parsed_open_api_string = """"""
    for path, methods in openapi_data["paths"].items():
        parsed_open_api_string += f"Path: {path}\n"
        for method, method_data in methods.items():
            parsed_open_api_string += f"  Method: {method.upper()}\n"
            parsed_open_api_string += f"    Summary: {method_data.get('summary', 'No summary available')}"
    return parsed_open_api_string

def get_response_schema(openapi_data: dict, schema_name:str) -> Optional[Dict[str, Any]]:
    schema_data = openapi_data["components"]["schemas"].get(schema_name)
    schema_string = """"""
    for schema_item in schema_data["properties"]:
        schema_string += f"     Schema Item: {schema_item}\n"
        try:
            schema_string += f"         Type: {schema_data['properties'][schema_item]['type']}\n"
            schema_string += f"         Title: {schema_data['properties'][schema_item]['title']}\n"
        except KeyError:
            for anyof_item in schema_data["properties"][schema_item]["anyOf"]:
                if "items" in anyof_item:
                    get_response_schema(openapi_data=openapi_data, schema_name=anyof_item["items"]["$ref"].split("/")[-1])
                    schema_string += f"         Type: {anyof_item['items']['$ref']}\n"
                schema_string += f"         Type: {anyof_item['type']}\n"
    return schema_string

def get_auth_provider_endpoints(openapi_data: dict):
    keywords = ["login", "token", "auth", "signin", "register"]
    provider_endpoints = ""

    for path, path_item in openapi_data.get("paths", {}).items():
        for method, method_spec in path_item.items():
            if not isinstance(method_spec, dict):
                continue

            if method.upper() != "POST":
                continue

            if "security" in method_spec and method_spec["security"]:
                continue

            operation_id = method_spec.get("operationId", "").lower()
            path_lower = path.lower()

            if any(keyword in operation_id or keyword in path_lower for keyword in keywords):
                provider_endpoints += f"{method.upper()} {path}\n"
    return provider_endpoints
