from app.api.args import get_args, process_command_line_args

def main():
    parser, args = get_args()
    process_command_line_args(args, parser)

if __name__ == "__main__":
    main()
