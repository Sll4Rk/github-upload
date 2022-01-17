from typing import List, Tuple, Optional

Block = List[Tuple[int, int]]

BLOCK_I, BLOCK_J, BLOCK_L, BLOCK_S, BLOCK_Z, BLOCK_T, BLOCK_O = range(7)
LEFT, RIGHT, ROTATE_CW, ROTATE_CCW, DOWN, DROP, QUIT = range(7)

WALL = "##"
SQUARE = "[]"
EMPTY = "  "

Arena = List[List[bool]]


def coords(block_type: int) -> Block:
    if block_type == BLOCK_I:
        return [(0, 0), (0, -1), (0, 1), (0, 2)]
    if block_type == BLOCK_J:
        return [(0, 0), (0, -1), (0, 1), (-1, 1)]
    if block_type == BLOCK_L:
        return [(0, 0), (0, -1), (0, 1), (1, 1)]
    if block_type == BLOCK_S:
        return [(0, 0), (1, 0), (0, 1), (-1, 1)]
    if block_type == BLOCK_Z:
        return [(0, 0), (-1, 0), (0, 1), (1, 1)]
    if block_type == BLOCK_T:
        return [(0, 0), (-1, 0), (1, 0), (0, 1)]
    return [(0, 0), (1, 0), (1, 1), (0, 1)]


def rotate_cw(coords: Block) -> Block:
    new_coords: Block = []
    for x, y in coords:
        new_coords.append((-y, x))
    return new_coords


def rotate_ccw(coords: Block) -> Block:
    new_coords: Block = []
    for x, y in coords:
        new_coords.append((y, -x))
    return new_coords


def new_arena(cols: int, rows: int) -> Arena:
    arena: Arena = []
    for y in range(rows):
        arena.append([])
        for _ in range(cols):
            arena[y].append(False)
    return arena


def is_occupied(arena: Arena, x: int, y: int) -> bool:
    cols = len(arena[0])
    rows = len(arena)
    if x < 0 or x >= cols or y >= rows or y < 0:
        return True
    return arena[y][x]


def set_occupied(arena: Arena, x: int, y: int, occupied: bool) -> None:
    arena[y][x] = occupied
    return


def draw(arena: Arena, score: int) -> None:
    line = ""
    for y in arena:
        line += WALL
        for x in y:
            if x:
                line += SQUARE
            else:
                line += EMPTY
        print(line + WALL)
        line = ""
    for _ in range(len(arena[0]) + 2):
        line += WALL
    print(line)
    print("  Score:".ljust(2 * len(arena[0]) + 2 - len(str(score)))
          + str(score))


def next_block() -> Block:
    # change this function as you wish
    return coords(BLOCK_S)


def poll_event() -> int:
    # change this function as you wish
    return int(input("Event number (0-6): "))


def check_lines(arena: Arena) -> int:
    count = 0
    for i in range(len(arena)):
        if all(arena[i]):
            count += 1
            for k in range(len(arena[0])):
                arena[i][k] = False
    for i in range(len(arena)):
        if not any(arena[i]):
            move_line_down(arena, i)
    return count


def move_line_down(arena: Arena, line_index: int) -> None:
    for y in range(line_index, -1, -1):
        for x in range(len(arena[0])):
            if arena[y][x]:
                down(arena, (0, 0), [(x, y)])


def get_block_center_x(block: Block) -> int:
    x = set()
    for tpl in block:
        x.add(tpl[0])
    length = len(x)
    if length % 2 == 0:
        length = length // 2 - 1
    else:
        length //= 2
    return sorted(x)[length]


def place_block(arena: Arena, block: Block
                ) -> Optional[Tuple[int, int]]:
    arena_center = len(arena[0]) // 2
    if len(arena[0]) % 2 == 0:
        arena_center -= 1
    block_center_x = get_block_center_x(block)
    move = 0
    for x, y in block:
        if y < move:
            move = y
    move = abs(move)
    for x, y in block:
        if is_occupied(arena, arena_center + x, move + y):
            return None
    for x, y in block:
        set_occupied(arena, arena_center + x, move + y, True)
    block_position = (arena_center, move)
    while block_center_x != 0:
        side_move(arena, block_position, block, -block_center_x)
        if block_center_x > 0:
            block_center_x -= 1
        else:
            block_center_x += 1
    return block_position


def change_in_arena(arena: Arena, pos: Tuple[int, int],
                    new_block: Block, old_block: Block) -> None:
    b_x, b_y = pos
    for x, y in old_block:
        set_occupied(arena, b_x + x, b_y + y, False)
    for x, y in new_block:
        set_occupied(arena, b_x + x, b_y + y, True)
    return None


def do_action(arena: Arena, block_position:
              Tuple[int, int], block: Block
              ) -> Tuple[Block, Optional[Tuple[int, int]]]:
    action = poll_event()
    if action == LEFT:
        return (block, side_move(arena, block_position, block, -1))
    elif action == RIGHT:
        return (block, side_move(arena, block_position, block, 1))
    elif action == DOWN:
        return (block, down(arena, block_position, block))

    elif action == ROTATE_CW:
        if not check_rotate_cw(arena, block_position, block):
            old_block = block
            block = rotate_cw(block)
            change_in_arena(arena, block_position, block, old_block)
        return (block, block_position)

    elif action == ROTATE_CCW:
        if not check_rotate_ccw(arena, block_position, block):
            old_block = block
            block = rotate_ccw(block)
            change_in_arena(arena, block_position, block, old_block)
        return (block, block_position)

    elif action == DROP:
        return (block, drop(arena, block_position, block))
    return (block, None)


def check_rotate_cw(arena: Arena, block_position: Tuple[int, int],
                    block: Block) -> bool:
    new_block = rotate_cw(block)
    b_x, b_y = block_position
    block_parts = get_block_parts_pos(block_position, block)
    for x, y in new_block:
        if is_occupied(arena, b_x + x, b_y + y) and \
           (b_x + x, b_y + y) not in block_parts:
            return True
    return False


def check_rotate_ccw(arena: Arena, block_position: Tuple[int, int],
                     block: Block) -> bool:
    new_block = rotate_ccw(block)
    b_x, b_y = block_position
    block_parts = get_block_parts_pos(block_position, block)
    for x, y in new_block:
        if is_occupied(arena, b_x + x, b_y + y) and \
           (b_x + x, b_y + y) not in block_parts:
            return True
    return False


def get_block_parts_pos(block_position: Tuple[int, int],
                        block: Block) -> Block:
    new_block: Block = []
    b_x, b_y = block_position
    for x, y in block:
        new_block.append((b_x + x, b_y + y))
    return new_block


def side_move(arena: Arena, block_position: Tuple[int, int],
              block: Block, direction: int) -> Tuple[int, int]:
    b_x, b_y = block_position
    new_block: Block = []
    block_parts = get_block_parts_pos(block_position, block)
    for x, y in block:
        if is_occupied(arena, b_x + x + direction,
                       b_y + y) and\
                       (b_x + x + direction, b_y + y) not in\
                       block_parts:
            return block_position
    for x, y in block:
        set_occupied(arena, b_x + x, b_y + y, False)
    for x, y in block:
        new_block.append((b_x + x + direction, b_y + y))
        set_occupied(arena, b_x + x + direction, b_y + y, True)
    return (b_x + direction, b_y)


def down(arena: Arena, block_position: Tuple[int, int],
         block: Block) -> Tuple[int, int]:
    b_x, b_y = block_position
    block_parts = get_block_parts_pos(block_position, block)
    for x, y in block:
        if is_occupied(arena, b_x + x, b_y + y + 1) and\
           (b_x + x, b_y + y + 1) not in\
           block_parts:
            return block_position
    for x, y in block:
        set_occupied(arena, b_x + x, b_y + y, False)
    for x, y in block:
        set_occupied(arena, b_x + x, b_y + y + 1, True)
    return (b_x, b_y + 1)


def drop(arena: Arena, block_position: Tuple[int, int],
         block: Block) -> Tuple[int, int]:
    old_block_position = block_position
    new_block_position = down(arena, block_position, block)
    while old_block_position != new_block_position:
        old_block_position = new_block_position
        new_block_position = down(arena, old_block_position, block)
    return new_block_position


def check_under(arena: Arena, block_position: Tuple[int, int],
                block: Block) -> bool:
    b_x, b_y = block_position
    block_parts = get_block_parts_pos(block_position, block)
    for x, y in block:
        if is_occupied(arena, b_x + x, b_y + y + 1)\
           and (b_x + x, b_y + y + 1) not in\
           block_parts:
            return True
    return False


def play(arena: Arena) -> int:
    score = 0
    block = next_block()
    block_position = place_block(arena, block)
    if block_position is None:
        return score
    while True:
        if check_under(arena, block_position, block):
            score += check_lines(arena) ** 2
            block = next_block()
            block_position = place_block(arena, block)
        draw(arena, score)
        if block_position is None:
            return score
        block, block_position = do_action(arena, block_position, block)
        if block_position is None:
            draw(arena, score)
            return score
