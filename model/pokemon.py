class Pokemon:
    def __init__(self, basic_data, species_data, evolution_chain):
        self.id = basic_data['id']
        self.name = basic_data['name'].upper()
        self.image_url = basic_data['sprites']['other']['official-artwork']['front_default']

        self.is_legendary = species_data['is_legendary']

        habitat_info = species_data.get('habitat')
        self.habitat = habitat_info['name'].capitalize() if habitat_info else "Unknown"

        self.evolution_chain = evolution_chain

        # Описание
        self.description = "Description is not found"
        entries = species_data.get('flavor_text_entries', [])
        for entry in entries:
            if entry['language']['name'] == 'en':
                self.description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                break

        # Типы
        self.types = [t['type']['name'].capitalize() for t in basic_data.get('types', [])]

        # Рост и Вес
        self.height = basic_data.get('height', 0) / 10
        self.weight = basic_data.get('weight', 0) / 10

        # Опыт
        self.base_exp = basic_data.get('base_experience', "Unknown")

        # Способности
        self.abilities = []
        for ab in basic_data.get('abilities', []):
            name = ab['ability']['name'].replace('-', ' ').title()
            if ab.get('is_hidden'):
                name += " (Скрытая)"
            self.abilities.append(name)

        # Характеристики
        self.stats = {}
        for stat_info in basic_data.get('stats', []):
            # Сокращаем длинные названия для красоты
            stat_name = stat_info['stat']['name']
            if stat_name == "special-attack": stat_name = "Sp.Atk"
            elif stat_name == "special-defense": stat_name = "Sp.Def"
            else: stat_name = stat_name.capitalize()

            self.stats[stat_name] = stat_info['base_stat']

        # Звуки
        cries = basic_data.get('cries', {})
        self.audio_url = cries.get('latest') or cries.get('legacy')


class LegendaryPokemon(Pokemon):
    def __init__(self, basic_data, species_data, evolution_chain):
        super().__init__(basic_data, species_data, evolution_chain)
        self.description = f"👑 **LEGENDARY** 👑\n{self.description}"