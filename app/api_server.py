from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import subprocess
from pathlib import Path
import sys
import tempfile
import os
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_execution.log')
    ]
)

app = FastAPI(
    title="Script Execution API",
    description="API for executing Python scripts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ExecutionResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

class CodeRequest(BaseModel):
    code: str

async def execute_script(script_path: str) -> ExecutionResponse:
    """
    Execute a Python script and return its output.
    
    Args:
        script_path (str): Path to the Python script to execute
        
    Returns:
        ExecutionResponse: Object containing execution results
    """
    try:
        # Verify the script exists
        script = Path(script_path)
        if not script.exists():
            return ExecutionResponse(
                success=False,
                error=f"Script not found: {script_path}"
            )
        
        # Execute the script using subprocess
        logging.info(f"Executing script: {script_path}")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logging.info("Script execution completed successfully")
            return ExecutionResponse(
                success=True,
                output=result.stdout
            )
        else:
            logging.error(f"Script execution failed with return code {result.returncode}")
            return ExecutionResponse(
                success=False,
                error=result.stderr
            )
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return ExecutionResponse(
            success=False,
            error=str(e)
        )

@app.post("/execute", response_model=ExecutionResponse)
async def execute_code_endpoint(code_request: CodeRequest) -> ExecutionResponse:
    """
    Endpoint to execute Python code sent as JSON.
    """
    # Create a temporary directory to store the script
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "script.py"
        
        # Save the code to a temporary file
        try:
            with open(temp_path, 'w') as f:
                f.write(code_request.code)
        except Exception as e:
            logging.error(f"Error saving code to file: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process code"
            )

        # Execute the script
        result = await execute_script(str(temp_path))
        return result

@app.post("/execute-file", response_model=ExecutionResponse)
async def execute_file_endpoint(script: UploadFile = File(...)) -> ExecutionResponse:
    """
    Endpoint to execute a Python script uploaded as a file.
    """
    if not script.filename.endswith('.py'):
        raise HTTPException(
            status_code=400,
            detail="Only Python files (.py) are allowed"
        )

    # Create a temporary directory to store the uploaded script
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / script.filename
        
        # Save the uploaded file
        try:
            contents = await script.read()
            with open(temp_path, 'wb') as f:
                f.write(contents)
        except Exception as e:
            logging.error(f"Error saving uploaded file: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process uploaded file"
            )

        # Execute the script
        result = await execute_script(str(temp_path))
        return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 