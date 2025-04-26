from tqdm import tqdm
import sys
import argparse
import json
from app.config import api_key_utils
from app.api.run import read_json_file, validate_open_api, get_tree_output
from app.api.openrouter import get_openrouter_models, select_model, convert_scenarios_dict_to_list, select_scenarios_to_run, send_request_to_openrouter
from app.api.prompts import pytest_test_write_prompt
from app.api.parser import parse_open_api, get_auth_provider_endpoints
from app.api.test_runner import run_tests_safely

def get_args():
    parser = argparse.ArgumentParser(description='OpenRouter AI tool manager')
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    set_parser = subparsers.add_parser('set-apikey', help='Set OpenRouter API key')
    set_parser.add_argument('--api-key', required=True, help='Your OpenRouter API key')

    get_parser = subparsers.add_parser('get-apikey', help='Get OpenRouter API key')  # <-- EKLENDİ
    delete_parser = subparsers.add_parser('delete-apikey', help='Delete OpenRouter API key')  # <-- EKLENDİ

    run_parser = subparsers.add_parser('run', help='Parse OpenAPI file and generate test cases')
    run_parser.add_argument('--openapi-path', required=True, help='Path to OpenAPI spec file')
    run_parser.add_argument('--project-path', required=True, help='Path of your backend project')
    run_parser.add_argument('--save-as', required=True, help='Name of the file to save the test file ')

    args = parser.parse_args()
    return parser, args

def process_command_line_args(args:argparse.Namespace, parser:argparse.ArgumentParser):
    if args.command == 'set-apikey':
        print(api_key_utils.set_api_key(args.api_key))
    elif args.command == 'get-apikey':
        print(api_key_utils.get_api_key_for_user())
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
        if not api_key_utils.get_api_key():
            print("🚨 API key not set. Please set it using --set-apikey.")
            sys.exit(1)
        model_list = get_openrouter_models(api_key=api_key_utils.get_api_key())
        if not model_list:
            print("🚨🤖 OpenRouter Error: No models found.")
        else:
            chosen = select_model(model_list)
            print(f"\nSelected model: {chosen}")


        parsed_open_api_data = parse_open_api(openapi_data=openapi_file_data, api_key=api_key_utils.get_api_key(), open_router_models=chosen)
        test_scenarios = convert_scenarios_dict_to_list(scenarios_dict=json.loads(parsed_open_api_data))
        chosen_tests = select_scenarios_to_run(test_scenarios)
        auth_provider_endpoints = get_auth_provider_endpoints(openapi_data=openapi_file_data)
        for chosen_test in tqdm(chosen_tests, desc="🤖 Generating Test Code", unit="endpoint"):
        # for chosen_test in chosen_tests:
            test_prompt = pytest_test_write_prompt + "\n\n" + chosen_test["test_scenario"] + "\n\n" + "open api data of the project:\n" + chosen_test["parsed_info"] + "\n\n" +"tree struct of the project:\n" + get_tree_output(args.project_path, ignore_dirs=[".git", "__pycache__", ".idea", ".vscode", ".pytest_cache", ".mypy_cache"]) + "\n\n" + "auth_provider_endpoints" + "\n" + auth_provider_endpoints
            code_from_ai = send_request_to_openrouter(api_key=api_key_utils.get_api_key(), model_name=chosen, prompt=test_prompt)
            print(code_from_ai)
            run_tests_safely(test_code=code_from_ai, project_path=str(args.project_path))
            #todo - add another prompt for test packages
            # run_test_in_ephemeral_venv(test_code=code_from_ai, project_path=str(args.project_path))
            # run_tests_recursive(code=code_from_ai, project=str(args.project_path), retry=1000)
            
    else:
        parser.print_help()
