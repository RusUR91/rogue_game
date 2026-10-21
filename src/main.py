import curses
from domain.level_generator import LevelGenerator, get_room_center
from domain.models import Character, Position, Stats, KeyColor
from domain.game import (
    move_forward,
    move_backward,
    pickup_item,
    use_food,
    use_scroll,
    equip_weapon,
    use_elixir,
    update_enemies,
    rotate_direction,
    get_nearby_enemies,
    is_door_at_position,
    use_key,
    pickup_key,
)
from domain.difficulty_manager import DifficultyManager
from datalayer.save_system import save_game, save_result, load_results
from presentation.three_d_renderer import ThreeDRenderer
from random import randint

MAX_LEVEL = 21

def find_start_room(level):
    return next(room for room in level.rooms if room.is_start)

def create_character_on_start(level):
    start_room = find_start_room(level)
    start_position = get_room_center(start_room)
    
    return Character(
        hp=100,
        max_hp=100,
        agility=10,
        strength=10,
        position=start_position,
        direction=0,
        keys=[]
    )

def main(screen):
    curses.curs_set(0)
    screen.nodelay(False)
    screen.keypad(True)
    
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    difficulty_manager = DifficultyManager()
    level_generator = LevelGenerator(difficulty_manager)
    
    level_number = 1
    level = level_generator.generate_level(level_number, 1.0)
    character = create_character_on_start(level)
    stats = Stats()
    message = ""
    combat_messages = []
    
    level_stats = {
        "enemies_killed": 0,
        "damage_taken": 0,
        "food_used": 0,
        "potions_used": 0,
        "scrolls_used": 0,
        "steps": 0,
        "treasure": 0
    }
    
    renderer = ThreeDRenderer(screen)
    
    while True:
        if character.hp <= 0:
            difficulty_manager.update_stats(level_number, level_stats, character, False)
            stats.levels_completed = level_number
            save_result(stats)
            
            renderer.render(level, character, stats, f"ВЫ ПОГИБЛИ! Сложность: {difficulty_manager.get_difficulty_name()}", combat_messages)
            try:
                screen.addstr(15, 25, "ИГРА ОКОНЧЕНА", curses.A_BOLD)
                screen.addstr(16, 25, f"Сложность: {difficulty_manager.get_difficulty_name()}", curses.A_BOLD)
                screen.addstr(17, 23, "Нажми любую клавишу для выхода")
                screen.refresh()
            except:
                pass
            screen.getch()
            break
        
        difficulty_text = f"СЛОЖНОСТЬ: {difficulty_manager.get_difficulty_name()}"
        renderer.render(level, character, stats, f"{message} | {difficulty_text}", combat_messages)
        message = ""
        
        if len(combat_messages) > 10:
            combat_messages = combat_messages[-10:]
        
        key = screen.getch()
        
        if key == 27 or key == ord('q') or key == ord('Q'):
            stats.levels_completed = level_number
            save_result(stats)
            break
        
        elif key == ord('w') or key == ord('W'):
            direction_map = {0: Position(0, -1), 1: Position(1, 0), 2: Position(0, 1), 3: Position(-1, 0)}
            direction = direction_map[character.direction]
            new_position = Position(character.position.x + direction.x, character.position.y + direction.y)
            
            door = is_door_at_position(new_position, level)
            if door:
                if use_key(character, door):
                    message = f"Дверь открыта ключом {door.color.name if hasattr(door.color, 'name') else str(door.color)}"
                    combat_messages.append(f"Вы открыли дверь!")
                else:
                    color_name = door.color.name if hasattr(door.color, 'name') else str(door.color)
                    message = f"Дверь заперта! Нужен {color_name} ключ"
                    continue
            
            old_position = character.position
            moved = move_forward(character, level, stats)
            if moved:
                level_stats["steps"] += 1
                
                for key_item in level.keys:
                    if (character.position.x == key_item.position.x and 
                        character.position.y == key_item.position.y and 
                        not key_item.is_picked):
                        if pickup_key(character, key_item):
                            color_name = key_item.color.name if hasattr(key_item.color, 'name') else str(key_item.color)
                            message = f"Подобран {color_name} ключ!"
                            combat_messages.append(f"Вы нашли {color_name} ключ!")
                            break
                
                picked_item = pickup_item(character, level)
                if picked_item:
                    message = f"Подобран предмет: {picked_item.item_type}"
                    if picked_item.item_type == "food":
                        level_stats["food_used"] += 1
                    elif picked_item.item_type == "elixir":
                        level_stats["potions_used"] += 1
                    elif picked_item.item_type == "scroll":
                        level_stats["scrolls_used"] += 1
                
                update_enemies(level, character)
                
                if character.hp < 100:
                    damage_taken = 100 - character.hp
                    level_stats["damage_taken"] += damage_taken
                
                nearby = get_nearby_enemies(character, level, 5)
                for enemy in nearby:
                    if randint(1, 3) == 1:
                        combat_messages.append(f"Вы слышите {enemy.enemy_type} где-то рядом!")
            else:
                message = "Путь заблокирован"
        
        elif key == ord('s') or key == ord('S'):
            moved = move_backward(character, level, stats)
            if moved:
                level_stats["steps"] += 1
                
                for key_item in level.keys:
                    if (character.position.x == key_item.position.x and 
                        character.position.y == key_item.position.y and 
                        not key_item.is_picked):
                        if pickup_key(character, key_item):
                            color_name = key_item.color.name if hasattr(key_item.color, 'name') else str(key_item.color)
                            message = f"Подобран {color_name} ключ!"
                            combat_messages.append(f"Вы нашли {color_name} ключ!")
                            break
                
                picked_item = pickup_item(character, level)
                if picked_item:
                    message = f"Подобран предмет: {picked_item.item_type}"
                    if picked_item.item_type == "food":
                        level_stats["food_used"] += 1
                    elif picked_item.item_type == "elixir":
                        level_stats["potions_used"] += 1
                    elif picked_item.item_type == "scroll":
                        level_stats["scrolls_used"] += 1
                
                update_enemies(level, character)
            else:
                message = "Путь заблокирован"
        
        elif key == ord('a') or key == ord('A'):
            character.direction = rotate_direction(character.direction, 'left')
            message = "Поворот налево"
        
        elif key == ord('d') or key == ord('D'):
            character.direction = rotate_direction(character.direction, 'right')
            message = "Поворот направо"
        
        elif key == ord(' '):
            for key_item in level.keys:
                if (character.position.x == key_item.position.x and 
                    character.position.y == key_item.position.y and 
                    not key_item.is_picked):
                    if pickup_key(character, key_item):
                        color_name = key_item.color.name if hasattr(key_item.color, 'name') else str(key_item.color)
                        message = f"Подобран {color_name} ключ!"
                        combat_messages.append(f"Вы нашли {color_name} ключ!")
                        break
            
            picked_item = pickup_item(character, level)
            if picked_item:
                message = f"Подобран предмет: {picked_item.item_type}"
                if picked_item.item_type == "food":
                    level_stats["food_used"] += 1
                elif picked_item.item_type == "elixir":
                    level_stats["potions_used"] += 1
                elif picked_item.item_type == "scroll":
                    level_stats["scrolls_used"] += 1
            else:
                message = "Здесь ничего нет"
        
        elif key == ord('i') or key == ord('I'):
            renderer.show_inventory(character)
        
        elif key == ord('j') or key == ord('J'):
            used_item = use_food(character)
            if used_item:
                stats.food_eaten += 1
                level_stats["food_used"] += 1
                message = f"Съедена еда: +{used_item.hp_bonus} HP"
                combat_messages.append(f"Вы съели {used_item.subtype} и восстановили {used_item.hp_bonus} HP")
            else:
                message = "В рюкзаке нет еды"
        
        elif key == ord('t') or key == ord('T'):
            used_item = use_scroll(character)
            if used_item:
                stats.scrolls_used += 1
                level_stats["scrolls_used"] += 1
                message = f"Прочитан свиток: +{used_item.strength_bonus} к силе"
                combat_messages.append(f"Сила увеличилась на {used_item.strength_bonus}!")
            else:
                message = "В рюкзаке нет свитков"
        
        elif key == ord('k') or key == ord('K'):
            used_item = use_elixir(character)
            if used_item:
                stats.elixirs_used += 1
                level_stats["potions_used"] += 1
                message = f"Выпит эликсир: {used_item.subtype}"
                if used_item.subtype == "agility":
                    combat_messages.append(f"Ловкость +{used_item.agility_bonus}!")
                elif used_item.subtype == "strength":
                    combat_messages.append(f"Сила +{used_item.strength_bonus}!")
                elif used_item.subtype == "max_hp":
                    combat_messages.append(f"Макс. HP +{used_item.max_hp_bonus}!")
            else:
                message = "В рюкзаке нет эликсиров"
        
        elif key == ord('h') or key == ord('H'):
            weapon = equip_weapon(character)
            if weapon:
                message = f"Оружие экипировано: {weapon.subtype} (+{weapon.strength_bonus} урона)"
                combat_messages.append(f"Вы экипировали {weapon.subtype}! Урон +{weapon.strength_bonus}")
            else:
                message = "В рюкзаке нет оружия"
        
        elif key == ord('r') or key == ord('R'):
            renderer.show_results(load_results())
        
        elif key == ord('m') or key == ord('M'):
            renderer.toggle_mode()
            mode_name = "2D FULLSCREEN" if renderer.mode_2d_fullscreen else "3D VIEW"
            message = f"Режим: {mode_name}"
        
        if (character.position.x == level.exit_position.x and
            character.position.y == level.exit_position.y):
            
            level_stats["enemies_killed"] = stats.enemies_killed
            level_stats["treasure"] = stats.treasures_collected
            
            difficulty_manager.update_stats(level_number, level_stats, character, True)
            
            stats.levels_completed = level_number
            save_game(level_number, character, stats)
            
            if level_number == MAX_LEVEL:
                save_result(stats)
                renderer.render(level, character, stats, "ПОЗДРАВЛЯЮ! ВЫ ПРОШЛИ ИГРУ!", combat_messages)
                try:
                    screen.addstr(15, 25, "ВЫ ПОБЕДИЛИ!", curses.A_BOLD)
                    screen.addstr(17, 23, "Нажми любую клавишу для выхода")
                    screen.refresh()
                except:
                    pass
                screen.getch()
                break
            
            level_number += 1
            
            player_health_ratio = character.hp / character.max_hp
            level = level_generator.generate_level(level_number, player_health_ratio, level_stats)
            
            character.position = get_room_center(find_start_room(level))
            character.direction = 0
            
            level_stats = {
                "enemies_killed": 0,
                "damage_taken": 0,
                "food_used": 0,
                "potions_used": 0,
                "scrolls_used": 0,
                "steps": 0,
                "treasure": 0
            }
            
            message = f"ПЕРЕХОД НА УРОВЕНЬ {level_number} | Сложность: {difficulty_manager.get_difficulty_name()}"
            combat_messages.append(f"═══════════════════════════════════")
            combat_messages.append(f"    УРОВЕНЬ {level_number}")
            combat_messages.append(f"    Сложность: {difficulty_manager.get_difficulty_name()}")
            combat_messages.append(f"═══════════════════════════════════")
            
            if character.hp < character.max_hp:
                heal = randint(10, 30)
                character.hp = min(character.hp + heal, character.max_hp)
                combat_messages.append(f"Вы восстановили {heal} HP")
        
        if difficulty_manager.current_difficulty.value <= 1:  # VERY_EASY или EASY
            if randint(1, 50) == 1 and character.hp < character.max_hp:
                character.hp = min(character.hp + 1, character.max_hp)
                combat_messages.append("Вы медленно восстанавливаете здоровье")

if __name__ == "__main__":
    curses.wrapper(main)