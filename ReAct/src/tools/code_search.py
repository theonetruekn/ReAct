import os
import ast
import logging

class CodebaseTool:
    name = "CodeSearch"
    desc = """
        searches the codebase for classes or functions specified in 'search_query'.
        Example use: CodeSearch(my_func(param1, param2)) or CodeSearch(Person(age, gender)).
        """

    def __init__(self, root):
        self.root = root

    def __call__(self, query):
        results = []
        name = query.split('(')[0].strip()
        logging.debug(f"Searching for '{name}' in {os.getcwd()}")
        for dirpath, dirnames, filenames in os.walk(self.root):
            for file in filenames:
                if file.endswith(".py"):
                    full_path = os.path.join(dirpath, file)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        try:
                            tree = ast.parse(content, filename=full_path)
                            for node in ast.walk(tree):
                                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name:
                                    code_segment = ast.get_source_segment(content, node)
                                    results.append(f"Found {node.name} in {full_path}:\n{code_segment}\n")
                        except SyntaxError as e:
                            print(f"Error parsing {file}: {e}")

        logging.debug(f"Result:\n###\n{results}\n###")
        if results == "":
            return "What you are seraching for does not exist."
        return "Result:".join(results)
