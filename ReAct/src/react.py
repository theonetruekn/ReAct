import logging
import re

from src.utils import query_completions

SYSPROMPT = """
You will be given `question` and you will respond with `answer`.

To do this, you will interleave Thought, Action, and Observation steps.

Thought can reason about the current situation, and Action can be the following types:

(1) CodeSearch[search_query], which 
        searches the codebase for classes or functions specified in 'search_query'. This includes all methods.
        Example use: CodeSearch[my_func(param1, param2)] or CodeSearch[SomeClass(param1, param2)].
        
(2) Finish[answer], which returns the final `answer` and finishes the task. After calling this tool, you can stop generating.

---

Follow the following format:

Thought 1: Reasoning which action to take to solve the task.
Action 1: always either CodeSearch[search_query] or, when done, Finish[answer]. Nothing else.
Observation 1: result of Action 1
Thought 2: next steps to take based on the previous Observation
...

until Action is of type Finish.

---

Question:
"""

class ReAct:

    def __init__(self, model, tools) -> None:
        self.model = model
        self.tools = tools

    def extract_action(self, response, i):
        pattern = rf"Action {i}: (\w+)\[(.*?)\]"
        
        actions = re.findall(pattern, response)
        
        if actions:
            return actions[-1]
        else:
            raise ValueError("No action found for the given index.")

    def clean_response(self, response, i):
        pattern = rf"Action {i}: \w+\[.*?]"
        
        matches = list(re.finditer(pattern, response))
        
        if not matches:
            raise ValueError("No action format found in the response.")
        
        last_match_end = matches[-1].end()
        
        return response[:last_match_end]

    def act(self, action_name, action_value):
        if action_name not in self.tools.keys():
            raise ValueError("Action does not exist!")
        
        return self.tools[action_name](action_value)

    def expand_prompt(self, prompt, response, obs, i):
        return f"{prompt}\n{response}\nObservation {i}:\n {obs}"

    def __call__(self, prompt, max_iters):
        prompt = f"{SYSPROMPT} {prompt}"
        logging.debug(f"Prompt:\n###\n{prompt}\n###")
        for i in range(1, max_iters+1):
            response = query_completions(model=self.model, prompt=prompt)
            logging.debug(f"Response:\n###\n{response}\n###")
            action_name, action_value = self.extract_action(response, i)
            if action_name == "Finish":
                return action_value
            try:
                obs = self.act(action_name=action_name, action_value=action_value)
                cleaned_response = self.clean_response(response, i)
                prompt = self.expand_prompt(prompt, cleaned_response, obs, i)
                logging.debug(f"New Prompt:\n###\n{prompt}\n###")
            except ValueError:
                logging.info("Something went wrong with the tool use. Trying again.")
        
        raise TimeoutError("The program did not terminate in the designated number of iterations.")

