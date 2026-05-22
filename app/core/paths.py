from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"
PAGES_DIR = TEMPLATES_DIR / "pages"
REFERENCE_TEMPLATES_DIR = TEMPLATES_DIR / "reference"
DATA_DIR = APP_DIR / "data"
CHARACTERS_DIR = DATA_DIR / "characters"
LOADOUTS_DIR = DATA_DIR / "loadouts"
CHATS_DIR = DATA_DIR / "chats"
CHARACTER_DEFINITIONS_DIR = CHARACTERS_DIR / "definitions"
CHARACTER_IMAGES_DIR = CHARACTERS_DIR / "images"
LOADOUT_IMAGES_DIR = LOADOUTS_DIR / "images"
