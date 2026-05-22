import os
from dotenv import load_dotenv

load_dotenv()

toyname = os.getenv("TOY_NAME", 8)
print(toyname)

toyuwu = os.getenv("TOY_UWU",2)
print(toyuwu)