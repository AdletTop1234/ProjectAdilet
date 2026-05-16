import httpx
from model.pokemon import Pokemon, LegendaryPokemon

async def get_pokemon_data(name: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
        if resp.status_code != 200:
            return None
        basic_data = resp.json()

        species_resp = await client.get(basic_data['species']['url'])
        species_data = species_resp.json()

        evo_resp = await client.get(species_data['evolution_chain']['url'])
        evo_data = evo_resp.json()

        if species_data['is_legendary']:
            return LegendaryPokemon(basic_data, species_data, evo_data)
        return Pokemon(basic_data, species_data, evo_data)