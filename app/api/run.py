import json
from typing import Optional, Dict, Any
from app.api.openrouter import get_openrouter_models, select_model

def read_json_file(file_path:str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"🚨 Error reading JSON file: {e}")
        return None    

def validate_open_api(openapi_data: dict) -> bool:
    try:
        return bool(openapi_data.get("openapi"))
    except KeyError:
        return False
    except AttributeError:
        return False
    except TypeError:
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
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



def parse_open_api(openapi_data: dict) -> None:
    parsed_open_api_string = """"""

    for path, methods in openapi_data["paths"].items():
        parsed_open_api_string += f"Path: {path}\n"

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
    return parsed_open_api_string
    
def parse_endpoints(openapi_data: dict) -> None:
    parsed_open_api_string = """"""
    for path, methods in openapi_data["paths"].items():
        parsed_open_api_string += f"Path: {path}\n"
        for method, method_data in methods.items():
            parsed_open_api_string += f"  Method: {method.upper()}\n"
            parsed_open_api_string += f"    Summary: {method_data.get('summary', 'No summary available')}"
    return parsed_open_api_string