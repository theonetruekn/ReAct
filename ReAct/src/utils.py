import requests
import json

URL = 'http://localhost:11434/api/generate'

def query_completions(model, prompt, stream=False, options=None):
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if options is not None:
            data['options'] = options
        
        json_data = json.dumps(data)
        
        response = requests.post(URL, data=json_data, headers={'Content-Type': 'application/json'})
        
        return response.json()["response"]