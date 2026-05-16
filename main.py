import asyncio
import json
import os

os.environ.pop("SSLKEYLOGFILE", None)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from api_client import get_pokemon_data

global config
config = None
with open("settings.json") as f:
    config = json.load(f)
TOKEN = config["token"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Пришли мне имя покемона на английском!")

@dp.message()
async def send_pokemon(message: types.Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")

    pokemon = await get_pokemon_data(message.text)

    if not pokemon:
        await message.answer("❌ Такого покемона нет.")
        return

    evo_lines = []
    for stage in pokemon.evolution_chain:
        types_str = ", ".join(stage['types'])
        evo_lines.append(f"• *{stage['name']}* ({types_str})")
    evo_chain_text = "\n⬇️\n".join(evo_lines)

    caption = (
        f"👾 **{pokemon.name}**\n"
        f"🏠 Среда обитания: {pokemon.habitat}\n\n"
        f"🧬 **Цепочка эволюции:**\n{evo_chain_text}\n\n"
        f"{pokemon.description}"
    )

    await message.answer_photo(
        photo=pokemon.image_url,
        caption=caption,
        parse_mode="Markdown"
    )

async def main():
    print("Бот работает...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())