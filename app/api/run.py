import re

def get_endpoint_names_from_scenario_result(test_scenario: str) -> str:
    if not test_scenario or not isinstance(test_scenario, str):
        raise TypeError("test_scenario must be a non-empty string")
    matches = re.findall(r'^testcase_(.*?):', test_scenario, re.MULTILINE)
    return "\n".join(matches)