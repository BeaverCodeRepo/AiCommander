import json
import subprocess
import sys
from io import StringIO
from termcolor import colored
import openai


class Gpt4Instance:
    def __init__(self, instance_id, model, api_key, temperature, max_tokens, system_message=None):
        self.instance_id = instance_id
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messages = []
        self.pre_approved_executions = 0
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def chat_completion(self, message):
        print(colored("Sending message to GPT-4:", "white"), message)
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
        response_message = response.choices[0]['message']['content']
        self.messages.append({"role": "assistant", "content": response_message})
        print(colored(f"[{self.instance_id}]:", "magenta"), colored(response_message, "cyan"))
        return response_message

    def analyze_response(self, response):
        print(colored("Analyzing GPT-4 response:", "cyan"), response)
        try:
            json_data = json.loads(response)
            return json_data
        except json.JSONDecodeError:
            return None

    def execute_shell_command(self, command):
        print(colored("Executing shell command:", "yellow"), command)
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
        print(colored("Executing Python code:", "yellow"), code)
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
        user_input = input(f"Do you want to allow the Gpt4Instance ({self.instance_id}) to {action}? (yes, no, or a number to pre-approve): ")
        if user_input.isdigit():
            self.pre_approved_executions = int(user_input)
            return True
        return user_input.lower() == "yes"