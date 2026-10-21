from json import dump, load
from os import path


SAVE_FILE = "save.json"
RESULTS_FILE = "results.json"


def save_game(level_number, character, stats):
    game_state = {
        "level_number": level_number,
        "character": {
            "hp": character.hp,
            "max_hp": character.max_hp,
            "agility": character.agility,
            "strength": character.strength,
        },
        "stats": {
            "treasures_collected": stats.treasures_collected,
            "levels_completed": stats.levels_completed,
            "enemies_killed": stats.enemies_killed,
            "food_eaten": stats.food_eaten,
            "elixirs_used": stats.elixirs_used,
            "scrolls_used": stats.scrolls_used,
            "hits_dealt": stats.hits_dealt,
            "hits_taken": stats.hits_taken,
            "steps_made": stats.steps_made,
        }
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        dump(game_state, file, indent=4, ensure_ascii=False)


def load_game():
    if not path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r", encoding="utf-8") as file:
        return load(file)


def save_result(stats):
    result = {
        "treasures": stats.treasures_collected,
        "level": stats.levels_completed,
        "kills": stats.enemies_killed,
        "food": stats.food_eaten,
        "elixirs": stats.elixirs_used,
        "scrolls": stats.scrolls_used,
        "hits_dealt": stats.hits_dealt,
        "hits_taken": stats.hits_taken,
        "steps": stats.steps_made,
    }

    results = load_results()
    results.append(result)

    results.sort(key=lambda item: item["treasures"], reverse=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        dump(results, file, indent=4, ensure_ascii=False)


def load_results():
    if not path.exists(RESULTS_FILE):
        return []

    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return load(file)