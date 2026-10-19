import json
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
ICON_DIR = Root / "assets" / "game_icons"

#ICON_DIR.mkdir(parents=True, exist_ok= True)

with CONFIG_PATH.open("r", encoding="utf-8") as file:
    games = json.load(file)

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

            #replace existing icon only after new one is ready
            temp_Path.replace(icon_Path)




    except Exception as error:
        print (f"Failed to update {game_Name}: {error}")
    