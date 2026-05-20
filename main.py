import asyncio
import json
import os
import random

import httpx

os.environ.pop("SSLKEYLOGFILE", None)

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardMarkup, \
    KeyboardButton, BufferedInputFile
from api_client import get_pokemon_data

global config
config = None
with open("settings.json") as f:
    config = json.load(f)
TOKEN = config["token"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

MAX_POKEMON_ID = 1025

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎲 Случайный покемон")],
            [KeyboardButton(text="🔍 Как пользоваться ботом?")]
        ],
        resize_keyboard=True,
        persistent=True
    )

def get_pokemon_keyboard(current_id: int, has_audio: bool) -> InlineKeyboardMarkup:
    prev_id = current_id - 1 if current_id > 1 else MAX_POKEMON_ID
    next_id = current_id + 1 if current_id < MAX_POKEMON_ID else 1

    builder = InlineKeyboardBuilder()

    if has_audio:
        builder.row(InlineKeyboardButton(text="🔊 Слушать голос", callback_data=f"cry:{current_id}"))

    builder.row(
        InlineKeyboardButton(text="⬅️ Пред.", callback_data=f"poke:{prev_id}"),
        InlineKeyboardButton(text="След. ➡️", callback_data=f"poke:{next_id}")
    )
    return builder.as_markup()

def build_pokemon_caption(pokemon) -> str:
    stats_lines = []
    for stat_name, value in pokemon.stats.items():
        bar_length = min(int((value / 255) * 10), 10)
        bar = "🟩" * bar_length + "⬜" * (10 - bar_length)
        stats_lines.append(f"`{stat_name:<7}: {value:<3}` {bar}")
    stats_text = "\n".join(stats_lines)

    types_text = ", ".join(pokemon.types)
    abilities_text = ", ".join(pokemon.abilities)

    evo_lines = []
    for stage in pokemon.evolution_chain:
        stage_types = ", ".join(stage['types']).title()
        evo_lines.append(f"• {stage['name']} ({stage_types})")
    evo_chain_text = "\n⬇️\n".join(evo_lines) if evo_lines else "Нет эволюции"

    return (
        f"👾 **{pokemon.name}** (ID: {pokemon.id})\n"
        f"🌪 **Тип:** {types_text}\n"
        f"📏 **Рост:** {pokemon.height} м | ⚖️ **Вес:** {pokemon.weight} кг\n"
        f"🌟 **Базовый опыт:** {pokemon.base_exp}\n"
        f"🏠 **Обитание:** {pokemon.habitat}\n\n"
        f"💪 **Способности:** {abilities_text}\n\n"
        f"📊 **Характеристики:**\n{stats_text}\n\n"
        f"🧬 **Цепочка эволюции:**\n{evo_chain_text}\n\n"
        f"📖 _{pokemon.description}_"
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Я PokéBot ⚡\n\n"
        "Просто напиши мне имя любого покемона на английском (например: *Pikachu*, *Charizard*, *Mewtwo*), "
        "и я найду всю информацию о нем!\n\n"
        "Или нажми кнопку ниже, чтобы испытать удачу.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "🎲 Случайный покемон")
async def btn_random_pokemon(message: types.Message):
    await send_random_pokemon(message)

@dp.message(F.text == "🔍 Как пользоваться ботом?")
async def btn_help(message: types.Message):
    text = (
        "📖 **Справка**\n\n"
        "1️⃣ **Поиск по имени:** Напиши имя (например, `Eevee`).\n"
        "2️⃣ **Поиск по ID:** Напиши номер из покедекса (например, `133`).\n"
        "3️⃣ **Навигация:** Используй кнопки ⬅️ и ➡️ под картинкой, чтобы листать покедекс!\n\n"
        "⚠️ _Имена нужно писать на английском языке._"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🎲 Случайный покемон")
@dp.message(Command("random"))
async def send_random_pokemon(message: types.Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")
    random_id = random.randint(1, MAX_POKEMON_ID)
    pokemon = await get_pokemon_data(random_id)

    if not pokemon:
        await message.answer("❌ Ошибка получения данных.")
        return

    await message.answer_photo(
        photo=pokemon.image_url,
        caption=build_pokemon_caption(pokemon),
        parse_mode="Markdown",
        reply_markup=get_pokemon_keyboard(pokemon.id, bool(pokemon.audio_url))
    )

@dp.message()
async def send_pokemon(message: types.Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")
    pokemon = await get_pokemon_data(message.text)

    if not pokemon:
        await message.answer("❌ Такого покемона нет.")
        return

    await message.answer_photo(
        photo=pokemon.image_url,
        caption=build_pokemon_caption(pokemon),
        parse_mode="Markdown",
        reply_markup=get_pokemon_keyboard(pokemon.id, bool(pokemon.audio_url))
    )

@dp.callback_query(lambda c: c.data and c.data.startswith("poke:"))
async def navigate_pokemon(callback_query: types.CallbackQuery):
    target_id = int(callback_query.data.split(":")[1])
    pokemon = await get_pokemon_data(target_id)

    if not pokemon:
        await callback_query.answer("❌ Ошибка.", show_alert=True)
        return

    media = InputMediaPhoto(
        media=pokemon.image_url,
        caption=build_pokemon_caption(pokemon),
        parse_mode="Markdown"
    )

    await callback_query.message.edit_media(
        media=media,
        reply_markup=get_pokemon_keyboard(pokemon.id, bool(pokemon.audio_url))
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("cry:"))
async def send_pokemon_cry(callback_query: types.CallbackQuery):
    target_id = int(callback_query.data.split(":")[1])
    pokemon = await get_pokemon_data(target_id)

    if pokemon and pokemon.audio_url:
        await callback_query.answer("🎙 Загружаю голосовое...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(pokemon.audio_url)
                if response.status_code != 200:
                    raise Exception("Не удалось скачать файл")
                audio_bytes = response.content

            voice_file = BufferedInputFile(audio_bytes, filename="voice.ogg")

            await bot.send_voice(
                chat_id=callback_query.message.chat.id,
                voice=voice_file,
                caption=f"🗣 Голос **{pokemon.name}**",
                parse_mode="Markdown"
            )

        except Exception as e:
            print(f"Ошибка загрузки звука: {e}")
            await callback_query.message.answer("❌ Не удалось отправить голос покемона.")
    else:
        await callback_query.answer("❌ Звук не найден.", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())