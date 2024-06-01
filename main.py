import asyncio

from mihomo import Language, MihomoAPI
from card import create_card
from utils import get_config
import os

uid = input("Enter UID: ")
client = MihomoAPI(Language.EN)
config = get_config()

async def func():
    print(f"Fetching user data (UID: {int(uid)})...")
    data = await client.fetch_user(int(uid), replace_icon_name_with_url=True)

    print("")
    print(f"User: {data.player.name} ({data.player.uid})")
    print(f"Trailblaze Level: {data.player.level}")

    print("")
    print("Which character would you like to create a card for?")
    print("0: All characters")
    for i, ch in enumerate(data.characters):
        print(f"{i+1}: {ch.name}")

    print(f"{len(data.characters)+1}: Exit")

    x = int(input("Enter the number: "))
    if x < 0 or x > len(data.characters):
        print("Exiting...")
        return

    pth = os.path.join(config["cardsPath"], f"{data.player.uid}")
    os.makedirs(pth, exist_ok=True)

    if x == 0:
        for i, ch in enumerate(data.characters):
            img_url = input(f"Enter the URL of character image for {ch.name}'s card (leave blank or type 'n' if you want to use character preview): ")
            if not img_url or img_url.lower().strip() == "n": img_url = None

            print(f"Creating card for {ch.name}...")
            img = create_card(data, i)
            img.save(os.path.join(pth, f"{ch.name}.png"))
            print(f"Card for {ch.name} saved.")
    else:
        img_url = input("Enter the URL of character image for the card (leave blank or type 'n' if you want to use character preview): ")
        if not img_url or img_url.lower().strip() == "n": img_url = None

        print(f"Creating card for {data.characters[x-1].name}...")
        img = create_card(data, x-1, img_url)
        img.save(os.path.join(pth, f"{data.characters[x-1].name}.png"))
        print(f"Card for {data.characters[x-1].name} saved.")

asyncio.run(func())
