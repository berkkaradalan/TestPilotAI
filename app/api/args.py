from tqdm import tqdm
import sys
import argparse
import json
from config import api_key_utils
from api.openrouter.openrouter import OpenRouter
from api.prompts.prompts import FastApiPrompts
from api.parser.parser import ParserFunctions
from api.test_runner.test_runner import FastAPITestRunner
from api.file_functions.file_functions import FileFunctions
from config.rich_console import rich_console

def get_args(): 
    parser = argparse.ArgumentParser(description='OpenRouter AI tool manager')
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    set_parser = subparsers.add_parser('set-apikey', help='Set OpenRouter API key')
    set_parser.add_argument('--api-key', required=True, help='Your OpenRouter API key')

    subparsers.add_parser('get-apikey', help='Get OpenRouter API key')
    subparsers.add_parser('delete-apikey', help='Delete OpenRouter API key')

    run_parser = subparsers.add_parser('run', help='Parse OpenAPI file and generate test cases')
    run_parser.add_argument('--openapi-path', required=True, help='Path to OpenAPI spec file')
    run_parser.add_argument('--project-path', required=True, help='Path of your backend project')
    run_parser.add_argument('--save-as', required=True, help='Name of the file to save the test file ')
    run_parser.add_argument('--venv-path', required=False, help='Path to your virtual environment (e.g. ./venv)')

    set_attempts_parser = subparsers.add_parser('set-max-attempts', help='Set the maximum number of attempts for test fix loop')
    set_attempts_parser.add_argument('--value', required=True, type=int, help='Maximum number of test fix attempts')

    subparsers.add_parser('get-max-attempts', help='Get the current maximum number of test fix attempts')

    args = parser.parse_args()
    return parser, args

def process_command_line_args(args:argparse.Namespace, parser:argparse.ArgumentParser):
    if args.command == 'set-apikey':
        rich_console.success_string(api_key_utils.set_api_key(args.api_key))
    elif args.command == 'get-apikey':
        rich_console.info_string(api_key_utils.get_api_key_for_user())
    elif args.command == 'delete-apikey':
        rich_console.success_string(api_key_utils.delete_api_key())
    elif args.command == 'set-max-attempts':
        rich_console.success_string(api_key_utils.set_max_attempts(args.value))
    elif args.command == 'get-max-attempts':
        rich_console.info_string(f"♻️ OpenRouter Max Attempts : {api_key_utils.get_max_attempts()}")

    elif args.command == 'run':
        python_venv = None
        if args.venv_path:
            python_venv = args.venv_path
        if not api_key_utils.check_api_key():
            rich_console.error_string("API key not set. Please set it using --set-apikey.")
            sys.exit(1)
        openapi_file_data = FileFunctions.read_json_file(args.openapi_path)
        if not FileFunctions.validate_open_api(openapi_file_data):
            rich_console.error_string("Invalid OpenAPI file")
            sys.exit(1)
        if not api_key_utils.get_api_key():
            rich_console.error_string("API key not set. Please set it using --set-apikey.")
            sys.exit(1)
        
        
        endpoints = ParserFunctions.parse_endpoint_names(openapi_data=openapi_file_data)
        auth_token_endpoint = OpenRouter.user_selection_fuzzy(given_choices=["[None]"]+endpoints)
        auth_token_endpoint_prompt = ("User gave this endpoint to get authentication token \n" + ParserFunctions.parse_single_endpoint(openapi_data=openapi_file_data, endpoint_name=auth_token_endpoint)) if auth_token_endpoint else ""
        rich_console.info_string(f"🔑 auth_token_endpoint: {auth_token_endpoint}")
        auth_register_endpoint = OpenRouter.user_selection_fuzzy(given_choices=["[None]"]+endpoints)
        auth_register_endpoint_prompt = ("User gave this endpoint to register. You don't have a test user instead you have to create one using this endpoint \n" + ParserFunctions.parse_single_endpoint(openapi_data=openapi_file_data, endpoint_name=auth_register_endpoint)) if auth_register_endpoint else ""
        rich_console.info_string(f"📋 auth_register_endpoint: {auth_register_endpoint}")
        
        model_list = OpenRouter.get_openrouter_models(api_key=api_key_utils.get_api_key())
        if not model_list:
            rich_console.error_string("🤖 OpenRouter Error: No models found.")
            sys.exit(1)
        else:
            chosen = OpenRouter.select_model(model_list)
            rich_console.model_selection_result(chosen)

        parsed_open_api_data = ParserFunctions.parse_open_api(openapi_data=openapi_file_data, api_key=api_key_utils.get_api_key(), open_router_models=chosen)
        test_scenarios = OpenRouter.convert_scenarios_dict_to_list(scenarios_dict=json.loads(parsed_open_api_data))
        
        chosen_tests = OpenRouter.select_scenarios_to_run(test_scenarios)        
        for chosen_test in tqdm(chosen_tests, desc="🤖 Generating Test Code", unit="endpoint"):
            relative_paths = ParserFunctions.parse_string_to_list(chosen_test["relative_paths"])

            if relative_paths:
                related_endpoints_parsed_data = "\n\nRelated Endpoints:\n"
                for relative_path in relative_paths:
                    related_endpoints_parsed_data += ParserFunctions.parse_single_endpoint(openapi_data=openapi_file_data, endpoint_name=relative_path)

            test_prompt = FastApiPrompts.pytest_test_write_prompt + "\n\nTest scenario:\n" + chosen_test["test_scenario"] + "\n\n" + "open api data of the project:\n" + chosen_test["parsed_info"] + "\n\n" +"tree struct of the project:\n" + FileFunctions.get_tree_output(args.project_path, ignore_dirs=[".git", "__pycache__", ".idea", ".vscode", ".pytest_cache", ".mypy_cache"]) + "\n\n" + "Auth token endpoint:\n" + "\n" + auth_token_endpoint_prompt + "\nAuth register endpoint:\n" + auth_register_endpoint_prompt + related_endpoints_parsed_data

            code_from_ai = OpenRouter.send_request_to_openrouter(api_key=api_key_utils.get_api_key(), model_name=chosen, prompt=test_prompt)
            test_runner_result =FastAPITestRunner. attempt_test_fix_loop(api_key=api_key_utils.get_api_key(),
                                                       model_name=chosen,
                                                       test_code=code_from_ai,
                                                       test_scenario=chosen_test["test_scenario"],
                                                       tree_struct=FileFunctions.get_tree_output(args.project_path, ignore_dirs=[".git", "__pycache__", ".idea", ".vscode", ".pytest_cache", ".mypy_cache"]),
                                                       project_path=str(args.project_path),
                                                       auth_token_endpoint_prompt=auth_token_endpoint_prompt,
                                                       auth_register_endpoint_prompt=auth_register_endpoint_prompt,
                                                       related_endpoints_prompt=related_endpoints_parsed_data,
                                                       max_attempts=api_key_utils.get_max_attempts(),
                                                       python_venv=python_venv)
            
            FileFunctions.append_test_code_to_file(test_code=str(test_runner_result), project_path=str(args.project_path), filename=args.save_as)
            
    else:
        parser.print_help()
