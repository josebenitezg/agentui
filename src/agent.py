import json
from typing import List, Tuple
from rich.console import Console
from rich.prompt import Prompt
from services.llm_service import LLMService
from ui.layout_manager import LayoutManager
from code_executor import PythonInterpreter

console = Console()

class Agent:
    def __init__(self):
        self.llm_service = LLMService()
        self.python_interpreter = PythonInterpreter()
        self.layout_manager = LayoutManager()
        self.memory_layer = []
        self.system_prompt = open("prompts/system.prompt", "r").read()

    def process_llm_response(self, chunk) -> Tuple[str, str]:
        llm_message = ""
        json_response = ""
        current_code = None
        update_counter = 0  # To control refresh rate
        
        console.print(self.layout_manager.layout)  # Initial layout print
        
        for chunk in self.llm_service.create_message(self.system_prompt, self.memory_layer):
            if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                llm_message += chunk.delta.text
                update_counter += 1
                
                # Update typing message every few tokens to avoid flickering
                if update_counter % 3 == 0:  # Adjust this number to control update frequency
                    self.layout_manager.update_typing_message(llm_message, current_code)
                    console.print(self.layout_manager.layout)
                    
            elif hasattr(chunk, "delta") and hasattr(chunk.delta, "partial_json"):
                json_response += chunk.delta.partial_json
                
                try:
                    json_data = json.loads(json_response)
                    if "code" in json_data:
                        current_code = json_data["code"]
                        # Explicitly format the message with the code
                        formatted_message = f"{llm_message}\n```python\n{current_code}\n```"
                        self.layout_manager.update_typing_message(formatted_message)
                        console.print(self.layout_manager.layout)
                except json.JSONDecodeError:
                    pass
        
        # Finalize the message with code if present
        final_message = llm_message
        if current_code:
            final_message = f"{llm_message}\n```python\n{current_code}\n```"
        
        if final_message:
            self.layout_manager.finalize_message(final_message)
            console.print(self.layout_manager.layout)
        
        return final_message, json_response

    def handle_code_execution(self, code: str, llm_message: str) -> bool:
        # Start by showing "Executing code..." message immediately
        self.layout_manager.display_code_execution("", "", "Executing code...")
        console.print(self.layout_manager.layout)
        
        with console.status("[bold yellow]Executing code...", spinner="bouncingBar"):
            stdout, stderr, error = self.python_interpreter.execute(code)
        
        # Update with actual output
        self.layout_manager.display_code_execution(stdout, stderr, error)
        console.print(self.layout_manager.layout)
        
        # Simplify the execution output - no need for extra newlines if strings are empty
        execution_output = "\n".join(filter(None, [stdout, stderr, error]))
        
        self.memory_layer.append({
            "role": "assistant",
            "content": f"{llm_message}\nllm_generated_code: {code}\nexecution_output: {execution_output}"
        })
        
        return bool(error or stderr)

    def handle_package_installation(self, packages: List[str], llm_message: str):
        with console.status(f"[bold yellow]Installing packages: {', '.join(packages)}...", spinner="bouncingBar"):
            execution_output = self.python_interpreter.install_packages(packages)
        
        self.layout_manager.display_package_installation(execution_output)
        
        self.memory_layer.append({
            "role": "assistant",
            "content": f"{llm_message}\nPackages installed: {packages}\nexecution_output: {execution_output}"
        })

    def run(self):
        console.clear()
        console.print(self.layout_manager.layout)
        self.layout_manager.display_message("Welcome! I'm your AI assistant. Ask me anything!", is_user=False)
        
        while True:
            human_message = Prompt.ask("\n\nAsk me anything")
            self.layout_manager.display_message(human_message, is_user=True)
            self.memory_layer.append({"role": "user", "content": human_message})
            console.print(self.layout_manager.layout)
            
            while True: 
                llm_message, json_response = self.process_llm_response(None)
            
                if json_response:
                    response_data = json.loads(json_response)
                    
                    if "code" in response_data:
                        has_error = self.handle_code_execution(response_data["code"], llm_message)
                        if has_error:
                            self.memory_layer.append({
                                "role": "user",
                                "content": "There was an error. Please try to fix it."
                            })
                            continue
                    elif "packages" in response_data:
                        self.handle_package_installation(response_data["packages"], llm_message)
                        self.memory_layer.append({
                            "role": "user",
                            "content": "Great, now that the packages are installed, please continue with the original task."
                        })
                        continue
                
                self.memory_layer.append({"role": "assistant", "content": llm_message})
                break

if __name__ == "__main__":
    agent = Agent()
    agent.run()