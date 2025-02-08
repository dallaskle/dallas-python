#!/usr/bin/env python3

import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('script_execution.log')
    ]
)

def execute_script(script_path: str) -> Optional[str]:
    """
    Execute a Python script and return its output.
    
    Args:
        script_path (str): Path to the Python script to execute
        
    Returns:
        Optional[str]: Output of the script if successful, None if failed
    """
    try:
        # Verify the script exists
        script = Path(script_path)
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Execute the script using subprocess
        logging.info(f"Executing script: {script_path}")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        logging.info("Script execution completed successfully")
        return result.stdout
    
    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Script execution failed with return code {e.returncode}")
        logging.error(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python script_executor.py <path_to_script>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    output = execute_script(script_path)
    
    if output is not None:
        print("Script Output:")
        print(output)
    else:
        sys.exit(1) 