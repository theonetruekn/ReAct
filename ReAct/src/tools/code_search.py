import os
import ast
import logging

class CodeSearch:
    name = "CodeSearch"
    
    desc = f"searches the codebase for a class or a function, specified as search_query in {name}[search_query]. Returns the source code."
    
    example = f"{name}[my_func(param1, param2)] for searching a function or {name}[SomeClass()] for searching a class."
    
    short_desc = f"{name}[search_query]"

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
