import sys
import configparser
from termcolor import colored
from gpt4_instance import Gpt4Instance


class AICommander:
    def __init__(self, model, api_key, temperature, max_tokens):
        self.commander = Gpt4Instance(model, api_key, temperature, max_tokens, system_message="You are the commander AI.")
        self.task_instances = []

    def process_goal(self, goal):
        print(colored("Analyzing user goal:", "green"), goal)
        task_list_response = self.commander.chat_completion(f"Create a list of tasks for the following goal: {goal}")
        task_list = self.parse_task_list(task_list_response)

        for task in task_list:
            system_msg = f"Your task is: {task}"
            print(colored("Creating a new GPT-4 instance with system message:", "green"), system_msg)
            task_instance = Gpt4Instance(self.commander.model, self.commander.api_key, self.commander.temperature, self.commander.max_tokens, system_message=system_msg)
            self.task_instances.append(task_instance)
            task_response = task_instance.chat_completion(task)
            print(f"Task: {task}\nResponse: {task_response}\n")

    def parse_task_list(self, response):
        task_list = response.split('\n')
        return [task.strip() for task in task_list if task.strip()]
    
def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    model = "gpt-4"
    api_key = config.get("AICommander", "api_key")
    temperature = config.getfloat("AICommander", "temperature")
    max_tokens = config.getint("AICommander", "max_tokens")

    ai_commander = AICommander(model, api_key, temperature, max_tokens)

    while True:
        try:
            goal = input("Enter your goal: ")
            ai_commander.process_goal(goal)
        except KeyboardInterrupt:
            print("\nExiting AICommander.")
            sys.exit()

if __name__ == "__main__":
    main()