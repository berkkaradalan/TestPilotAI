from api.args import get_args, process_command_line_args
import sys

def main():
    parser, args = get_args()
    process_command_line_args(args, parser)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited by user.")
        sys.exit(0)
