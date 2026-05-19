import asyncio
import json
import os
import random

os.environ.pop("SSLKEYLOGFILE", None)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from api_client import get_pokemon_data

global config
config = None
with open("settings.json") as f:
    config = json.load(f)
TOKEN = config["token"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

MAX_POKEMON_ID = 1025

def get_pokemon_keyboard(current_id: int) -> InlineKeyboardMarkup:
    prev_id = current_id - 1 if current_id > 1 else MAX_POKEMON_ID
    next_id = current_id + 1 if current_id < MAX_POKEMON_ID else 1

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="⬅️ Previous", callback_data=f"poke:{prev_id}"),
        InlineKeyboardButton(text="➡️ Next", callback_data=f"poke:{next_id}")
    )
    return builder.as_markup()

def build_pokemon_caption(pokemon) -> str:
    evo_lines = []
    for stage in pokemon.evolution_chain:
        types_str = ", ".join(stage['types'])
        evo_lines.append(f"• *{stage['name']}* ({types_str})")
    evo_chain_text = "\n⬇️\n".join(evo_lines)

    return (
        f"👾 **{pokemon.name}** (ID: {pokemon.id})\n"
        f"🏠 Среда обитания: {pokemon.habitat}\n\n"
        f"🧬 **Цепочка эволюции:**\n{evo_chain_text}\n\n"
        f"{pokemon.description}"
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Пришли мне имя покемона на английском или используй команду /random!")

@dp.message(Command("random"))
async def send_random_pokemon(message: types.Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")

    random_id = random.randint(1, MAX_POKEMON_ID)
    pokemon = await get_pokemon_data(random_id)

    if not pokemon:
        await message.answer("❌ Не удалось получить случайного покемона. Попробуй еще раз.")
        return

    caption = build_pokemon_caption(pokemon)
    await message.answer_photo(
        photo=pokemon.image_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=get_pokemon_keyboard(pokemon.id)
    )

@dp.message()
async def send_pokemon(message: types.Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")

    pokemon = await get_pokemon_data(message.text)

    if not pokemon:
        await message.answer("❌ Такого покемона нет.")
        return

    caption = build_pokemon_caption(pokemon)
    await message.answer_photo(
        photo=pokemon.image_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=get_pokemon_keyboard(pokemon.id)
    )

@dp.callback_query(lambda c: c.data and c.data.startswith("poke:"))
async def navigate_pokemon(callback_query: types.CallbackQuery):
    target_id = int(callback_query.data.split(":")[1])

    pokemon = await get_pokemon_data(target_id)
    if not pokemon:
        await callback_query.answer("❌ Ошибка при переключении.", show_alert=True)
        return

    caption = build_pokemon_caption(pokemon)

    media = InputMediaPhoto(media=pokemon.image_url, caption=caption, parse_mode="Markdown")

    await callback_query.message.edit_media(
        media=media,
        reply_markup=get_pokemon_keyboard(pokemon.id)
    )

    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())