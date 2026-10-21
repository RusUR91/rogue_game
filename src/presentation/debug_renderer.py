from domain.level_generator import generate_level


enemy_symbols = {
    "zombie": "z",
    "vampire": "v",
    "ghost": "g",
    "ogre": "O",
    "snake_mage": "s"
}


def render_debug_level(level, character):
    grid = [[" " for _ in range(90)] for _ in range(30)]

    for room in level.rooms:
        left = room.position.x
        right = room.position.x + room.width - 1
        top = room.position.y
        bottom = room.position.y + room.height - 1

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                is_wall = (
                    x == left
                    or x == right
                    or y == top
                    or y == bottom
                )

                if is_wall:
                    grid[y][x] = "#"
                else:
                    grid[y][x] = "."

    for corridor in level.corridors:
        for cell in corridor.cells:
            if grid[cell.y][cell.x] == " ":
                grid[cell.y][cell.x] = "#"
            elif grid[cell.y][cell.x] == "#":
                grid[cell.y][cell.x] = "+"

    for item in level.items:
        if item.item_type == "food":
            symbol = "f"
        elif item.item_type == "weapon":
            symbol = "w"
        elif item.item_type == "elixir":
            symbol = "e"
        elif item.item_type == "scroll":
            symbol = "s"

    for enemy in level.enemies:
        symbol = enemy_symbols.get(enemy.enemy_type, "?")
        grid[enemy.position.y][enemy.position.x] = symbol

    grid[item.position.y][item.position.x] = symbol

    exit_pos = level.exit_position
    grid[exit_pos.y][exit_pos.x] = "E"

    grid[character.position.y][character.position.x] = '@'

    for row in grid:
        print("".join(row))