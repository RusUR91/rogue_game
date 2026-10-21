from domain.models import Position, Room, KeyColor, Door, Key
from random import random, randint
import math

def is_inside_room_floor(position: Position, room: Room) -> bool:
    return (
        room.position.x < position.x < room.position.x + room.width - 1
        and room.position.y < position.y < room.position.y + room.height - 1
    )

def is_corridor_cell(position: Position, corridor) -> bool:
    return any(
        cell.x == position.x and cell.y == position.y
        for cell in corridor.cells
    )

def is_walkable(position: Position, level) -> bool:
    for room in level.rooms:
        if is_inside_room_floor(position, room):
            return True

    for corridor in level.corridors:
        if is_corridor_cell(position, corridor):
            return True

    if (position.x == level.exit_position.x and position.y == level.exit_position.y):
        return True

    return False

def rotate_direction(current_dir: int, turn: str) -> int:
    if turn == 'left':
        return (current_dir - 1) % 4
    elif turn == 'right':
        return (current_dir + 1) % 4
    return current_dir

def is_door_at_position(position, level):
    for door in level.doors:
        if door.position.x == position.x and door.position.y == position.y:
            return door
    return None

def use_key(character, door: Door) -> bool:
    if not door.is_locked:
        return True
    
    if character.has_key(door.color):
        character.remove_key(door.color)
        door.is_locked = False
        return True
    
    return False

def pickup_key(character, key: Key) -> bool:
    if not key.is_picked:
        character.add_key(key.color)
        key.is_picked = True
        return True
    return False

def move_forward(character, level, stats=None):
    direction_map = {
        0: Position(0, -1),
        1: Position(1, 0),
        2: Position(0, 1),
        3: Position(-1, 0),
    }
    
    direction = direction_map[character.direction]
    new_position = Position(
        character.position.x + direction.x,
        character.position.y + direction.y
    )

    door = is_door_at_position(new_position, level)
    if door:
        if not use_key(character, door):
            return False

    if not is_walkable(new_position, level):
        return False

    enemy = get_enemy_at_position(new_position, level)

    if enemy:
        attack_enemy(character, enemy)

        if enemy.hp <= 0:
            treasure = enemy.hostility + enemy.strength + enemy.agility + randint(1, 10)
            level.enemies.remove(enemy)

            if stats:
                stats.enemies_killed += 1
                stats.treasures_collected += treasure

            character.position = new_position
        else:
            attack_character(enemy, character)

        return True

    character.position = new_position

    if stats:
        stats.steps_made += 1

    return True

def move_backward(character, level, stats=None):
    direction_map = {
        0: Position(0, 1),
        1: Position(-1, 0),
        2: Position(0, -1),
        3: Position(1, 0),
    }
    
    direction = direction_map[character.direction]
    new_position = Position(
        character.position.x + direction.x,
        character.position.y + direction.y
    )

    door = is_door_at_position(new_position, level)
    if door:
        if not use_key(character, door):
            return False

    if not is_walkable(new_position, level):
        return False

    enemy = get_enemy_at_position(new_position, level)

    if enemy:
        attack_enemy(character, enemy)

        if enemy.hp <= 0:
            treasure = enemy.hostility + enemy.strength + enemy.agility + randint(1, 10)
            level.enemies.remove(enemy)

            if stats:
                stats.enemies_killed += 1
                stats.treasures_collected += treasure

            character.position = new_position
        else:
            attack_character(enemy, character)

        return True

    character.position = new_position

    if stats:
        stats.steps_made += 1

    return True

def pickup_item(character, level):
    for item in level.items:
        if (item.position.x == character.position.x and item.position.y == character.position.y):
            character.backpack.append(item)
            level.items.remove(item)
            return item
    return None

def get_enemy_at_position(position, level):
    for enemy in level.enemies:
        if enemy.position.x == position.x and enemy.position.y == position.y:
            return enemy
    return None

def attack_enemy(character, enemy):
    damage_power = character.strength
    if character.weapon:
        damage_power += character.weapon.strength_bonus
    damage = randint(1, damage_power)
    enemy.hp -= damage

def attack_character(enemy, character):
    hit_chance = enemy.agility / (enemy.agility + character.agility)
    if random() <= hit_chance:
        damage = randint(1, enemy.strength)
        character.hp -= damage
        return True
    return False

def use_food(character):
    for item in character.backpack:
        if item.item_type == "food":
            character.hp += item.hp_bonus
            if character.hp > character.max_hp:
                character.hp = character.max_hp
            character.backpack.remove(item)
            return item
    return None

def use_scroll(character):
    for item in character.backpack:
        if item.item_type == "scroll":
            character.strength += item.strength_bonus
            character.backpack.remove(item)
            return item
    return None

def equip_weapon(character):
    for item in character.backpack:
        if item.item_type == "weapon":
            character.weapon = item
            character.backpack.remove(item)
            return item
    return None

def use_elixir(character):
    for item in character.backpack:
        if item.item_type == "elixir":
            if item.subtype == "agility":
                character.agility += item.agility_bonus
            elif item.subtype == "strength":
                character.strength += item.strength_bonus
            elif item.subtype == "max_hp":
                character.max_hp += item.max_hp_bonus
                character.hp += item.max_hp_bonus
            character.backpack.remove(item)
            return item
    return None

def distance(pos1, pos2):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

def is_enemy_at_position(position, level):
    for enemy in level.enemies:
        if enemy.position.x == position.x and enemy.position.y == position.y:
            return True
    return False

def move_enemy_towards_player(enemy, character, level):
    dx = 0
    dy = 0

    if character.position.x > enemy.position.x:
        dx = 1
    elif character.position.x < enemy.position.x:
        dx = -1

    if character.position.y > enemy.position.y:
        dy = 1
    elif character.position.y < enemy.position.y:
        dy = -1

    new_position = Position(enemy.position.x + dx, enemy.position.y + dy)

    if new_position.x == character.position.x and new_position.y == character.position.y:
        attack_character(enemy, character)
        return

    if is_walkable(new_position, level) and not is_enemy_at_position(new_position, level):
        enemy.position = new_position

def get_room_for_position(position, level):
    for room in level.rooms:
        if (room.position.x <= position.x < room.position.x + room.width and
            room.position.y <= position.y < room.position.y + room.height):
            return room
    return None

def update_enemies(level, character):
    player_room = get_room_for_position(character.position, level)
    if player_room is None:
        return

    for enemy in level.enemies:
        enemy_room = get_room_for_position(enemy.position, level)
        if enemy_room != player_room:
            continue
        if distance(enemy.position, character.position) > enemy.hostility:
            continue
        if random() < 0.2:
            continue
        move_enemy_towards_player(enemy, character, level)

def get_nearby_enemies(character, level, radius=5):
    nearby = []
    for enemy in level.enemies:
        if distance(character.position, enemy.position) <= radius:
            nearby.append(enemy)
    return nearby