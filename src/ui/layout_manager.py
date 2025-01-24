from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box

console = Console()

class LayoutManager:
    def __init__(self):
        self.layout = self._setup_layout()
        self.current_typing_panel = None

    def _setup_layout(self) -> Layout:
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        layout["body"].split_row(
            Layout(name="chat", ratio=1),
            Layout(name="output", ratio=1)
        )
        
        layout["header"].update(
            Panel(
                Text("🤖 TUI AI Agent", justify="center", style="bold blue"),
                box=box.DOUBLE,
                style="blue"
            )
        )
        
        layout["chat"].update(Panel(Group(), title="Chat", box=box.ROUNDED))
        layout["output"].update(Panel(Group(), title="Execution Output", box=box.ROUNDED))
        
        return layout

    def display_message(self, content: str, is_user: bool = False):
        panel = Panel(
            Markdown(content),
            title="You" if is_user else "🤖 AI Agent",
            style="green" if is_user else "blue",
            box=box.ROUNDED
        )
        
        chat_content = self.layout["chat"].renderable.renderable
        if isinstance(chat_content, Group):
            chat_content.renderables.append(panel)
        else:
            chat_content = Group(panel)
        
        self.layout["chat"].update(Panel(chat_content, title="Chat", box=box.ROUNDED))

    def display_code_execution(self, stdout: str, stderr: str, error: str):
        output_content = []
        
        # If we have stdout, show it immediately
        if stdout:
            output_content.append(Panel(
                Syntax(stdout, "python", theme="monokai", line_numbers=True),
                title="Output",
                style="bright_green",
                box=box.ROUNDED
            ))
        
        # Combine stderr and error into a single panel if either exists
        error_text = "\n".join(filter(None, [stderr, error]))
        if error_text:
            output_content.append(Panel(
                Text(error_text, style="red"),
                title="Error",
                style="red",
                box=box.ROUNDED
            ))
        
        # If no content, show a waiting message
        if not output_content:
            output_content.append(Panel(
                Text("Waiting for execution output..."),
                style="yellow",
                box=box.ROUNDED
            ))
        
        self.layout["output"].update(Panel(
            Group(*output_content), 
            title="Execution Output", 
            box=box.ROUNDED
        ))

    def display_package_installation(self, execution_output: str):
        output_content = Panel(
            Text(execution_output),
            title="Package Installation",
            style="yellow",
            box=box.ROUNDED
        )
        
        current_output = self.layout["output"].renderable.renderable
        if isinstance(current_output, Group):
            current_output.renderables.append(output_content)
        else:
            current_output = Group(output_content)
            
        self.layout["output"].update(Panel(current_output, title="Execution Output", box=box.ROUNDED))

    def update_typing_message(self, content: str, code: str = None):
        """Updates the current typing message or creates a new one"""
        if code:
            content = f"{content}\n```python\n{code}\n```"
            
        panel = Panel(
            Markdown(content),
            title="🤖 AI Agent (typing...)",
            style="blue",
            box=box.ROUNDED
        )
        
        chat_content = self.layout["chat"].renderable.renderable
        if not isinstance(chat_content, Group):
            chat_content = Group()
            
        # Remove previous typing panel if it exists
        if self.current_typing_panel and self.current_typing_panel in chat_content.renderables:
            chat_content.renderables.remove(self.current_typing_panel)
            
        # Add new typing panel
        self.current_typing_panel = panel
        chat_content.renderables.append(panel)
        
        self.layout["chat"].update(Panel(chat_content, title="Chat", box=box.ROUNDED))

    def finalize_message(self, content: str):
        """Replaces typing message with final message"""
        chat_content = self.layout["chat"].renderable.renderable
        if not isinstance(chat_content, Group):
            chat_content = Group()
            
        # Remove typing panel if it exists
        if self.current_typing_panel and self.current_typing_panel in chat_content.renderables:
            chat_content.renderables.remove(self.current_typing_panel)
        
        # Add final message
        panel = Panel(
            Markdown(content),
            title="🤖 AI Agent",
            style="blue",
            box=box.ROUNDED
        )
        chat_content.renderables.append(panel)
        
        self.layout["chat"].update(Panel(chat_content, title="Chat", box=box.ROUNDED))
        self.current_typing_panel = None 