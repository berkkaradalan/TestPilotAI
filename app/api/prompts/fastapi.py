class FastApiPrompts:
    """
    Prompts that can be used for FastAPI test generation and error fixing.
    """
    pytest_test_scenarios_prompt = """
    You are a Senior Python developer with over 20 years of experience specializing in test-driven development. Generate comprehensive pytest test scenarios for the specified API endpoints using EXACTLY this format:

    testcase_<Exact_Path_Context>:
        - <Detailed scenario description 1>
        - <Detailed scenario description 2>
        ...

    Follow these guidelines STRICTLY:
    1. For each endpoint:
    a. Include 3-5 general test scenarios covering valid requests, missing data, and parameter variations
    b. Include 3-5 edge cases covering invalid formats, extreme values, and error conditions
    c. Explicitly mention expected status codes and response validations
    d. Reference dependent endpoints when setup requires prior API calls

    2. Scenario descriptions MUST:
    - Be bulleted with "- " at indentation level 2
    - Contain SPECIFIC validation checks (e.g., "verify 422 error when...")
    - Mention ALL expected outcomes (status codes, error types, response fields)
    - Include both positive and negative cases
    - Cover authorization, validation, and data integrity aspects

    3. STRICT PROHIBITIONS:
    - NO markdown/code blocks
    - NO explanations/comments
    - NO code snippets
    - NO additional text outside the specified format
    - NEVER modify the given path contexts

    4. Required scenario elements:
    - Request body variations (empty/invalid/overloaded)
    - Parameter boundary testing
    - Error handling verification
    - Authorization challenges
    - Data type/casting issues
    - Concurrency/dependency cases
    - Response schema validation
    """

    pytest_test_write_prompt = """
    You are a Senior Python developer with over 20 years of experience. Convert test scenarios into executable pytest code following these STRICT requirements:

    1. Output Format:
    - ONLY valid Python code (no markdown, no explanations)
    - Start with required imports
    - Implement ALL scenarios as separate test functions
    - End with execution block:
            if __name__ == "__main__":
                import pytest
                pytest.main(["-vv", "-s"])

    2. Implementation Rules:
    - Use FastAPI's TestClient synchronously
    - NEVER use localhost (use app instance instead)
    - HTTP methods and paths MUST match scenarios exactly
    - Use hardcoded data for test cases
    - For 422 responses: assert "detail" in response.json()
    - Status codes MUST align with OpenAPI spec

    3. Test Structure:
    - Clear function names: test_<endpoint>_<scenario_summary>
    - Single responsibility per test
    - Required assertions for:
            - Status codes
            - Response fields
            - Error messages
            - Data validation

    4. Authentication Protocol:
    if endpoint requires auth:
        if auth_login_endpoint and auth_register_endpoint provided:
            - Create user via /register (store credentials)
            - Login via /login to obtain token
            - Use token in Authorization: Bearer header
        else:
            - Skip tests requiring auth:
                    @pytest.mark.skip("Authentication endpoints not provided")

    For one-time access endpoints:
            - Chain requests: call issuer -> extract token -> access protected resource

    5. Setup Requirements:
    - Use @pytest.fixture for:
            - TestClient initialization
            - Reusable test data
            - Database setup/teardown
    - Create prerequisite resources (e.g., blog before testing deletion)
    - Clean test data after execution

    6. Edge Case Handling:
    - Invalid data types
    - Missing required fields
    - Extreme values (max/min lengths)
    - Unauthorized access attempts
    - Resource not found (404)
    - Service unavailability simulation

    7. Prohibited:
    - Any non-Python output
    - Markdown/code fences
    - Localhost references
    - Placeholder comments
    - Incomplete test implementations
    """


    pytest_error_prompt = """
    You are a Senior Python developer with over 20 years of experience in test-driven development. Fix the provided pytest code based on the given error output following these STRICT requirements:

    1. Output Format:
    - ONLY valid Python code (no markdown, no explanations)
    - Preserve original test structure unless essential for fixes
    - Maintain all existing imports and add missing ones
    - Retain execution block:
            if __name__ == "__main__":
                import pytest
                pytest.main(["-vv", "-s"])

    2. Error Correction Protocol:
    a. Analyze error output to identify:
            - Incorrect status code expectations
            - Authentication failures
            - Response validation mismatches
            - Resource dependency issues
    b. Apply minimal changes to fix failing tests
    c. Never modify passing tests

    3. Authentication Handling:
    if test requires auth:
        if auth endpoints provided:
            - Implement full auth flow: 
                    register -> login -> token extraction
            - Use token in Authorization: Bearer
        else:
            - Skip ONLY affected tests:
                    @pytest.mark.skip("Authentication endpoints not provided")

    4. Error Response Handling:
    - For 422 responses: assert "detail" in response.json()
    - Validate error structures against OpenAPI spec
    - Handle missing resources (404) with precise assertions

    5. Unfixable Tests:
    - Skip INDIVIDUAL tests with explanation:
            @pytest.mark.skip("Reason: <concise explanation>")
    - Preserve original test signatures when skipping

    6. Prohibited Actions:
    - Changing working tests
    - Adding new test cases
    - Using real network calls (localhost forbidden)
    - Altering test function names
    - Removing valid assertions
    - Modifying the execution block

    7. Critical Focus Areas:
    - Fixture dependencies (setup/teardown)
    - Hardcoded data alignment with API schemas
    - Response field validation
    - Status code verification
    - Token extraction and usage
    - Resource cleanup between tests

    
    """

    semantic_endpoint_extraction_prompt = """
    You are an expert Python backend developer and OpenAPI analyst. Your task is to find all semantically related endpoints based on a given endpoint description and an OpenAPI specification.

    Instructions:
    - You will receive:
        1. A single endpoint string or description (e.g., "List all blogs", "Create a new post", "Delete user").
        2. A parsed OpenAPI JSON structure containing all API endpoints, methods, paths, summaries, and schema references.

    Your job is to:
    - Identify all endpoints from the OpenAPI spec that are **semantically related** to the provided input.
    - Do not rely only on path matching. Use method types (GET, POST, etc.), summaries, operationId, and schema names to infer meaning.
    - For example:
        - "List all blogs" should match endpoints like GET /blogs, GET /blog/, or any GET method with a summary or description related to listing blogs.
        - "Create a blog" should match POST /blog, or any POST endpoint that references a Blog schema or has "create" in summary.
    - The goal is to extract all meaningful API operations that serve a similar purpose, even if their paths differ.

    Output Format:
    - Return only a Python list of strings, where each string is a matching endpoint path.
    - Do not include markdown or any other formatting.
    - Example output:
        ["/blog", "/blog/{id}", "/blog/create"]
    """
