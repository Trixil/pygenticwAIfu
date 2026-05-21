from fastapi import FastAPI, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import Request
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import os
import time
import glob
import json
from pathlib import Path
import shutil

try:
    from . import definitions, file_io
except ImportError:
    import definitions
    import file_io
    
def buildMessageHTML(role: str, content: str):
    if role == "user":
        classString = "user"
    elif role == "assistant":
        classString = "character"
    else:
        raise ValueError(f"Unknown message role: {role}")

    return f"""
        <div class="{classString}-chat-bubble">
            <p class="{classString}-message">{content}</p>
        </div>
    """