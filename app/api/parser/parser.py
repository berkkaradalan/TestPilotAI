import re
import ast
from api.openrouter.openrouter import OpenRouter
from api.prompts.prompts import FastApiPrompts
import json
from tqdm import tqdm
from typing import Optional, Dict, Any

class ParserFunctions:

    def request_body_schema_parser(openapi_data: dict, schema_ref: str) -> str:
        output = ""
        if not schema_ref or not schema_ref.startswith("#/components/schemas/"):
            return output
        
        schema_name = schema_ref.split("/")[-1]
        schema = openapi_data.get("components", {}).get("schemas", {}).get(schema_name, {})
        
        if "properties" not in schema:
            return f"     Unable to parse schema: {schema_name}\n"

        for prop_name, prop_info in schema["properties"].items():
            prop_type = prop_info.get("type", "Unknown")
            prop_title = prop_info.get("title", "")
            output += f"     Schema Item: {prop_name}\n"
            output += f"         Type: {prop_type}\n"
            if prop_title:
                output += f"         Title: {prop_title}\n"
        return output

    def parse_single_endpoint(openapi_data: dict,endpoint_name: str,) -> str:
        parsed_open_api_data = {}

        if "paths" not in openapi_data or endpoint_name not in openapi_data["paths"]:
            return json.dumps(parsed_open_api_data, indent=2)

        path = endpoint_name
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
                # parsed_open_api_string += f"    Request Body Schema: {request_schema_ref}\n"
                parsed_open_api_string += f"    Request Body Schema Ref:\n {ParserFunctions.request_body_schema_parser(openapi_data, request_schema_ref)}\n"
                parsed_open_api_string += f"    Request Body Schema:\n {ParserFunctions.request_body_schema_parser(openapi_data=openapi_data, schema_ref=request_schema_ref)}"
                # parsed_open_api_string += f"    Request Body Schema: {get_response_schema(openapi_data=openapi_data, schema_name=request_schema_ref.split("/")[-1])}\n"
            
            if 'security' in method_data:
                parsed_open_api_string += "    Security Requirements:\n"
                for security_req in method_data['security']:
                    for scheme_name, scopes in security_req.items():
                        parsed_open_api_string += f"      - Scheme: {scheme_name}, Scopes: {', '.join(scopes) if scopes else 'None'}\n"
            
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
                    parsed_open_api_string += ParserFunctions.get_response_schema(openapi_data=openapi_data, schema_name=ref.split("/")[-1])
            
            if 'parameters' in method_data:
                parsed_open_api_string += "    Parameters:\n"
                for param in method_data["parameters"]:
                    param_schema = param.get("schema", {})
                    param_type = param_schema.get("type", "Unknown type")
                    parsed_open_api_string += f"      - Name: {param['name']}, In: {param['in']}, Type: {param_type}\n"
            
            parsed_open_api_string += "\n"
        return parsed_open_api_string

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
                        parsed_open_api_string += ParserFunctions.get_response_schema(openapi_data=openapi_data, schema_name=ref.split("/")[-1])
                if 'parameters' in method_data:
                    parsed_open_api_string += "    Parameters:\n"
                    for param in method_data["parameters"]:
                        parsed_open_api_string += f"      - Name: {param['name']}, In: {param['in']}, Type: {param['schema']['type']}\n"
                parsed_open_api_string += "\n"

            parsed_string_prompt = FastApiPrompts.pytest_test_scenarios_prompt + "\n\n" + parsed_open_api_string
            test_scenario = OpenRouter.send_request_to_openrouter(
                api_key=api_key,
                model_name=open_router_models,
                prompt=parsed_string_prompt
            )

            parsed_open_api_data[path] = {
                "parsed_open_api_string": parsed_open_api_string,
                "test_scenario": test_scenario,
                "relative_paths": OpenRouter.get_relative_endpoints(endpoint_path=path, openapi_data=openapi_data, api_key=api_key, open_router_model=open_router_models),
            }

        json_output = json.dumps(parsed_open_api_data, indent=2)
        return json_output

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
                        ParserFunctions.get_response_schema(openapi_data=openapi_data, schema_name=anyof_item["items"]["$ref"].split("/")[-1])
                        schema_string += f"         Type: {anyof_item['items']['$ref']}\n"
                    schema_string += f"         Type: {anyof_item['type']}\n"
        return schema_string

    def find_auth_endpoint(openapi_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        security_schemes = openapi_spec.get('components', {}).get('securitySchemes', {})
        for scheme_name, scheme in security_schemes.items():
            if scheme.get('type') == 'oauth2':
                token_url = scheme.get('flows', {}).get('password', {}).get('tokenUrl', '')
                if token_url:
                    token_path = '/' + token_url.lstrip('/')
                    if token_path in openapi_spec.get('paths', {}):
                        method_data = openapi_spec['paths'][token_path].get('post', {})
                        return ParserFunctions.parse_endpoint_details(openapi_spec, token_path, 'post', method_data)

        login_keywords = {'login', 'token', 'auth', 'authenticate'}
        for path, methods in openapi_spec.get('paths', {}).items():
            for http_method, method_data in methods.items():
                if http_method.lower() == 'post':
                    summary = method_data.get('summary', '').lower()
                    if any(kw in summary for kw in login_keywords):
                        return ParserFunctions.parse_endpoint_details(openapi_spec, path, http_method, method_data)
                    
                    response_content = method_data.get('responses', {}).get('200', {}).get('content', {})
                    if 'application/json' in response_content:
                        schema_ref = response_content['application/json'].get('schema', {}).get('$ref', '')
                        if schema_ref:
                            schema_name = schema_ref.split('/')[-1]
                            schema_props = openapi_spec['components']['schemas'].get(schema_name, {}).get('properties', {})
                            if 'access_token' in schema_props:
                                return ParserFunctions.parse_endpoint_details(openapi_spec, path, http_method, method_data)
        return None

    def parse_endpoint_details(openapi_spec: Dict[str, Any], path: str, method: str, method_data: Dict[str, Any]) -> Dict[str, Any]:
        def get_response_schema_details(schema_name: str) -> str:
            schema = openapi_spec["components"]["schemas"].get(schema_name, {})
            details = []
            for prop, prop_details in schema.get("properties", {}).items():
                detail = f"  - {prop}:\n    Type: {prop_details.get('type', 'unknown')}"
                if 'title' in prop_details:
                    detail += f"\n    Title: {prop_details['title']}"
                details.append(detail)
            return "\n".join(details)

        details = {
            'path': path,
            'method': method.upper(),
            'summary': method_data.get('summary', 'No summary available'),
            'operationId': method_data.get('operationId', 'No operation ID'),
            'security': [],
            'parameters': [],
            'request_schema': None,
            'response_schema': None
        }

        for security_req in method_data.get('security', []):
            for scheme_name, scopes in security_req.items():
                details['security'].append({
                    'scheme': scheme_name,
                    'scopes': list(scopes) if scopes else None
                })

        if 'requestBody' in method_data:
            content = method_data['requestBody'].get('content', {})
            if 'application/json' in content:
                schema_ref = content['application/json'].get('schema', {}).get('$ref', '')
                if schema_ref:
                    details['request_schema'] = schema_ref.split('/')[-1]

        response = method_data.get('responses', {}).get('200', {})
        if 'content' in response and 'application/json' in response['content']:
            schema_ref = response['content']['application/json'].get('schema', {}).get('$ref', '')
            if schema_ref:
                schema_name = schema_ref.split('/')[-1]
                details['response_schema'] = {
                    'name': schema_name,
                    'properties': get_response_schema_details(schema_name)
                }

        for param in method_data.get('parameters', []):
            details['parameters'].append({
                'name': param.get('name'),
                'in': param.get('in'),
                'required': param.get('required', False),
                'type': param.get('schema', {}).get('type', 'unknown')
            })

        return details

    def parse_endpoint_names(openapi_data):
        return [endpoints for endpoints in openapi_data["paths"]]

    def parse_string_to_list(raw: str) -> list:
        if not raw or not isinstance(raw, str):
            relative_paths = []
        else:
            try:
                relative_paths = json.loads(raw)
            except json.JSONDecodeError:
                try:
                    relative_paths = ast.literal_eval(raw)
                except Exception:
                    relative_paths = []
        return relative_paths
    
    def get_endpoint_names_from_scenario_result(test_scenario: str) -> str:
        if not test_scenario or not isinstance(test_scenario, str):
            raise TypeError("test_scenario must be a non-empty string")
        matches = re.findall(r'^testcase_(.*?):', test_scenario, re.MULTILINE)
        return "\n".join(matches)