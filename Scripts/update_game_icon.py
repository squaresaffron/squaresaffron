import json
import sys
from io import BytesIO
from pathlib import Path
from google_play_scraper import app
import requests
from PIL import Image


Root = Path(__file__).resolve().parent.parent

print(Root, " this is root")

#loading game configuration 
#"/" isnt division, its pathlib.path class, joins two path components together
CONFIG_PATH = Root / "games.json"
ICON_DIR = Root / "Assets" / "game_icons"

ICON_DIR.mkdir(parents=True, exist_ok= True)

with CONFIG_PATH.open("r", encoding="utf-8") as file:
    games = json.load(file)

success_Count = 0
failed_Games = []

#fetching each game's metadata
for game in games:
    package_id = game["package_id"]
    game_Name = game["name"]

    #use the package ID to create the file name
    icon_Path = ICON_DIR / f"{package_id}.png"
    temp_Path = ICON_DIR / f"{package_id}_temp.png"

    try:
        print(f"Updating icon: {game_Name}")

        #fetch latest meta data
        details = app(package_id, lang="en", country="in")
        icon_URL = details["icon"]

        #download the icon
        response = requests.get(icon_URL, timeout=30)
        response.raise_for_status()

        #validate image and convert to png
        with Image.open(BytesIO(response.content)) as image:
            png_image = image.convert("RGBA")
            png_image.save(temp_Path, format="PNG")

            #replace existing icon only after new one is ready and its content is unchanged
            if icon_Path.exists() and temp_Path.read_bytes() == icon_Path.read_bytes():
                print(f"No Changes: {game_Name}")
                temp_Path.unlink()
            else:
                temp_Path.replace(icon_Path)
        
            success_Count += 1

    except Exception as error:
        failed_Games.append(game_Name)
        print (f"Failed to update {game_Name}: {error}")

    finally:
        #remove temporary files after outcome
        if temp_Path.exists():
            temp_Path.unlink()

    # A non zero exit code will tell automation that something failed
    if failed_Games:
        print("Failed games:", ", ".join(failed_Games))
        sys.exit(1)
    