import signal
import sys
from contextlib import contextmanager
from io import StringIO
import resource

class PythonInterpreter:
    def __init__(self, timeout_seconds: int = 10, memory_limit_mb: int = 100):
        self.timeout_seconds = timeout_seconds  
        self.memory_limit_mb = memory_limit_mb
        
    @contextmanager
    def _capture_output(self):
        """Capture stdout and stderr"""
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err
            
    def _set_resource_limits(self):
        """Set memory and CPU limits"""
        try:
            memory_bytes = self.memory_limit_mb * 1024 * 1024
            # Get the current soft and hard limits
            _, hard_limit = resource.getrlimit(resource.RLIMIT_AS)
            # Use the minimum of our desired limit and the system's hard limit
            memory_limit = min(memory_bytes, hard_limit)

            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, hard_limit))
        except Exception as e:
            # Continue execution without memory limits
            pass
    
    def execute(self, code: str) -> str:
        def handler(signum, frame):
            raise TimeoutError(f"Code execution timed out after {self.timeout_seconds} seconds")
        
        try:
            # Set up timeout
            
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(self.timeout_seconds)

            # Set up output capture and resource limits
            with self._capture_output() as (out, err):
                self._set_resource_limits()
                exec(code)
                
            return out.getvalue(), err.getvalue(), None

        except Exception as e:
            return "", "", e

        finally:
            signal.alarm(0)
    
    def install_packages(self, packages: list[str]) -> str:
        import subprocess
        results = []
        
        for package in packages:
            try:
                print(f"Installing package: {package}")
                result = subprocess.check_output(
                    [sys.executable, "-m", "pip", "install", package],
                    stderr=subprocess.STDOUT,
                    text=True
                )
                results.append(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                results.append(f"Failed to install package {package}: {e.output}")
                
        return "\n".join(results)
