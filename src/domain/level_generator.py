from domain.models import Level, Room, Position, Corridor, Item, Enemy, Key
from domain.door_system import DoorGenerator, PathValidator
from domain.difficulty_manager import DifficultyManager
from random import randint, choice

MAP_WIDTH = 90
MAP_HEIGHT = 30

GRID_ROWS = 3
GRID_COLS = 3

SECTION_WIDTH = MAP_WIDTH // GRID_COLS
SECTION_HEIGHT = MAP_HEIGHT // GRID_ROWS

connections = [
    (0, 1), (1, 2), (2, 5), (5, 8), (8, 7), (7, 6), (6, 3), (3, 4),
]

def get_room_center(room: Room) -> Position:
    return Position(
        room.position.x + room.width // 2,
        room.position.y + room.height // 2
    )

class LevelGenerator:
    def __init__(self, difficulty_manager: DifficultyManager = None):
        self.difficulty_manager = difficulty_manager or DifficultyManager()
        self.current_difficulty_config = self.difficulty_manager.get_difficulty_config()
    
    def generate_room(self, row: int, col: int) -> Room:
        section_x = col * SECTION_WIDTH
        section_y = row * SECTION_HEIGHT

        room_width = randint(8, SECTION_WIDTH - 4)
        room_height = randint(4, SECTION_HEIGHT - 3)

        max_x_offset = SECTION_WIDTH - room_width - 1
        max_y_offset = SECTION_HEIGHT - room_height - 1

        room_x = section_x + randint(1, max_x_offset)
        room_y = section_y + randint(1, max_y_offset)

        return Room(
            position=Position(room_x, room_y),
            width=room_width,
            height=room_height
        )

    def generate_corridor(self, room1: Room, room2: Room) -> Corridor:
        center1 = get_room_center(room1)
        center2 = get_room_center(room2)

        corridor_cells = []

        if center1.x < center2.x:
            for x in range(center1.x, center2.x + 1):
                corridor_cells.append(Position(x, center1.y))
        else:
            for x in range(center2.x, center1.x + 1):
                corridor_cells.append(Position(x, center1.y))

        if center1.y < center2.y:
            for y in range(center1.y, center2.y + 1):
                corridor_cells.append(Position(center2.x, y))
        else:
            for y in range(center2.y, center1.y + 1):
                corridor_cells.append(Position(center2.x, y))

        return Corridor(cells=corridor_cells)

    def choose_item_type(self, level_number: int) -> str:
        config = self.current_difficulty_config
        
        if level_number <= 3:
            weights = ["food"] * int(3 * config.food_spawn_multiplier)
            weights += ["weapon"] * int(1 * config.weapon_spawn_multiplier)
        elif level_number <= 6:
            weights = ["food"] * int(2 * config.food_spawn_multiplier)
            weights += ["weapon"] * int(1 * config.weapon_spawn_multiplier)
            weights += ["elixir"] * int(1 * config.potion_spawn_multiplier)
        elif level_number <= 9:
            weights = ["food"] * int(2 * config.food_spawn_multiplier)
            weights += ["weapon"] * int(1 * config.weapon_spawn_multiplier)
            weights += ["elixir"] * int(1 * config.potion_spawn_multiplier)
            weights += ["scroll"] * int(1 * config.scroll_spawn_multiplier)
        else:
            weights = ["food"] * int(1 * config.food_spawn_multiplier)
            weights += ["weapon"] * int(1 * config.weapon_spawn_multiplier)
            weights += ["elixir"] * int(1 * config.potion_spawn_multiplier)
            weights += ["scroll"] * int(2 * config.scroll_spawn_multiplier)
        
        if not weights:
            weights = ["food"]
        
        return choice(weights)

    def generate_random_position_inside_room(self, room: Room) -> Position:
        x = randint(room.position.x + 1, room.position.x + room.width - 2)
        y = randint(room.position.y + 1, room.position.y + room.height - 2)
        return Position(x, y)

    def generate_items(self, rooms: List[Room], level_number: int, player_health_ratio: float = 1.0) -> list[Item]:
        items = []
        config = self.current_difficulty_config
        
        base_items_count = randint(1, 3)
        
        health_multiplier = 1.0
        if player_health_ratio < 0.3:
            health_multiplier = 2.0
        elif player_health_ratio < 0.5:
            health_multiplier = 1.5
        
        for room in rooms:
            if room.is_start:
                continue

            items_count = int(base_items_count * config.food_spawn_multiplier * health_multiplier)
            items_count = max(0, min(4, items_count))

            for _ in range(items_count):
                item_type = self.choose_item_type(level_number)
                position = self.generate_random_position_inside_room(room)

                if item_type == "food":
                    hp_bonus = randint(10, 25)
                    if player_health_ratio < 0.3:
                        hp_bonus = int(hp_bonus * 1.5)
                    item = Item(
                        item_type="food",
                        subtype=choice(["apple", "banana", "bread", "cheese"]),
                        position=position,
                        hp_bonus=hp_bonus
                    )
                elif item_type == "scroll":
                    item = Item(
                        item_type="scroll",
                        subtype="strength",
                        position=position,
                        strength_bonus=randint(1, 3)
                    )
                elif item_type == "elixir":
                    item = Item(
                        item_type="elixir",
                        subtype=choice(["agility", "strength", "max_hp"]),
                        position=position,
                        agility_bonus=randint(1, 3) if choice([True, False]) else 0,
                        strength_bonus=randint(1, 3) if choice([True, False]) else 0,
                        max_hp_bonus=randint(5, 15) if choice([True, False]) else 0
                    )
                else:
                    strength_bonus = randint(2, 5)
                    if self.current_difficulty_config.enemy_strength_multiplier > 1.2:
                        strength_bonus = randint(3, 7)
                    item = Item(
                        item_type="weapon",
                        subtype=choice(["sword", "axe", "dagger", "mace"]),
                        position=position,
                        strength_bonus=strength_bonus
                    )

                items.append(item)

        return items

    def generate_enemies(self, rooms: List[Room], level_number: int) -> list[Enemy]:
        enemies = []
        config = self.current_difficulty_config
    
        base_hp = 20 + level_number * 5
        base_agility = 1 + level_number
        base_strength = 1 + level_number
        
        for room in rooms:
            if room.is_start:
                continue

            base_count = randint(0, 3)
            enemies_count = int(base_count * config.enemy_count_multiplier)
            enemies_count = max(0, min(5, enemies_count))

            for _ in range(enemies_count):
                position = self.generate_random_position_inside_room(room)
                
                enemy_pool = ["zombie", "vampire", "ghost", "ogre", "snake_mage"]
                if config.enemy_strength_multiplier > 1.2:
                    enemy_pool = ["ogre", "snake_mage", "vampire", "zombie", "ghost"]
                elif config.enemy_strength_multiplier < 0.8:
                    enemy_pool = ["zombie", "ghost", "vampire", "ogre", "snake_mage"]
                
                enemy = Enemy(
                    enemy_type=choice(enemy_pool),
                    hp=int(base_hp * config.enemy_hp_multiplier),
                    agility=int(base_agility * config.enemy_agility_multiplier),
                    strength=int(base_strength * config.enemy_strength_multiplier),
                    hostility=randint(1, 10),
                    position=position
                )
                enemies.append(enemy)

        return enemies

    def generate_level(self, level_number: int, player_health_ratio: float = 1.0, level_stats: dict = None) -> Level:
        self.current_difficulty_config = self.difficulty_manager.get_difficulty_config()
        
        rooms = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rooms.append(self.generate_room(row, col))

        start_room = choice(rooms)
        exit_room = choice(rooms)
        while exit_room == start_room:
            exit_room = choice(rooms)

        start_room.is_start = True
        exit_room.is_exit = True

        exit_position = get_room_center(exit_room)

        corridors = []
        for room1_index, room2_index in connections:
            corridor = self.generate_corridor(rooms[room1_index], rooms[room2_index])
            corridors.append(corridor)

        items = self.generate_items(rooms, level_number, player_health_ratio)
        enemies = self.generate_enemies(rooms, level_number)

        door_gen = DoorGenerator(level_number)
        doors = door_gen.generate_doors(rooms, corridors)
        
        max_doors = int(len(doors) * self.current_difficulty_config.door_count_multiplier)
        doors = doors[:max_doors]
        
        keys = door_gen.generate_keys(rooms, doors)

        level = Level(
            level_number=level_number,
            rooms=rooms,
            corridors=corridors,
            enemies=enemies,
            items=items,
            doors=doors,
            keys=keys,
            exit_position=exit_position
        )

        validator = PathValidator(level)
        start_position = get_room_center(start_room)
        
        for attempt in range(3):
            if validator.validate_level(start_position):
                break
            doors = door_gen.generate_doors(rooms, corridors)
            doors = doors[:max_doors]
            keys = door_gen.generate_keys(rooms, doors)
            level.doors = doors
            level.keys = keys

        return level

def generate_level(level_number: int, player_health_ratio: float = 1.0, level_stats: dict = None) -> Level:
    generator = LevelGenerator()
    return generator.generate_level(level_number, player_health_ratio, level_stats)