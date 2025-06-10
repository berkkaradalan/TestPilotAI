# ⚙️ Preparing Your Test Environment for TestPilot AI
TestPilot AI is designed to generate and run automated tests within your existing project environment. It does not create or configure this environment for you. Understanding this is crucial for smooth operation.

## What You Need to Do

1-Set Up Your Python Virtual Environment

- Create and activate a virtual environment inside your project directory (commonly .venv).

- Install all your project’s dependencies inside this environment.

- This ensures that when TestPilot AI runs tests, it uses the exact same packages and versions your application relies on.

2-Start Any Required External Services

- If your application depends on services like databases (e.g., MongoDB, PostgreSQL), caches (e.g., Redis), message brokers (e.g., Kafka), or other APIs, make sure these services are running and accessible.

- This could mean starting Docker containers, running services locally, or using cloud-hosted resources.

- TestPilot AI does not manage these services or their lifecycle.

3-Provide Correct Paths When Running TestPilot AI When you run TestPilot AI, specify:

- --project-path — the root directory of your project where tests will run.

- --venv-path — the path to the virtual environment with installed dependencies.

Example Command

```bash
testpilotai run \
  --openapi /path/to/openapi.json \
  --save-as ./generated_tests.py \
  --project-path /path/to/your/project \
  --venv-path /path/to/your/project/.venv
```

## Important Notes
TestPilot AI assumes your environment is ready — it uses the provided virtual environment and any running services to execute and validate tests.

The tool is agnostic about how you set up this environment: Docker Compose, manual service start, cloud resources, or none at all — that choice is yours.

If your environment is missing dependencies or services, tests may fail to run or produce incorrect results.

Preparing a stable test environment is essential to leverage TestPilot AI's full power.

