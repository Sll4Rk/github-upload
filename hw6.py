from typing import List, Tuple, Optional, Set


class Clue:
    def __init__(self, total: int, position: Tuple[int, int],
                 is_row: bool, length: int):
        self.total = total
        self.position = position
        self.is_row = is_row
        self.length = length


class Kakuro:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.array = [[-1 for _ in range(width)] for _ in range(height)]
        self.clues: List[Clue] = []

    def set(self, x: int, y: int, value: int) -> None:
        self.array[y][x] = value

    def show_board(self) -> None:
        for row in self.array:
            line = ""
            for field in row:
                if field == -1:
                    line = " ".join([line, "\\"])
                elif field == 0:
                    line = " ".join([line, "."])
                else:
                    line = " ".join([line, str(field)])
            print(line[1:])

    def save(self, filename: str) -> None:
        result: List[List[str]] = []
        for row in self.array:
            line: List[str] = []
            for field in row:
                if field == -1:
                    line.append("\\")
                elif field == 0:
                    line.append(".")
                else:
                    line.append(str(field))
            result.append(line)

        for clue in self.clues:
            x, y = clue.position
            if clue.is_row:
                result[y][x] = "".join([result[y][x], str(clue.total)])
            else:
                result[y][x] = "".join([str(clue.total), result[y][x]])

        with open(filename, "w") as file:
            for row_out in result:
                line_out: str = ""
                for field_out in row_out:
                    line_out = " ".join([line_out, field_out])
                file.write(line_out[1:] + '\n')

    def is_valid(self) -> bool:
        for clue in self.clues:
            used_nums: Set[int] = set()
            if clue.is_row:
                direction = (1, 0)
            else:
                direction = (0, 1)
            x = clue.position[0] + direction[0]
            y = clue.position[1] + direction[1]
            total = 0
            move = clue.length

            while move > 0:
                num = self.array[y][x]
                total += num
                if total > clue.total or (num != 0 and num in used_nums):
                    return False
                used_nums.add(num)
                x += direction[0]
                y += direction[1]
                move -= 1
        return True

    def pick_clue(self) -> Optional[Clue]:
        min_count: Tuple[int, int] = (0, 0)
        for clue in self.clues:
            count = 0
            if clue.is_row:
                direction = (1, 0)
            else:
                direction = (0, 1)

            x = clue.position[0] + direction[0]
            y = clue.position[1] + direction[1]
            for _ in range(clue.length):
                if self.array[y][x] == 0:
                    count += 1
                x += direction[0]
                y += direction[1]

            if min_count[0] == 0:
                min_count = (count, self.clues.index(clue))
            elif count != 0 and count < min_count[0]:
                min_count = (count, self.clues.index(clue))

        if min_count[0] == 0:
            return None
        return self.clues[min_count[1]]

    def is_finished(self) -> bool:
        for clue in self.clues:
            used_nums: Set[int] = set()

            if clue.is_row:
                direction = (1, 0)
            else:
                direction = (0, 1)
            x = clue.position[0] + direction[0]
            y = clue.position[1] + direction[1]
            total = 0
            move = clue.length

            while move > 0:
                num = self.array[y][x]
                total += num
                if num == 0 or num in used_nums:
                    return False
                used_nums.add(num)
                x += direction[0]
                y += direction[1]
                move -= 1

            if total != clue.total:
                return False
        return True

    def solve(self) -> bool:
        clue = self.pick_clue()
        if clue:
            partial: List[int] = []
            if clue.is_row:
                direction = (1, 0)
            else:
                direction = (0, 1)
            x = clue.position[0] + direction[0]
            y = clue.position[1] + direction[1]

            for _ in range(clue.length):
                partial.append(self.array[y][x])
                x += direction[0]
                y += direction[1]
            cells = cells_from_partial(clue.total, partial)

            for cell in cells:
                changed: List[Tuple[Tuple[int, int], int]] = []
                x = clue.position[0] + direction[0]
                y = clue.position[1] + direction[1]

                for i in range(clue.length):
                    changed.append(((x, y), self.array[y][x]))
                    self.array[y][x] = cell[i]
                    x += direction[0]
                    y += direction[1]

                if self.solve() and self.is_valid():
                    return True

                for (x, y), val in changed:
                    self.array[y][x] = val

            return False
        return self.is_finished()


def load_kakuro(filename: str) -> Kakuro:
    kakuro_array: List[List[int]] = []
    clues: List['Clue'] = []
    with open(filename, "r") as file:
        for line in file:
            line_list = line.split()
            kakuro_line = []

            for field in line_list:
                if field == ".":
                    kakuro_line.append(0)
                elif field.isnumeric():
                    kakuro_line.append(int(field))
                else:
                    kakuro_line.append(-1)
                    if field == "\\":
                        continue
                    field_clue = field.split('\\')
                    col, row = field_clue[0], field_clue[1]
                    x, y = len(kakuro_line) - 1, len(kakuro_array)
                    if col != '':
                        clues.append(Clue(int(col), (x, y), False, 0))
                    if row != '':
                        clues.append(Clue(int(row), (x, y), True, 0))
            kakuro_array.append(kakuro_line)
    clues = add_clues_length(clues, kakuro_array)
    kakuro = Kakuro(len(kakuro_line), len(kakuro_array))
    kakuro.array = kakuro_array
    kakuro.clues = sorted(clues, key=lambda x: x.position)
    return kakuro


def add_clues_length(clues: List['Clue'], kakuro: List[List[int]]
                     ) -> List['Clue']:
    for clue in clues:
        length = 0
        if clue.is_row:
            direction = (1, 0)
        else:
            direction = (0, 1)
        x = clue.position[0] + direction[0]
        y = clue.position[1] + direction[1]

        while x < len(kakuro[0]) and y < len(kakuro) and kakuro[y][x] != -1:
            length += 1
            x += direction[0]
            y += direction[1]
        clue.length = length
    return clues


def cells_from_empty(total: int, length: int) -> List[List[int]]:
    if total == 0:
        return []
    unused_nums = {i for i in range(1, 10)}
    return cells_from_empty_with_unused(total, length, unused_nums)


def cells_rec(total: int, length: int, unused_nums: Set[int],
              attempt: List[int]) -> List[List[int]]:
    result: List[List[int]] = []
    length -= 1

    if length == 1:
        if total - 9 > 0:
            return result
        if total in unused_nums:
            attempt[-length] = total
            result.append(attempt.copy())
        return result

    for i in range(1, total):
        if i not in unused_nums:
            continue
        if total - i < 0:
            return result
        unused_nums.remove(i)
        attempt[-length] = i
        result.extend(cells_rec(total - i, length, unused_nums,
                                attempt.copy()))
        attempt[-length] = 0
        unused_nums.add(i)
    return result


def cells_from_empty_with_unused(total: int, length: int,
                                 unused_nums: Set[int]) -> List[List[int]]:
    result: List[List[int]] = []
    check = [i for i in range(9, 0, -1)]

    if sum(check[:length]) < total:
        return []

    if length == 1 and total < 10:
        return [[total]]

    at = [0 for _ in range(length)]

    for i in range(1, 10):
        if i not in unused_nums:
            continue
        unused_nums.remove(i)
        at[0] = i
        attempt = cells_rec(total - i, length, unused_nums, at)
        unused_nums.add(i)
        result.extend(attempt)
    return result


def cells_from_partial(total: int, partial: List[int]) -> List[List[int]]:
    partial_hold: List[Tuple[int, int]] = []
    unused_nums = {i for i in range(1, 10)}
    partial_copy = partial.copy()
    i = 0
    if total < sum(partial_copy):
        return []
    length = len(partial_copy)

    while i < length:
        if partial_copy[i] != 0:
            if partial_copy[i] not in unused_nums:
                return []
            partial_hold.append((i, partial_copy[i]))
            unused_nums.remove(partial_copy[i])
            total -= partial_copy[i]
            partial_copy.pop(i)
            length -= 1
        else:
            i += 1

    if total == 0:
        if len(partial_hold) == len(partial):
            return [partial]
        return []

    result = cells_from_empty_with_unused(total, length, unused_nums)
    for i in range(len(result)):
        for pos, val in partial_hold[::-1]:
            result[i].insert(pos, val)

    for attempt in result:
        if len(attempt) != len(set(attempt)):
            result.remove(attempt)

    return result


# --- Tests ---

# Note: If there is a file with the following name in the current working
# directory, running these tests will overwrite that file!

TEST_FILENAME = "_ib111_tmp_file_"

EXAMPLE = ("\\   11\\  8\\     \\   \\   7\\ 16\\\n"
           "\\16   .   .   11\\   \\4   .   .\n"
           "\\7    .   .     .  7\\13  .   .\n"
           "\\   15\\ 21\\12   .   .    .   .\n"
           "\\12   .   .     .   .   4\\  6\\\n"
           "\\13   .   .     \\6  .    .   .\n"
           "\\17   .   .     \\   \\6   .   .\n")


def write_example(filename: str) -> None:
    with open(filename, "w") as file:
        file.write(EXAMPLE)


def example() -> Kakuro:
    write_example(TEST_FILENAME)
    return load_kakuro(TEST_FILENAME)


def test_1() -> None:
    kakuro = example()
    assert kakuro.width == 7
    assert kakuro.height == 7
    assert kakuro.array == [
        [-1, -1, -1, -1, -1, -1, -1],
        [-1, 0, 0, -1, -1, 0, 0],
        [-1, 0, 0, 0, -1, 0, 0],
        [-1, -1, -1, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, -1, -1],
        [-1, 0, 0, -1, 0, 0, 0],
        [-1, 0, 0, -1, -1, 0, 0],
    ]

    clue_set = {(clue.total, clue.position, clue.is_row, clue.length)
                for clue in kakuro.clues}

    assert clue_set == {
        (11, (1, 0), False, 2),
        (8, (2, 0), False, 2),
        (7, (5, 0), False, 3),
        (16, (6, 0), False, 3),
        (16, (0, 1), True, 2),
        (11, (3, 1), False, 3),
        (4, (4, 1), True, 2),
        (7, (0, 2), True, 3),
        (7, (4, 2), False, 3),
        (13, (4, 2), True, 2),
        (15, (1, 3), False, 3),
        (21, (2, 3), False, 3),
        (12, (2, 3), True, 4),
        (12, (0, 4), True, 4),
        (4, (5, 4), False, 2),
        (6, (6, 4), False, 2),
        (13, (0, 5), True, 2),
        (6, (3, 5), True, 3),
        (17, (0, 6), True, 2),
        (6, (4, 6), True, 2),
    }


def test_2() -> None:
    kakuro = example()

    print("show_board result:")
    kakuro.show_board()
    print("---")

    print("save result:")
    kakuro.save(TEST_FILENAME)
    with open(TEST_FILENAME) as file:
        print(file.read(), end="")
    print("---")


def test_3() -> None:
    kakuro = example()
    assert kakuro.is_valid()

    kakuro.set(2, 1, 9)
    assert not kakuro.is_valid()

    kakuro.set(2, 1, 0)
    assert kakuro.is_valid()

    kakuro.set(1, 2, 1)
    kakuro.set(2, 2, 1)
    assert not kakuro.is_valid()

    kakuro.set(1, 2, 0)
    kakuro.set(2, 2, 0)
    assert kakuro.is_valid()

    kakuro.set(5, 5, 4)
    assert kakuro.is_valid()


def test_4() -> None:
    assert cells_from_empty(13, 2) \
        == [[4, 9], [5, 8], [6, 7], [7, 6], [8, 5], [9, 4]]

    assert cells_from_partial(12, [0, 0, 6, 0]) \
        == [[1, 2, 6, 3], [1, 3, 6, 2], [2, 1, 6, 3],
            [2, 3, 6, 1], [3, 1, 6, 2], [3, 2, 6, 1]]


def test_5() -> None:
    kakuro = example()
    clue = kakuro.pick_clue()
    assert clue is not None
    assert clue.total == 16
    assert clue.position == (0, 1)
    assert clue.is_row
    assert clue.length == 2

    kakuro.set(6, 5, 1)
    clue = kakuro.pick_clue()
    assert clue is not None
    assert clue.total == 6
    assert clue.position == (6, 4)
    assert not clue.is_row
    assert clue.length == 2

    kakuro.set(6, 6, 5)
    clue = kakuro.pick_clue()
    assert clue is not None
    assert clue.total == 6
    assert clue.position == (4, 6)
    assert clue.is_row
    assert clue.length == 2


def test_6() -> None:
    kakuro = example()
    kakuro.solve()
    assert kakuro.array == [
        [-1, -1, -1, -1, -1, -1, -1],
        [-1, 9, 7, -1, -1, 1, 3],
        [-1, 2, 1, 4, -1, 4, 9],
        [-1, -1, -1, 5, 1, 2, 4],
        [-1, 1, 5, 2, 4, -1, -1],
        [-1, 6, 7, -1, 2, 3, 1],
        [-1, 8, 9, -1, -1, 1, 5],
    ]


if __name__ == '__main__':
    test_1()
    # uncomment to visually check the results:
    # test_2()
    test_3()
    test_4()
    test_5()
    test_6()
