class Pokemon:
    def __init__(self, basic_data, species_data, evolution_chain):
        self.name = basic_data['name'].upper()
        self.image_url = basic_data['sprites']['other']['official-artwork']['front_default']

        self.is_legendary = species_data['is_legendary']

        habitat_info = species_data.get('habitat')
        self.habitat = habitat_info['name'] if habitat_info else "Unknown"

        self.evolution_chain = evolution_chain

        self.description = "Description is not found"
        entries = species_data.get('flavor_text_entries', [])
        for entry in entries:
            if entry['language']['name'] == 'en':
                self.description = entry['flavor_text']
                break

class LegendaryPokemon(Pokemon):
    def __init__(self, basic_data, species_data, evolution_chain):
        super().__init__(basic_data, species_data, evolution_chain)

        self.description = f" LEGENDARY \n{self.description}"