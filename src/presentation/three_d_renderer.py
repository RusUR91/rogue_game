import curses
import math
from domain.models import Position


class ThreeDRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.view_distance = 12
        self.fov = 80
        self.mode_2d_fullscreen = False
        
    def safe_addstr(self, y, x, text, attr=0):
        try:
            height, width = self.screen.getmaxyx()
            if 0 <= y < height and 0 <= x < width:
                max_len = width - x
                if max_len > 0:
                    self.screen.addstr(y, x, text[:max_len], attr)
        except:
            pass
    
    def safe_addch(self, y, x, ch, attr=0):
        try:
            height, width = self.screen.getmaxyx()
            if 0 <= y < height and 0 <= x < width:
                self.screen.addch(y, x, ch, attr)
        except:
            pass
    
    def toggle_mode(self):
        self.mode_2d_fullscreen = not self.mode_2d_fullscreen
    
    def get_key_symbol(self, color):
        key_symbols = {
            0: 'r',  # RED
            1: 'g',  # GREEN
            2: 'b',  # BLUE
            3: 'y',  # YELLOW
            4: 'w',  # WHITE
            5: 'p'   # PURPLE
        }
        if hasattr(color, 'value'):
            return key_symbols.get(color.value, 'k')
        return key_symbols.get(color, 'k')
    
    def get_door_symbol(self, color):
        door_symbols = {
            0: 'R',  # RED
            1: 'G',  # GREEN
            2: 'B',  # BLUE
            3: 'Y',  # YELLOW
            4: 'W',  # WHITE
            5: 'P'   # PURPLE
        }
        if hasattr(color, 'value'):
            return door_symbols.get(color.value, 'D')
        return door_symbols.get(color, 'D')
    
    def cast_ray(self, level, character, angle):
        rad = math.radians(angle)
        direction = Position(math.cos(rad), math.sin(rad))
        
        distance = 0
        max_distance = self.view_distance
        step_size = 0.1
        
        x = float(character.position.x)
        y = float(character.position.y)
        
        while distance < max_distance:
            test_pos = Position(int(x), int(y))
            
            for enemy in level.enemies:
                if enemy.position.x == test_pos.x and enemy.position.y == test_pos.y:
                    return distance, 'enemy', enemy
            
            for item in level.items:
                if item.position.x == test_pos.x and item.position.y == test_pos.y:
                    return distance, 'item', item
            
            if test_pos.x == level.exit_position.x and test_pos.y == level.exit_position.y:
                return distance, 'exit', None
            
            if not self.is_walkable_3d(test_pos, level):
                return distance, 'wall', None
            
            x += direction.x * step_size
            y += direction.y * step_size
            distance += step_size
            
        return max_distance, 'empty', None
    
    def is_walkable_3d(self, position, level):
        if position.x < 0 or position.x >= 90 or position.y < 0 or position.y >= 30:
            return False
            
        for room in level.rooms:
            if (room.position.x <= position.x <= room.position.x + room.width - 1 and
                room.position.y <= position.y <= room.position.y + room.height - 1):
                if (position.x == room.position.x or 
                    position.x == room.position.x + room.width - 1 or
                    position.y == room.position.y or 
                    position.y == room.position.y + room.height - 1):
                    return False
                return True
                
        for corridor in level.corridors:
            for cell in corridor.cells:
                if cell.x == position.x and cell.y == position.y:
                    return True
                    
        if (position.x == level.exit_position.x and 
            position.y == level.exit_position.y):
            return True
            
        return False
    
    def render_3d_view(self, level, character):
        try:
            height, width = self.screen.getmaxyx()
            view_width = min(80, width - 4)
            view_height = min(25, height - 10)
            start_x = 2
            start_y = 8
            
            if view_width <= 0 or view_height <= 0:
                return
            
            start_angle = character.direction * 90 - self.fov / 2
            wall_chars = ['█', '▓', '▒', '░', ' ']
            
            for y in range(view_height):
                for x in range(view_width):
                    self.safe_addch(start_y + y, start_x + x, ' ')
            
            for x in range(view_width):
                try:
                    angle = start_angle + (x / view_width) * self.fov
                    distance, obj_type, obj = self.cast_ray(level, character, angle)
                    
                    if distance < 0.1:
                        wall_height = view_height
                    else:
                        wall_height = int(view_height / (distance + 0.2))
                    
                    if wall_height > view_height:
                        wall_height = view_height
                    
                    start_y_pos = (view_height - wall_height) // 2
                    end_y_pos = start_y_pos + wall_height
                    
                    for y in range(view_height):
                        if start_y_pos <= y < end_y_pos:
                            if obj_type == 'wall':
                                char_index = min(int(distance / 3), len(wall_chars) - 1)
                                self.safe_addch(start_y + y, start_x + x, wall_chars[char_index])
                            elif obj_type == 'enemy':
                                if abs(y - view_height // 2) < 3:
                                    symbol = self.get_enemy_symbol(obj.enemy_type)
                                    color = curses.color_pair(1) if curses.has_colors() else 0
                                    self.safe_addch(start_y + y, start_x + x, symbol, color)
                                else:
                                    char_index = min(int(distance / 3), len(wall_chars) - 1)
                                    self.safe_addch(start_y + y, start_x + x, wall_chars[char_index])
                            elif obj_type == 'item':
                                if abs(y - view_height // 2) < 2:
                                    symbol = self.get_item_symbol(obj.item_type)
                                    color = curses.color_pair(3) if curses.has_colors() else 0
                                    self.safe_addch(start_y + y, start_x + x, symbol, color)
                                else:
                                    char_index = min(int(distance / 3), len(wall_chars) - 1)
                                    self.safe_addch(start_y + y, start_x + x, wall_chars[char_index])
                            elif obj_type == 'exit':
                                if abs(y - view_height // 2) < 2:
                                    color = curses.color_pair(2) if curses.has_colors() else 0
                                    self.safe_addch(start_y + y, start_x + x, 'E', color)
                                else:
                                    char_index = min(int(distance / 3), len(wall_chars) - 1)
                                    self.safe_addch(start_y + y, start_x + x, wall_chars[char_index])
                except Exception:
                    pass
        except Exception:
            pass
    
    def render_2d_fullscreen(self, level, character):
        try:
            height, width = self.screen.getmaxyx()
            map_height = height - 12
            map_width = width - 4
            start_x = 2
            start_y = 8
            
            if map_width <= 0 or map_height <= 0:
                return
            
            offset_x = character.position.x - map_width // 2
            offset_y = character.position.y - map_height // 2
            
            enemy_symbols = {
                "zombie": "Z", "vampire": "V", "ghost": "G",
                "ogre": "O", "snake_mage": "S"
            }
            
            item_symbols = {
                "food": "f", "scroll": "s", "elixir": "e", "weapon": "w"
            }
            
            for y in range(map_height):
                for x in range(map_width):
                    world_x = x + offset_x
                    world_y = y + offset_y
                    
                    if world_x < 0 or world_x >= 90 or world_y < 0 or world_y >= 30:
                        self.safe_addch(start_y + y, start_x + x, ' ')
                        continue
                    
                    if world_x == character.position.x and world_y == character.position.y:
                        direction_chars = ['↑', '→', '↓', '←']
                        self.safe_addch(start_y + y, start_x + x, direction_chars[character.direction], curses.A_BOLD)
                        continue
                    
                    if world_x == level.exit_position.x and world_y == level.exit_position.y:
                        self.safe_addch(start_y + y, start_x + x, 'E', curses.A_BOLD)
                        continue
                    
                    # Отрисовка ключей
                    key_found = False
                    if hasattr(level, 'keys'):
                        for key in level.keys:
                            if not key.is_picked and key.position.x == world_x and key.position.y == world_y:
                                symbol = self.get_key_symbol(key.color)
                                color = curses.color_pair(3) if curses.has_colors() else 0
                                self.safe_addch(start_y + y, start_x + x, symbol, color)
                                key_found = True
                                break
                    
                    if key_found:
                        continue
                    
                    door_found = False
                    if hasattr(level, 'doors'):
                        for door in level.doors:
                            if door.position.x == world_x and door.position.y == world_y:
                                symbol = self.get_door_symbol(door.color)
                                if door.is_locked:
                                    color = curses.color_pair(1) if curses.has_colors() else 0
                                else:
                                    color = curses.color_pair(2) if curses.has_colors() else 0
                                self.safe_addch(start_y + y, start_x + x, symbol, color)
                                door_found = True
                                break
                    
                    if door_found:
                        continue
                    
                    enemy_found = False
                    for enemy in level.enemies:
                        if enemy.position.x == world_x and enemy.position.y == world_y:
                            symbol = enemy_symbols.get(enemy.enemy_type, '?')
                            color = curses.color_pair(1) if curses.has_colors() else 0
                            self.safe_addch(start_y + y, start_x + x, symbol, color)
                            enemy_found = True
                            break
                    
                    if enemy_found:
                        continue
                    
                    item_found = False
                    for item in level.items:
                        if item.position.x == world_x and item.position.y == world_y:
                            symbol = item_symbols.get(item.item_type, '?')
                            color = curses.color_pair(3) if curses.has_colors() else 0
                            self.safe_addch(start_y + y, start_x + x, symbol, color)
                            item_found = True
                            break
                    
                    if item_found:
                        continue
                    
                    is_walkable = self.is_walkable_3d(Position(world_x, world_y), level)
                    self.safe_addch(start_y + y, start_x + x, '.' if is_walkable else '#')
        except Exception:
            pass
    
    def render_minimap(self, level, character):
        if self.mode_2d_fullscreen:
            return
            
        try:
            height, width = self.screen.getmaxyx()
            map_width = min(35, width - 6)
            map_height = min(18, height - 15)
            map_x = width - map_width - 3
            map_y = height - map_height - 5
            
            if map_width <= 0 or map_height <= 0 or map_x < 0 or map_y < 0:
                return
            
            self.safe_addstr(map_y - 1, map_x - 1, "┌" + "─" * map_width + "┐")
            self.safe_addstr(map_y + map_height, map_x - 1, "└" + "─" * map_width + "┘")
            self.safe_addstr(map_y - 1, map_x + map_width, "┐")
            self.safe_addstr(map_y + map_height, map_x + map_width, "┘")
            
            for i in range(map_height):
                self.safe_addch(map_y + i, map_x - 1, '│')
                self.safe_addch(map_y + i, map_x + map_width, '│')
            
            self.safe_addstr(map_y - 1, map_x + 2, " МИНИ-КАРТА ")
            
            offset_x = character.position.x - map_width // 2
            offset_y = character.position.y - map_height // 2
            
            enemy_symbols = {
                "zombie": "Z", "vampire": "V", "ghost": "G",
                "ogre": "O", "snake_mage": "S"
            }
            
            item_symbols = {
                "food": "f", "scroll": "s", "elixir": "e", "weapon": "w"
            }
            
            for y in range(map_height):
                for x in range(map_width):
                    world_x = x + offset_x
                    world_y = y + offset_y
                    
                    if world_x < 0 or world_x >= 90 or world_y < 0 or world_y >= 30:
                        self.safe_addch(map_y + y, map_x + x, ' ')
                        continue
                    
                    if world_x == character.position.x and world_y == character.position.y:
                        direction_chars = ['↑', '→', '↓', '←']
                        self.safe_addch(map_y + y, map_x + x, direction_chars[character.direction], curses.A_BOLD)
                        continue
                    
                    if world_x == level.exit_position.x and world_y == level.exit_position.y:
                        self.safe_addch(map_y + y, map_x + x, 'E')
                        continue
                    
                    # Отрисовка ключей на мини-карте
                    key_found = False
                    if hasattr(level, 'keys'):
                        for key in level.keys:
                            if not key.is_picked and key.position.x == world_x and key.position.y == world_y:
                                symbol = self.get_key_symbol(key.color)
                                self.safe_addch(map_y + y, map_x + x, symbol)
                                key_found = True
                                break
                    
                    if key_found:
                        continue
                    
                    door_found = False
                    if hasattr(level, 'doors'):
                        for door in level.doors:
                            if door.position.x == world_x and door.position.y == world_y:
                                symbol = self.get_door_symbol(door.color)
                                self.safe_addch(map_y + y, map_x + x, symbol)
                                door_found = True
                                break
                    
                    if door_found:
                        continue
                    
                    enemy_found = False
                    for enemy in level.enemies:
                        if enemy.position.x == world_x and enemy.position.y == world_y:
                            symbol = enemy_symbols.get(enemy.enemy_type, '?')
                            self.safe_addch(map_y + y, map_x + x, symbol, curses.A_BOLD)
                            enemy_found = True
                            break
                    
                    if enemy_found:
                        continue
                    
                    item_found = False
                    for item in level.items:
                        if item.position.x == world_x and item.position.y == world_y:
                            symbol = item_symbols.get(item.item_type, '?')
                            self.safe_addch(map_y + y, map_x + x, symbol)
                            item_found = True
                            break
                    
                    if item_found:
                        continue
                    
                    is_walkable = self.is_walkable_3d(Position(world_x, world_y), level)
                    self.safe_addch(map_y + y, map_x + x, '.' if is_walkable else '#')
        except Exception:
            pass
    
    def get_enemy_symbol(self, enemy_type):
        symbols = {"zombie": "Z", "vampire": "V", "ghost": "G", "ogre": "O", "snake_mage": "S"}
        return symbols.get(enemy_type, "?")
    
    def get_item_symbol(self, item_type):
        symbols = {"food": "f", "scroll": "s", "elixir": "e", "weapon": "w"}
        return symbols.get(item_type, "?")
    
    def render_hud(self, character, stats, message, level):
        try:
            height, width = self.screen.getmaxyx()
            
            mode_text = "3D" if not self.mode_2d_fullscreen else "2D"
            mode_color = curses.color_pair(2) if curses.has_colors() else 0
            self.safe_addstr(0, width - 10, f"[{mode_text}]", mode_color)
            
            try:
                self.screen.hline(0, 2, '═', width - 5)
                self.screen.hline(6, 2, '═', width - 5)
                self.screen.vline(1, 2, '║', 5)
                self.screen.vline(1, width - 3, '║', 5)
            except:
                pass
            
            self.safe_addstr(1, 5, f"УРОВЕНЬ: {level.level_number}")
            self.safe_addstr(1, 30, f"СОКРОВИЩА: {stats.treasures_collected}")
            self.safe_addstr(1, 55, f"УБИЙСТВА: {stats.enemies_killed}")
            
            hp_text = f"HP: {character.hp}/{character.max_hp}"
            self.safe_addstr(2, 5, hp_text)
            
            if character.max_hp > 0:
                hp_percent = character.hp / character.max_hp
                hp_bar_length = 30
                hp_filled = int(hp_bar_length * hp_percent)
                hp_bar = "█" * hp_filled + "░" * (hp_bar_length - hp_filled)
                self.safe_addstr(2, 20, "[" + hp_bar + "]")
            
            self.safe_addstr(3, 5, f"СИЛА: {character.strength} | ЛОВКОСТЬ: {character.agility}")
            
            keys_text = "КЛЮЧИ: "
            if hasattr(character, 'keys') and character.keys:
                key_names = []
                for k in character.keys:
                    if hasattr(k, 'name'):
                        key_names.append(k.name[0].upper())
                    elif hasattr(k, 'value'):
                        key_names.append(['R','G','B','Y','W','P'][k.value])
                    else:
                        key_names.append(str(k)[0].upper())
                keys_text += " ".join(key_names)
            else:
                keys_text += "нет"
            self.safe_addstr(4, 5, keys_text[:40])
            
            if character.weapon:
                self.safe_addstr(3, 40, f"ОРУЖИЕ: {character.weapon.subtype} (+{character.weapon.strength_bonus})")
            else:
                self.safe_addstr(3, 40, "ОРУЖИЕ: нет")
            
            self.safe_addstr(4, 40, f"РЮКЗАК: {len(character.backpack)} предметов")
            
            if message:
                self.safe_addstr(5, 5, f"➤ {message}", curses.A_BOLD)
            
            controls_y = height - 4
            if controls_y > 15:
                controls_text = "W/S - вперед/назад | A/D - поворот | M - вид | ПРОБЕЛ - взять | I-инвентарь | J-еда | H-оружие | K-эликсир | T-свиток | R-рекорды | Q-выход"
                self.safe_addstr(controls_y, 2, controls_text[:width-4])
        except Exception:
            pass
    
    def render_combat_log(self, combat_messages):
        if not combat_messages or self.mode_2d_fullscreen:
            return
            
        try:
            height, width = self.screen.getmaxyx()
            log_x = 2
            log_y = height - 12
            
            if log_y > 15:
                self.safe_addstr(log_y - 1, log_x, "┌" + "─" * 35 + "┐")
                self.safe_addstr(log_y, log_x, "│           ЛОГ БОЯ           │")
                self.safe_addstr(log_y + 1, log_x, "├" + "─" * 35 + "┤")
                
                for i, msg in enumerate(combat_messages[-6:]):
                    if log_y + 2 + i < height - 5:
                        self.safe_addstr(log_y + 2 + i, log_x + 1, " " + msg[:33] + " " * (34 - len(msg[:33])))
                        self.safe_addstr(log_y + 2 + i, log_x + 35, "│")
                
                self.safe_addstr(log_y + 8, log_x, "└" + "─" * 35 + "┘")
        except Exception:
            pass
    
    def render(self, level, character, stats, message="", combat_messages=None):
        try:
            self.screen.clear()
            
            if curses.has_colors():
                curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
                curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            
            if self.mode_2d_fullscreen:
                self.render_2d_fullscreen(level, character)
            else:
                self.render_3d_view(level, character)
                self.render_minimap(level, character)
            
            self.render_hud(character, stats, message, level)
            
            if combat_messages and not self.mode_2d_fullscreen:
                self.render_combat_log(combat_messages)
            
            self.screen.refresh()
        except Exception:
            try:
                self.screen.clear()
                self.safe_addstr(0, 0, f"Level: {level.level_number}")
                self.safe_addstr(1, 0, f"HP: {character.hp}/{character.max_hp}")
                self.safe_addstr(2, 0, f"Str: {character.strength} Agi: {character.agility}")
                self.safe_addstr(3, 0, f"Treasures: {stats.treasures_collected}")
                if message:
                    self.safe_addstr(5, 0, message)
                self.screen.refresh()
            except:
                pass

    def show_inventory(self, character):
        try:
            self.screen.clear()
            height, width = self.screen.getmaxyx()
            
            self.safe_addstr(2, width//2 - 15, "╔" + "═" * 30 + "╗")
            self.safe_addstr(3, width//2 - 15, "║          ИНВЕНТАРЬ           ║")
            self.safe_addstr(4, width//2 - 15, "╠" + "═" * 30 + "╣")
            
            if hasattr(character, 'keys') and character.keys:
                self.safe_addstr(5, width//2 - 12, "║ КЛЮЧИ:                       ║")
                key_line = "║ "
                for key in character.keys:
                    if hasattr(key, 'name'):
                        key_line += f"{key.name} "
                    elif hasattr(key, 'value'):
                        names = ['RED', 'GREEN', 'BLUE', 'YELLOW', 'WHITE', 'PURPLE']
                        key_line += f"{names[key.value]} "
                    else:
                        key_line += f"{str(key)} "
                key_line += " " * (28 - len(key_line)) + "║"
                self.safe_addstr(6, width//2 - 15, key_line[:31])
                offset = 7
            else:
                self.safe_addstr(5, width//2 - 12, "║ КЛЮЧИ: нет                  ║")
                offset = 6
            
            if not character.backpack:
                self.safe_addstr(offset + 1, width//2 - 12, "║        Рюкзак пуст         ║")
            else:
                for i, item in enumerate(character.backpack):
                    y = offset + 1 + i
                    if y < height - 5:
                        item_text = f"{i+1}. {item.item_type} ({item.subtype})"
                        
                        if item.item_type == "food":
                            item_text += f" +{item.hp_bonus} HP"
                        elif item.item_type == "scroll":
                            item_text += f" +{item.strength_bonus} STR"
                        elif item.item_type == "elixir":
                            if hasattr(item, "agility_bonus"):
                                item_text += f" +{item.agility_bonus} AGI"
                        elif item.item_type == "weapon":
                            item_text += f" +{item.strength_bonus} DMG"
                        
                        spaces = 30 - len(item_text) - 2
                        if spaces < 0:
                            item_text = item_text[:28]
                            spaces = 0
                        self.safe_addstr(y, width//2 - 15, f"║ {item_text}{' ' * spaces} ║")
            
            self.safe_addstr(height-4, width//2 - 15, "╚" + "═" * 30 + "╝")
            self.safe_addstr(height-2, width//2 - 15, "Нажми любую клавишу")
            self.screen.refresh()
            self.screen.getch()
        except:
            pass
    
    def show_results(self, results):
        try:
            self.screen.clear()
            height, width = self.screen.getmaxyx()
            
            self.safe_addstr(2, width//2 - 20, "╔" + "═" * 40 + "╗")
            self.safe_addstr(3, width//2 - 20, "║           ТАБЛИЦА РЕКОРДОВ            ║")
            self.safe_addstr(4, width//2 - 20, "╠════════╦══════════╦════════╦════════╦═══════════╣")
            self.safe_addstr(5, width//2 - 20, "║   #    ║ Сокровища ║ Уровень ║ Убийства ║   Шаги    ║")
            self.safe_addstr(6, width//2 - 20, "╠════════╬══════════╬════════╬════════╬═══════════╣")
            
            if not results:
                self.safe_addstr(8, width//2 - 18, "║         Пока нет результатов          ║")
            else:
                for i, result in enumerate(results[:10]):
                    y = 7 + i
                    if y < height - 5:
                        treasures = str(result.get('treasures', 0))[:8]
                        level_num = str(result.get('level', 0))[:6]
                        kills = str(result.get('kills', 0))[:6]
                        steps = str(result.get('steps', 0))[:9]
                        line = f"║{i+1:^6} ║{treasures:^8} ║{level_num:^6} ║{kills:^6} ║{steps:^9}║"
                        self.safe_addstr(y, width//2 - 20, line[:41])
            
            self.safe_addstr(height-5, width//2 - 20, "╚════════╩══════════╩════════╩════════╩═══════════╝")
            self.safe_addstr(height-3, width//2 - 20, "Нажми любую клавишу для выхода")
            self.screen.refresh()
            self.screen.getch()
        except:
            pass