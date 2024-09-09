import pytest
from unittest.mock import Mock
import re
from ReAct.src.react import ReAct

def mock_query_completions(model, prompt):
    responses = {
        1: "Thought 1: We need to check the status.\nAction 1: CodeSearch[status]\nObservation 1: Status is OK.",
        2: "Thought 2: We should finish the task.\nAction 2: Finish[result]",
    }
    return responses[len(re.findall(r'Observation', prompt)) + 1]

class CodeSearch:
    name = "CodeSearch"
    desc = """searches the codebase for a class or a function, specified as search_query in CodeSearch[search_query]. Returns the source code."""
    example = """CodeSearch[my_func(param1, param2)] for searching a function or CodeSearch[SomeClass()] for searching a class."""
    short_desc = """CodeSearch[search_query]"""

tools = {
    "CodeSearch": Mock(short_desc="CodeSearch[search_query]", desc="searches the codebase for a class or a function", example="CodeSearch[search_query]"),
    "Finish": Mock(short_desc="Finish", desc="finishes the process", example="Finish[result]"),
}

@pytest.fixture
def react():
    model = Mock()
    return ReAct(model, tools)

def test_build_sysprompt(react):
    sysprompt = react._build_sysprompt(tools)
    assert "CodeSearch" in sysprompt
    assert "Finish" in sysprompt

def test_extract_action(react):
    response = ("Thought 1: We need to check the status.\n"
            "Action 1: CodeSearch[status]\n"
            "Observation 1: Status is OK.\n"
            "Thought 2: Now, we need to finish the task"
            "Action 2: Finish[The process is running]")
    action_name, action_value = react.extract_action(response, 1)
    assert action_name == "CodeSearch"
    assert action_value == "status"
    action_name, action_value = react.extract_action(response, 2)
    assert action_name == "Finish"
    assert action_value == "The process is running"


def test_clean_response(react):
    response = "Thought 1: We need to check the status.\nAction 1: CodeSearch[status]\nObservation 1: Status is OK."
    cleaned_response = react.clean_response(response, 1)
    assert cleaned_response == "Thought 1: We need to check the status.\nAction 1: CodeSearch[status]"

def test_act(react):
    tools["CodeSearch"].return_value = "Status is OK."
    obs = react.act("CodeSearch", "status")
    assert obs == "Status is OK."

def test_expand_prompt(react):
    prompt = "Initial prompt"
    response = "Thought 1: We need to check the status.\nAction 1: CodeSearch[status]"
    obs = "Status is OK."
    expanded_prompt = react.expand_prompt(prompt, response, obs, 1)
    expected_prompt = f"{prompt}\nThought 1: We need to check the status.\nAction 1: CodeSearch[status]\nObservation 1:\nStatus is OK."
    assert expanded_prompt == expected_prompt