from dataclasses import dataclass
from typing import Optional, List
from enum import IntEnum

class KeyColor(IntEnum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    WHITE = 4
    PURPLE = 5

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Room:
    position: Position
    width: int
    height: int
    is_start: bool = False
    is_exit: bool = False

@dataclass
class Corridor:
    cells: List[Position]

@dataclass
class Item:
    item_type: str
    subtype: str
    position: Position
    hp_bonus: int = 0
    max_hp_bonus: int = 0
    agility_bonus: int = 0
    strength_bonus: int = 0
    cost: int = 0

@dataclass
class Enemy:
    enemy_type: str
    hp: int
    agility: int
    strength: int
    hostility: int
    position: Position

@dataclass
class Door:
    position: Position
    color: KeyColor
    is_locked: bool = True

@dataclass
class Key:
    color: KeyColor
    position: Position
    is_picked: bool = False

@dataclass
class Character:
    hp: int
    max_hp: int
    agility: int
    strength: int
    position: Position
    direction: int = 0
    weapon: Optional[Item] = None
    backpack: List[Item] = None
    keys: List[KeyColor] = None
    
    def __post_init__(self):
        if self.backpack is None:
            self.backpack = []
        if self.keys is None:
            self.keys = []
    
    def has_key(self, color: KeyColor) -> bool:
        return color in self.keys
    
    def add_key(self, color: KeyColor):
        if color not in self.keys:
            self.keys.append(color)
    
    def remove_key(self, color: KeyColor):
        if color in self.keys:
            self.keys.remove(color)

@dataclass
class Level:
    level_number: int
    rooms: List[Room]
    corridors: List[Corridor]
    enemies: List[Enemy]
    items: List[Item]
    doors: List[Door]
    keys: List[Key]
    exit_position: Position

@dataclass
class Stats:
    treasures_collected: int = 0
    levels_completed: int = 0
    enemies_killed: int = 0
    food_eaten: int = 0
    elixirs_used: int = 0
    scrolls_used: int = 0
    hits_dealt: int = 0
    hits_taken: int = 0
    steps_made: int = 0

@dataclass
class GameSession:
    level: Level
    character: Character
    stats: Stats
    current_level_number: int = 1
    is_finished: bool = False
    is_won: bool = False