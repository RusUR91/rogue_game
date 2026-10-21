import curses


def build_grid(level, character):
    grid = [[" " for _ in range(90)] for _ in range(30)]

    for room in level.rooms:
        left = room.position.x
        right = room.position.x + room.width - 1
        top = room.position.y
        bottom = room.position.y + room.height - 1

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                if x == left or x == right or y == top or y == bottom:
                    grid[y][x] = "#"
                else:
                    grid[y][x] = "."

    for corridor in level.corridors:
        for cell in corridor.cells:
            if grid[cell.y][cell.x] == " ":
                grid[cell.y][cell.x] = "#"
            elif grid[cell.y][cell.x] == "#":
                grid[cell.y][cell.x] = "+"

    item_symbols = {
        "food": "f",
        "scroll": "s",
        "elixir": "e",
        "weapon": "w",
    }

    for item in level.items:
        grid[item.position.y][item.position.x] = item_symbols.get(item.item_type, "?")

    enemy_symbols = {
        "zombie": "z",
        "vampire": "v",
        "ghost": "g",
        "ogre": "O",
        "snake_mage": "s",
    }

    for enemy in level.enemies:
        grid[enemy.position.y][enemy.position.x] = enemy_symbols.get(enemy.enemy_type, "?")

    exit_pos = level.exit_position
    grid[exit_pos.y][exit_pos.x] = "E"

    grid[character.position.y][character.position.x] = "@"

    return grid


def render_game(screen, level, character, stats, message=""):
    screen.clear()

    screen.addstr(0, 0, f"Уровень: {level.level_number}")
    screen.addstr(1, 0, f"HP: {character.hp}/{character.max_hp}")
    screen.addstr(2, 0, f"Сила: {character.strength} | Ловкость: {character.agility}")
    screen.addstr(3, 0, f"Рюкзак: {len(character.backpack)} предметов")
    screen.addstr(4, 0, f"Сокровища: {stats.treasures_collected}")
    screen.addstr(5, 0, f"Убито врагов: {stats.enemies_killed}")
    screen.addstr(6, 0, "WASD - ход | i инвентарь | h оружие | j еда | k эликсир | e свиток | r рекорды | q выход")

    if message:
        screen.addstr(7, 0, message[:90])

    grid = build_grid(level, character)

    offset_y = 9

    for y, row in enumerate(grid):
        screen.addstr(offset_y + y, 0, "".join(row))

    screen.refresh()


def show_results_screen(screen, results):
    screen.clear()
    screen.addstr(0, 0, "Таблица рекордов")

    if not results:
        screen.addstr(2, 0, "Пока результатов нет.")
    else:
        for i, result in enumerate(results[:10], start=1):
            line = (
                f"{i}. "
                f"Сокровища: {result['treasures']} | "
                f"Уровень: {result['level']} | "
                f"Убийства: {result['kills']} | "
                f"Шаги: {result['steps']}"
            )
            screen.addstr(i + 1, 0, line[:100])

    screen.addstr(14, 0, "Нажми любую клавишу, чтобы вернуться.")
    screen.refresh()
    screen.getch()


def show_inventory_screen(screen, character):
    screen.clear()

    screen.addstr(0, 0, "Рюкзак")

    if not character.backpack:
        screen.addstr(2, 0, "Рюкзак пуст.")
    else:
        for index, item in enumerate(character.backpack, start=1):
            line = f"{index}. {item.item_type} ({item.subtype})"

            if item.item_type == "food":
                line += f" +HP {item.hp_bonus}"

            elif item.item_type == "scroll":
                line += f" +STR {item.strength_bonus}"

            elif item.item_type == "elixir":
                if hasattr(item, "agility_bonus"):
                    line += f" +AGI {item.agility_bonus}"

            elif item.item_type == "weapon":
                line += f" +DMG {item.strength_bonus}"

            screen.addstr(index + 1, 0, line[:100])

    screen.addstr(20, 0, "Нажми любую клавишу для возврата.")
    screen.refresh()
    screen.getch()