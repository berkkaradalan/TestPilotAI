import argparse
from app.api.run import read_json_file, validate_open_api, parse_open_api
from app.config import api_key_utils
import sys

#todo
parser = argparse.ArgumentParser(description='AI API key manager')

subparsers = parser.add_subparsers(dest="command", help="Commands")

set_parser = subparsers.add_parser('set-apikey', help='Set API key for a provider')
set_parser.add_argument('--provider', required=True, help='AI Provider name (e.g., chatgpt, deepseek)')
set_parser.add_argument('--api-key', required=True, help='API key for the provider')

set_default_parser = subparsers.add_parser('set-default-provider', help='Set default provider for requests')
set_default_parser.add_argument('--provider', required=True, help='AI Provider name to set as default')

get_parser = subparsers.add_parser('get-apikey', help='Get API key for a provider')
get_parser.add_argument('--provider', required=True, help='AI Provider name to retrieve the key')

get_default_parser = subparsers.add_parser('get-default-apikey', help='Get the default API key for the default provider')

delete_parser = subparsers.add_parser('delete-apikey', help='Delete API key for a provider')
delete_parser.add_argument('--provider', required=True, help='AI Provider name to delete the key')

run_script_parser = subparsers.add_parser('run', help='Run the script')
run_script_parser.add_argument('--openapi-path', required=True, help='OpenAPI path to run the script')
run_script_parser.add_argument('--output-path', required=True, help='where to write the pytest file')

args = parser.parse_args()

if args.command == 'set-apikey':
    print(api_key_utils.set_api_key(args.provider, args.api_key))
elif args.command == 'set-default-provider':
    print(api_key_utils.set_default_provider(args.provider))
elif args.command == 'get-apikey':
    print(api_key_utils.get_api_key(args.provider))
elif args.command == 'get-default-apikey':
    print(api_key_utils.get_default_provider())
elif args.command == 'delete-apikey':
    print(api_key_utils.delete_api_key(args.provider))
elif args.command == 'run':
    openapi_file_data = read_json_file(args.openapi_path)
    if not validate_open_api(openapi_file_data):
        print("🚨 Invalid OpenAPI file") #todo
        sys.exit(1)
    parse_open_api(openapi_file_data)
else:
    parser.print_help()
