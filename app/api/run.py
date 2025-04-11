import json
from openapi_schema_pydantic import OpenAPI

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

#todo
def parse_open_api(openapi_data: dict):
    openapi_schema = OpenAPI.parse_obj(openapi_data)
    for path, path_item in openapi_schema.paths.items():
        print(f"\nPATH: {path}")
        
        for method_name in ['get', 'post', 'put', 'delete', 'patch']:
            method = getattr(path_item, method_name, None)
            if not method:
                continue

            print(f"  METHOD: {method_name.upper()}")
            print(f"    TAGS: {method.tags}")
            print(f"    SUMMARY: {method.summary}")
            
            if method.requestBody:
                content = method.requestBody.content
                for content_type, media in content.items():
                    print(f"    REQUEST BODY:")
                    print(f"      Content-Type: {content_type}")
                    print(f"      Required: {method.requestBody.required}")
                    print(f"      Schema: {media.schema}")

            if method.parameters:
                print("    PARAMETERS:")
                for param in method.parameters:
                    print(f"      Name: {param.name}")
                    print(f"      In: {param.param_in}")
                    print(f"      Required: {param.required}")
                    print(f"      Schema: {param.schema}")
        
            print("    RESPONSES:")
            for code, response in method.responses.items():
                print(f"      Status Code: {code}")
                print(f"        Description: {response.description}")
                if response.content:
                    for content_type, media in response.content.items():
                        print(f"        Content-Type: {content_type}")
                        print(f"        Schema: {media.schema}")

            if method.security:
                print(f"    SECURITY:")
                for sec in method.security:
                    print(f"      {sec}")