import glob
import asyncio
import json
import os

from slugify import slugify
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

def appendLorebookEntry(lorebook: definitions.lorebook, newEntries: list[dict]):
    allEntries = lorebook.entries

    allIds = [entry.id for entry in lorebook.entries]
    
    for entry in newEntries:
        # here, we define the name, content, tags, type, and aliases to be the minimum
        if not (entry.name and entry.content and entry.tags and entry.type and entry.aliases):
            raise ValueError("bruh")
            #/#/ NOT IMPLEMENTED YET: repairing lorebook entry written by llm

        entry = definitions.lorebookEntry.model_validate(entry)
        if not entry.id:
            entry.id = f"{entry.type}_{slugify(entry.name, separator='_')}_{uuid4().hex[:8]}"
                  
        allEntries.append(definitions.lorebookEntry.model_validate(entry))

    return lorebook

def nameAliasTypeTagLb(lorebook: definitions.lorebook):
    allEntries = lorebook.entries

    entryContent = [
        {
            "name": entry.name,
            "aliases": entry.aliases,
            "type": entry.type,
            "tags": entry.tags,
        }
        for entry in allEntries
    ]
    return json.dumps(entryContent, indent=2, ensure_ascii=False)

def contentById(lorebook: definitions.lorebook, ids: list[str]):
    allEntries = lorebook.entries

    entryContent = [
        {
            "name": entry.name,
            "content": entry.content
        }
        for entry in allEntries
        if entry.id in ids
    ]
    return json.dumps(entryContent, indent=2, ensure_ascii=False)

