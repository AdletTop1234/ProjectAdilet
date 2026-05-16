import httpx
from model.pokemon import Pokemon, LegendaryPokemon

async def get_pokemon_data(name: str):
    async def _fetch_chain_recursive(client: httpx.AsyncClient, node: dict) -> list:
        name = node['species']['name']
        resp = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
        types = [t['type']['name'] for t in resp.json()['types']] if resp.status_code == 200 else []

        chain = [{"name": name.capitalize(), "types": types}]
        for next_node in node.get('evolves_to', []):
            chain.extend(await _fetch_chain_recursive(client, next_node))
        return chain

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
        if resp.status_code != 200:
            return None
        basic_data = resp.json()

        species_resp = await client.get(basic_data['species']['url'])
        species_data = species_resp.json()

        evo_resp = await client.get(species_data['evolution_chain']['url'])
        evo_data = evo_resp.json()

        full_chain = await _fetch_chain_recursive(client, evo_data['chain'])

        if species_data['is_legendary']:
            return LegendaryPokemon(basic_data, species_data, full_chain)
        return Pokemon(basic_data, species_data, full_chain)