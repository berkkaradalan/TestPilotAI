import argparse
import sys
from app.api.run import read_json_file, validate_open_api, parse_open_api, parse_endpoints
from app.api.prompts import pytest_test_scenarios_prompt
from app.api.openrouter import get_openrouter_models, select_model
from app.config import api_key_utils

parser = argparse.ArgumentParser(description='OpenRouter AI tool manager')

subparsers = parser.add_subparsers(dest="command", help="Available commands")

set_parser = subparsers.add_parser('set-apikey', help='Set OpenRouter API key')
set_parser.add_argument('--api-key', required=True, help='Your OpenRouter API key')

model_parser = subparsers.add_parser('set-default-model', help='Set default model for requests')
model_parser.add_argument('--model', required=True, help='Model name (e.g., mistral:latest)')

get_key_parser = subparsers.add_parser('get-apikey', help='Get current OpenRouter API key')

get_model_parser = subparsers.add_parser('get-default-model', help='Get default model name')

delete_parser = subparsers.add_parser('delete-apikey', help='Delete saved OpenRouter API key')

run_parser = subparsers.add_parser('run', help='Parse OpenAPI file and generate test cases')
run_parser.add_argument('--openapi-path', required=True, help='Path to OpenAPI spec file')
run_parser.add_argument('--output-path', required=True, help='Path to write pytest file')

args = parser.parse_args()

if args.command == 'set-apikey':
    print(api_key_utils.set_api_key(args.api_key))
elif args.command == 'set-default-model':
    print(api_key_utils.set_default_model(args.model))
elif args.command == 'get-apikey':
    print(api_key_utils.get_api_key_for_user())
elif args.command == 'get-default-model':
    print(api_key_utils.get_default_model())
elif args.command == 'delete-apikey':
    print(api_key_utils.delete_api_key())
elif args.command == 'run':
    if not api_key_utils.check_api_key():
        print("🚨 API key not set. Please set it using --set-apikey.")
        sys.exit(1)
    openapi_file_data = read_json_file(args.openapi_path)
    if not validate_open_api(openapi_file_data):
        print("🚨 Invalid OpenAPI file")
        sys.exit(1)
    open_router_models = get_openrouter_models(api_key=api_key_utils.get_api_key())
    if not api_key_utils.get_api_key():
        print("🚨 API key not set. Please set it using --set-apikey.")
        sys.exit(1)
    model_list = get_openrouter_models(api_key=api_key_utils.get_api_key())
    if not model_list:
        print("🚨🤖 OpenRouter Error: No models found.")
    else:
        chosen = select_model(model_list)
        print(f"\nSelected model: {chosen}")
    prompt = pytest_test_scenarios_prompt + "\n\n" + parse_endpoints(openapi_file_data)
    print(prompt)
else:
    parser.print_help()