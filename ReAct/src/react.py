import logging
import re

from ReAct.src.llm_wrapper import LLM

class ReAct:

    def __init__(self, lm: LLM, tools) -> None:
        self.lm = lm
        self.tools = tools
        self.sysprompt = self._build_sysprompt(tools)

    def _build_sysprompt(self, tools: dict) -> str:
        skeleton = (
            "You will be given `question` and you will respond with `answer`.\n\n"
            "To do this, you will interleave Thought, Action, and Observation steps.\n\n"
            "Thought can reason about the current situation, and Action can be the following types:\n"
        )

        for i, (action_name, action_value) in enumerate(tools.items(), start=1):
            skeleton += f"({i}) {action_value.short_desc}, which {action_value.desc}. Example use: {action_value.example}\n"

        skeleton += (
            "---\n\n"
            "Follow the following format:\n\n"
            "Thought 1: Reasoning which action to take to solve the task.\n"
            "Action 1: Always either "
        )

        action_descriptions = " or ".join([f"{action_value.short_desc}" for _, action_value in tools.items()])
        skeleton += action_descriptions

        skeleton += (
            "\nObservation 1: result of Action 1\n"
            "Thought 2: next steps to take based on the previous Observation\n"
            "...\n"
            "until Action is of type Finish.\n\n"
            "---\n\n"
            "Question: "
        )

        return skeleton

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
        return f"{prompt}\n{response}\nObservation {i}:\n{obs}"

    def __call__(self, prompt, max_iters):
        prompt = f"{self.sysprompt} {prompt}"
        logging.debug(f"Prompt:\n###\n{prompt}\n###")
        for i in range(1, max_iters+1):
            response = self.lm.query_completions(prompt=prompt)
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