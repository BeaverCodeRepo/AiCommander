import json
import subprocess
import sys
from io import StringIO

import openai


class Gpt4Instance:
    def __init__(self, model, api_key, temperature, max_tokens, system_message=None):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messages = []
        self.pre_approved_executions = 0
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def chat_completion(self, message):
        self.messages.append({"role": "user", "content": message})
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_tokens,
            n=1,
            stop=None,
            temperature=self.temperature,
        )
        response_message = response.choices[0].text.strip()
        self.messages.append({"role": "assistant", "content": response_message})
        return response_message

    def analyze_response(self, response):
        try:
            json_data = json.loads(response)
            return json_data
        except json.JSONDecodeError:
            return None

    def execute_shell_command(self, command):
        if self.pre_approved_executions > 0 or self.request_permission("execute a shell command"):
            if self.pre_approved_executions > 0:
                self.pre_approved_executions -= 1
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8')
            self.chat_completion(f"[OUTPUT]: {output}")
            return output, stderr.decode('utf-8')
        return "", ""

    def execute_python_code(self, code):
        if self.pre_approved_executions > 0 or self.request_permission("execute Python code"):
            if self.pre_approved_executions > 0:
                self.pre_approved_executions -= 1
            old_stdout = sys.stdout
            sys.stdout = output = StringIO()
            exec(code)
            sys.stdout = old_stdout
            output_str = output.getvalue()
            self.chat_completion(f"[OUTPUT]: {output_str}")
            return output_str

    def request_permission(self, action):
        user_input = input(f"Do you want to allow the Gpt4Instance to {action}? (yes, no, or a number to pre-approve): ")
        if user_input.isdigit():
            self.pre_approved_executions = int(user_input)
            return True
        return user_input.lower() == "yes"