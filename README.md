# 🧠 TestPilot AI
TestPilot AI is an AI-assisted automated test generation and repair tool. It reads your OpenAPI spec, generates endpoint-specific tests, runs them, and if they fail—fixes them using AI. Designed to be modular, it currently supports FastAPI + TestClient, but can be extended to other frameworks and languages.

## 📦 Features
- 🔍 Parses OpenAPI JSON to understand endpoint structure
- 🧪 Generates initial test cases (success/error scenarios)
- ⚙️ Runs tests automatically
- 🤖 Uses AI (via OpenRouter) to fix failing tests
- 🔁 Loops until all tests pass (or max retry)
- ⚙️ Framework-agnostic core

## 🚀 Getting Started
1. Install the tool
```bash
pip install .
```
>This installs the testpilotai CLI globally using the setup from setup.py.


2. Set your API key (OpenRouter/OpenAI)
```bash
testpilotai --set-api-key
```
>The key is stored securely using keyring.

3. Run the tool
```bash
testpilotai run \
  --openapi /path/to/openapi.json \
  --save-as ./test.py \
  --project-path /path/to/your/project \
  --venv-path /path/to/your/project/.venv
```

```
--openapi: Path to your OpenAPI JSON file
--save-as: Output test file path
--project-path: Target project root where tests will run
--venv-path: Path to the virtual environment to run tests in
```

## 🎯 To-Do
- [ ] implementation of other project environments
- [ ] implementation of other ai providers


## 🧩 Current Support
| Language | Framework | Test Tool | Status         |
| :-------- | :--------- | :--------- | :-------------- |
| `Python`   | `FastAPI`   | Fastapi-TestClient    | ✅ Supported    |


## 🤝 Contributing
Contributions are welcome! You can implement support for new frameworks by adding modules under:
```
prompts/{framework}.py

test_runner/{framework}.py
```
> Feel free to open issues, discuss ideas, or submit pull requests.

## ⚖️ License

This project is licensed under the [MIT License](./LICENSE).  
© 2025 Berk