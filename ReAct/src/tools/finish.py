class FinishTool:
    name = "Finish"
    
    desc = """returns the final `answer` and finishes the task. After calling this tool, you can stop generating."""
    
    example = """Finish[The Answer is 42]."""
    
    short_desc = """Finish[answer]"""
    
    def __init__(self) -> None:
        pass

    def __call__(self, answer:str) -> str:
        return answer