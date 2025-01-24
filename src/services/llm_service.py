from typing import List, Dict, Any
import anthropic
from rich.console import Console

console = Console()

class LLMService:
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Client()
        self.model = model
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "python_interpreter",
                "description": "A tool that can execute python code",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The python code to execute",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "install_packages",
                "description": "A tool that can install python packages if you need to install new libraries",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "packages": {
                            "type": "array",
                            "description": "The python packages to install",
                        },
                    },
                },
            },
        ]

    def create_message(self, system_prompt: str, messages: List[Dict[str, str]]):
        with console.status("[bold blue]AI is thinking...", spinner="dots"):
            return self.client.messages.create(
                system=system_prompt,
                model=self.model,
                max_tokens=4096,
                tools=self.tools,
                messages=messages,
                stream=True,
            ) 