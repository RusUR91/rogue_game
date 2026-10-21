from domain.models import Position, Room, Corridor, Door, Key, KeyColor
from random import choice, randint
from collections import deque
from typing import List, Optional

class DoorGenerator:
    def __init__(self, level_number: int):
        self.level_number = level_number
    
    def _doors_per_level(self) -> int:
        """Количество дверей в зависимости от уровня"""
        if self.level_number <= 3:
            return 2
        elif self.level_number <= 6:
            return 3
        elif self.level_number <= 9:
            return 4
        else:
            return 5
    
    def _find_door_tile(self, room: Room, corridors: List[Corridor]) -> Optional[Position]:
        """Находит клетку где коридор соприкасается со стеной комнаты"""
        # Проверяем стены комнаты
        for x in range(room.position.x, room.position.x + room.width):
            # Верхняя стена
            y = room.position.y - 1
            for corridor in corridors:
                for cell in corridor.cells:
                    if cell.x == x and cell.y == y:
                        return Position(x, y)
            # Нижняя стена
            y = room.position.y + room.height
            for corridor in corridors:
                for cell in corridor.cells:
                    if cell.x == x and cell.y == y:
                        return Position(x, y)
        
        for y in range(room.position.y, room.position.y + room.height):
            # Левая стена
            x = room.position.x - 1
            for corridor in corridors:
                for cell in corridor.cells:
                    if cell.x == x and cell.y == y:
                        return Position(x, y)
            # Правая стена
            x = room.position.x + room.width
            for corridor in corridors:
                for cell in corridor.cells:
                    if cell.x == x and cell.y == y:
                        return Position(x, y)
        return None
    
    def generate_doors(self, rooms: List[Room], corridors: List[Corridor]) -> List[Door]:
        """Генерирует двери в случайных комнатах"""
        doors = []
        non_start_rooms = [r for r in rooms if not r.is_start and not r.is_exit]
        
        if not non_start_rooms:
            return doors
        
        num_doors = min(self._doors_per_level(), len(non_start_rooms))
        selected_rooms = []
        rooms_copy = non_start_rooms.copy()
        
        # Выбираем случайные комнаты для дверей
        for _ in range(num_doors):
            if not rooms_copy:
                break
            room = choice(rooms_copy)
            selected_rooms.append(room)
            rooms_copy.remove(room)
        
        colors = [KeyColor.RED, KeyColor.GREEN, KeyColor.BLUE, KeyColor.YELLOW, KeyColor.WHITE, KeyColor.PURPLE]
        
        for i, room in enumerate(selected_rooms):
            door_pos = self._find_door_tile(room, corridors)
            if door_pos:
                color = colors[i % len(colors)]
                door = Door(position=door_pos, color=color, is_locked=True)
                doors.append(door)
        
        return doors
    
    def generate_keys(self, rooms: List[Room], doors: List[Door]) -> List[Key]:
        """Генерирует ключи для дверей в других комнатах"""
        keys = []
        non_start_rooms = [r for r in rooms if not r.is_start]
        
        for door in doors:
            # Выбираем другую комнату для ключа
            available_rooms = [r for r in non_start_rooms if r != door.position]
            if available_rooms:
                key_room = choice(available_rooms)
                # Случайная позиция внутри комнаты
                x = randint(key_room.position.x + 1, key_room.position.x + key_room.width - 2)
                y = randint(key_room.position.y + 1, key_room.position.y + key_room.height - 2)
                key = Key(color=door.color, position=Position(x, y))
                keys.append(key)
        
        return keys

class PathValidator:
    def __init__(self, level, width=90, height=30):
        self.level = level
        self.width = width
        self.height = height
    
    def _is_walkable(self, x: int, y: int) -> bool:
        """Проверяет, можно ли пройти через клетку (без учёта дверей)"""
        from domain.game import is_walkable
        return is_walkable(Position(x, y), self.level)
    
    def _is_door_at_position(self, x: int, y: int):
        """Проверяет, есть ли дверь на позиции"""
        for door in self.level.doors:
            if door.position.x == x and door.position.y == y:
                return door
        return None
    
    def validate_level(self, start_pos: Position) -> bool:
        """Проверяет, что все ключи достижимы и открывают свои двери"""
        if not self.level.doors:
            return True
        
        def bfs(start, target, opened_colors):
            queue = deque([start])
            visited = {(start.x, start.y)}
            
            while queue:
                pos = queue.popleft()
                if pos.x == target.x and pos.y == target.y:
                    return True
                
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = pos.x + dx, pos.y + dy
                    if (nx, ny) in visited:
                        continue
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        door = self._is_door_at_position(nx, ny)
                        if door:
                            if door.color not in opened_colors:
                                continue
                        if self._is_walkable(nx, ny):
                            queue.append(Position(nx, ny))
                            visited.add((nx, ny))
            return False
        
        opened = set()
        
        for door in self.level.doors:
            # Находим ключ для этой двери
            key_pos = None
            for key in self.level.keys:
                if key.color == door.color and not key.is_picked:
                    key_pos = key.position
                    break
            
            if key_pos is None:
                return False
            
            # Проверяем, можно ли дойти до ключа
            if not bfs(start_pos, key_pos, opened):
                return False
            
            opened.add(door.color)
            
            # Проверяем, можно ли дойти до двери
            if not bfs(key_pos, door.position, opened):
                return False
        
        # Проверяем, можно ли дойти до выхода
        if not bfs(start_pos, self.level.exit_position, opened):
            return False
        
        return True