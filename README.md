# ⚡ PokéBot — Telegram Pokémon Encyclopedia

A Telegram bot built with **aiogram 3** that acts as a comprehensive digital Pokédex. Users can search for individual Pokémon by name or ID, view detailed statistics and evolutionary chains, flip through the Pokédex via inline buttons, and even listen to original Pokémon cries!

This project was developed as a practical assignment/student project to demonstrate asynchronous programming in Python, REST API integration, and Telegram Bot API handling.

---

## 🚀 Features

*   🔍 **Flexible Search:** Find any Pokémon by typing its English name (e.g., `Pikachu`) or Pokédex ID (e.g., `133`).
*   🎲 **Randomizer:** Discover unexpected Pokémon with a single click using the "Random Pokémon" button.
*   📊 **Visualized Stats:** View beautiful, dynamically adjusted in-app progress bars (`🟩🟩⬜⬜`) representing base stats (HP, Attack, Speed, etc.).
*   🧬 **Evolutionary Chains:** Asynchronously fetches and compiles full evolution trees, including names and corresponding elemental types.
*   🔊 **Audio Cries:** Streams and delivers original high-quality audio recordings (`.ogg` voice messages) of Pokémon cries directly into the chat via external API streaming.
*   🖼 **Interactive Navigation:** Smoothly browse forward or backward using reactive inline buttons without cluttering chat history.
*   👑 **Legendary Highlights:** Distinctive visual badges and descriptions for Mythical and Legendary Pokémon using Object-Oriented Polymorphism.

---

## 🛠 Tech Stack & Architecture

*   **Language:** Python 3.10+
*   **Framework:** `aiogram 3.x` (Asynchronous Telegram Bot API wrapper)
*   **Networking:** `httpx` (Async HTTP requests for high concurrency performance)
*   **External API:** [PokéAPI](https://pokeapi.co/)
*   **Data Models:** OOP implementation mapping JSON structures to clean Python objects with built-in inheritance for special instances (`LegendaryPokemon`).

---

## 📁 Project Structure

```text
├── main.py             # Bot initialization, routers, and event handlers
├── api_client.py       # Asynchronous PokéAPI client handling complex data fetching
├── model/
│   └── pokemon.py      # OOP Models (Pokemon and LegendaryPokemon classes)
├── settings.json       # Configuration file (Tokens and configuration settings)
└── README.md           # Project documentation
