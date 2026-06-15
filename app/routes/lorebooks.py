import glob
import asyncio
import json
import os

from openai import OpenAI
from openai import AsyncOpenAI
from openai import APIError, APIConnectionError, RateLimitError, BadRequestError
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi import Request
from enum import Enum
from uuid import uuid4

from ..core.paths import CHATS_DIR, CHARACTER_IMAGES_DIR, TEMPLATES_DIR
from ..models import definitions
from ..rendering import htmlHelpers
from ..storage import file_io
from ..utils.normalize import normalize
from dotenv import load_dotenv

router = APIRouter()

def createBaseLorebook():
    return {"version": 1, "entries": []}

