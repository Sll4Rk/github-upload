from typing import List, Tuple, Optional
from random import choice

INVALID_POSITION = 0
EMPTY_POSITION = 1
ROUND_OVER = 2
PLAY_AGAIN = 3


def init(size: int, start: int) -> Tuple[List[int], List[int]]:
    player_side = [start for _ in range(size)]
    player_side.append(0)
    return (player_side, player_side.copy())


def play(our: List[int], their: List[int], position: int) -> int:
    if position > len(our) - 2 or position < 0:
        return INVALID_POSITION
    if our[position] == 0:
        return EMPTY_POSITION
    return distribution(our, their, position)


def distribution(our: List[int], their: List[int], position: int) -> int:
    ball_count, our[position], pos = our[position], 0, 0
    ball_count, pos = distribute_to_player(our, ball_count, position + 1)
    if ball_count == 0:
        steal_balls(our, their, pos)
    while ball_count > 0:
        ball_count, pos = distribute_to_player(their, ball_count,
                                               isEnemy=True)
        if ball_count == 0:
            break
        ball_count, pos = distribute_to_player(our, ball_count)
        if ball_count == 0:
            steal_balls(our, their, pos)
    if pos == len(our) - 1:
        return PLAY_AGAIN
    return ROUND_OVER


def steal_balls(our: List[int], their: List[int],
                pos: int) -> None:
    their_pos = len(their) - 2 - pos
    if pos != len(our) - 1 \
       and our[pos] == 1 and \
       their[their_pos] != 0:
        our[len(our) - 1] += 1 + their[their_pos]
        our[pos], their[their_pos] = 0, 0


def distribute_to_player(player_side: List[int],
                         ball_count: int, position: int = 0,
                         isEnemy: bool = False) -> Tuple[int, int]:
    if isEnemy:
        enemy_bank = 1
    else:
        enemy_bank = 0
    pos = 0
    for i in range(position, len(player_side) - enemy_bank):
        if ball_count == 0:
            break
        player_side[i] += 1
        ball_count -= 1
        pos = i
    return ball_count, pos


def random_choice(our: List[int]) -> Optional[int]:
    rng = []
    for i in range(len(our) - 1):
        if our[i] != 0:
            rng.append(i)
    if len(rng) == 0:
        return None
    return choice(rng)


def run_random_game(size: int, start: int) -> Tuple[int, int]:
    player_A, player_B = init(size, start)
    while True:
        if player_moving(player_A, player_B) is False:
            return result(player_A, player_B)
        if player_moving(player_B, player_A) is False:
            return result(player_A, player_B)


def result(player_A: List[int], player_B: List[int]) -> Tuple[int, int]:
    player_A[-1] += sum(player_A[:-1])
    player_B[-1] += sum(player_B[:-1])
    return (player_A[-1], player_B[-1])


def player_moving(player_A: List[int], player_B: List[int]) -> bool:
    pos = random_choice(player_A)
    status = 0
    if pos is not None:
        status = play(player_A, player_B, pos)
        print(player_A, player_B)
    else:
        return False
    while status == PLAY_AGAIN:
        pos = random_choice(player_A)
        if pos is None:
            break
        status = play(player_A, player_B, pos)
        print(player_A, player_B)
    return True


def main() -> None:
    # --- init ---

    assert init(6, 3) \
        == ([3, 3, 3, 3, 3, 3, 0], [3, 3, 3, 3, 3, 3, 0])

    assert init(9, 7) \
        == ([7, 7, 7, 7, 7, 7, 7, 7, 7, 0], [7, 7, 7, 7, 7, 7, 7, 7, 7, 0])

    # --- play ---

    our = [3, 0, 6, 0]
    their = [3, 3, 3, 0]
    assert play(our, their, -1) == INVALID_POSITION
    assert our == [3, 0, 6, 0]
    assert their == [3, 3, 3, 0]

    our = [3, 0, 6, 0]
    their = [3, 3, 3, 0]
    assert play(our, their, 0) == PLAY_AGAIN
    assert our == [0, 1, 7, 1]
    assert their == [3, 3, 3, 0]

    our = [3, 0, 6, 0]
    their = [3, 3, 3, 0]
    assert play(our, their, 1) == EMPTY_POSITION
    assert our == [3, 0, 6, 0]
    assert their == [3, 3, 3, 0]

    our = [3, 0, 6, 0]
    their = [3, 3, 3, 0]
    assert play(our, their, 2) == ROUND_OVER
    assert our == [4, 0, 0, 6]
    assert their == [4, 0, 4, 0]

    our = [3, 0, 6, 0]
    their = [3, 3, 3, 0]
    assert play(our, their, 3) == INVALID_POSITION
    assert our == [3, 0, 6, 0]
    assert their == [3, 3, 3, 0]

    # --- random_choice ---

    assert random_choice([1, 2, 3, 4, 0]) in [0, 1, 2, 3]

    assert random_choice([3, 3, 0, 3, 3, 7]) in [0, 1, 3, 4]

    assert random_choice([0, 0, 0, 1]) is None


if __name__ == '__main__':
    print(run_random_game(1, 1))
    main()
