import tkinter as tk

# change hw2 below if your file name is different
import hw2 as student

# game parameters; feel free to change them
SIZE = 6
START = 3

BORDER = 32
CELL_SIZE = 64
MSG_FONT = ('system', '12')
FONT = ('system', '16')
BANK_FONT = ('system', '32')

TOP = 2 * BORDER
BOTTOM = 2 * BORDER + 2 * CELL_SIZE
LEFT = BORDER
RIGHT = BORDER + (SIZE + 4) * CELL_SIZE


class Game:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.top, self.bottom = student.init(SIZE, START)


def draw_cell(canvas: tk.Canvas, x: int, y: int,
              num: int, fill: str = "") -> None:
    canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=fill)
    canvas.create_text(x + CELL_SIZE // 2, y + CELL_SIZE // 2,
                       text=str(num), font=FONT)


def draw(canvas: tk.Canvas, game: Game, msg: str = "") -> None:
    canvas.delete('all')

    canvas.create_rectangle(LEFT, TOP, RIGHT, BOTTOM)

    for i in range(SIZE):
        x = LEFT + (2 + i) * CELL_SIZE
        for y, row, index in ((TOP, game.top, SIZE - 1 - i),
                              (TOP + CELL_SIZE, game.bottom, i)):
            draw_cell(canvas, x, y, row[index])

    for x, row in ((LEFT + CELL_SIZE, game.top),
                   (RIGHT - CELL_SIZE, game.bottom)):
        canvas.create_text(x, TOP + CELL_SIZE,
                           text=str(row[-1]), font=BANK_FONT)

    canvas.create_text((LEFT + RIGHT) // 2, BOTTOM + 2 * BORDER,
                       text=msg, font=MSG_FONT)


def reset_and_draw(canvas: tk.Canvas, game: Game) -> None:
    game.reset()
    draw(canvas, game)


def click(event: tk.Event, canvas: tk.Canvas, game: Game) -> None:
    lbound = LEFT + 2 * CELL_SIZE
    rbound = RIGHT - 2 * CELL_SIZE
    if not (TOP < event.y < BOTTOM and lbound < event.x < rbound) \
            or (event.x - lbound) % CELL_SIZE == 0 \
            or event.y == TOP + CELL_SIZE:
        return  # ignore clicks outside and directly on boundary lines

    i = (event.x - lbound) // CELL_SIZE
    our, their = game.bottom, game.top

    if event.y < TOP + CELL_SIZE:
        i = SIZE - 1 - i
        our, their = their, our

    result = student.play(our, their, i)

    assert result != student.INVALID_POSITION, \
        "This result should not be possible here!"

    if result == student.EMPTY_POSITION:
        msg = "This position is empty. Try again."
    elif result == student.PLAY_AGAIN:
        msg = "Last token ended in the bank. Play again."
    else:
        msg = "Round over, switch to the next player."

    draw(canvas, game, msg)


def highlight_random(event: tk.Event, canvas: tk.Canvas, game: Game) -> None:
    top = event.y_root < BOTTOM // 2
    row = game.top if top else game.bottom

    result = student.random_choice(row)
    if result is None:
        draw(canvas, game, "Found no possible moves.")
        return

    assert 0 <= result < SIZE and row[result] > 0, \
        f"Invalid move returned from random_choice: {result}."

    if top:
        y = TOP
        x = LEFT + (1 + SIZE - result) * CELL_SIZE
    else:
        y = TOP + CELL_SIZE
        x = LEFT + (2 + result) * CELL_SIZE

    draw(canvas, game, "Random move selected.")
    draw_cell(canvas, x, y, row[result], fill="red")


def main() -> None:
    root = tk.Tk()
    canvas = tk.Canvas(
        width=RIGHT + BORDER,
        height=BOTTOM + 3 * BORDER,
    )

    game = Game()
    draw(canvas, game)

    for y in BORDER, BOTTOM + BORDER:
        button = tk.Button(canvas, text="Random")
        button.place(x=(LEFT + RIGHT) // 2, y=y, anchor=tk.CENTER)
        button.bind("<Button-1>",
                    lambda ev: highlight_random(ev, canvas, game))

    canvas.bind("<Button-1>", lambda ev: click(ev, canvas, game))
    canvas.bind_all("r", lambda _: reset_and_drawdraw(canvas, game))
    canvas.bind_all("q", lambda _: root.destroy())

    canvas.pack()
    root.mainloop()


if __name__ == '__main__':
    main()