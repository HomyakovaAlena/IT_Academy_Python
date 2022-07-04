import random
import keyboard
import click
import json
import os


def randomize(matrix=0, size=4):
    if matrix == 0:
        matrix = [[0 for cell in range(size)]
                  for row in range(size)]

    coordinates = [(row, cell) for cell in range(size)
                   for row in range(size) if matrix[row][cell] == 0]

    x, y = random.choice(coordinates)
    matrix[x][y] = random.choice([2, 4])
    return matrix


def show_state(state):
    n_cols = state['size']
    n_rows = state['size']
    w_cell = 4
    h_cell = 1
    matrix = state['matrix']
    score = state['score']
    best_score = state['best_score']
    matrix_display = [(cell, ' ')[cell < 1] for row in matrix for cell in row]

    hor_line = ('+' + '-' * w_cell) * n_cols + '+\n'
    line_with_gaps = ('|' + '%s') * n_cols + '|\n'
    table = (hor_line + line_with_gaps * h_cell) * n_rows + hor_line

    print('\n' * 50)
    print('SCORE:', score, '  BEST_SCORE:', best_score)
    print(table % tuple((str(cell).center(w_cell, ' ')
          for cell in matrix_display)))


def step(state, cmd):
    n_turns = {  # main direction is left
        'left': (0, 0),
        'up': (3, 1),
        'down': (1, 3),
        'right': (2, 2),
        'a': (0, 0),
        'w': (3, 1),
        's': (1, 3),
        'd': (2, 2),
    }
    before, after = n_turns[cmd]

    matrix = state['matrix']
    size = state['size']

    for _ in range(before):
        matrix = turn(matrix)
    copy_matrix = matrix

    matrix = remove_zeros(matrix)
    matrix, score = aggregate(matrix)
    matrix = append_zeros(matrix, size)

    if copy_matrix != matrix:
        matrix = randomize(matrix, size)

    for _ in range(after):
        matrix = turn(matrix)

    state['matrix'] = matrix
    state['score'] += score
    if state['score'] > state['best_score']:
        state['best_score'] = state['score']

    state['is_finished'] = False
    save_state(state)


def turn(matrix):
    len_rows = len(matrix)
    len_columns = len(matrix[0])

    new_matrix = [[0 for cell in row] for row in matrix]
    for row_index in range(len_rows):
        for column_index in range(len_columns):
            new_matrix[column_index][row_index] = matrix[len_rows -
                                                         row_index - 1][column_index]
    return new_matrix


def remove_zeros(matrix):
    matrix = [[cell for cell in row if cell != 0] for row in matrix]
    return matrix


def aggregate(matrix):
    rows = len(matrix)
    new_matrix = []
    score = 0
    for i in range(rows):
        new_matrix.append([])
        fast = 1
        j = 0
        while j < len(matrix[i]):
            if fast == len(matrix[i]):
                new_matrix[i].append(matrix[i][j])
                break
            elif matrix[i][j] == matrix[i][fast]:
                score += matrix[i][j] * 2
                new_matrix[i].append(matrix[i][j] * 2)
                j += 2
                fast += 2
            else:
                new_matrix[i].append(matrix[i][j])
                j += 1
                fast += 1
    return new_matrix, score


def append_zeros(matrix, size):
    rows = len(matrix)
    for i in range(rows):
        matrix[i].extend([0]*(size - len(matrix[i])))
    return matrix


def save_state(state):
    with open('state.json', 'w') as js_fh:
        state = json.dump(state, js_fh, indent='    ')


def init_state(size):
    if not os.path.exists("state.json"):
        state = {
            'matrix': randomize(0, size),
            'score': 0,
            'best_score': 0,
            'is_finished': False,
            'size': size,
        }
        save_state(state)
    else:
        with open('state.json', 'r') as js_fh:
            state = json.loads(js_fh.read())
            if state['is_finished'] == True:
                state['matrix'] = randomize(0, size)
                state['score'] = 0
                state['is_finished'] = False
                state['size'] = size
                state.pop('continue', None)
                save_state(state)
    return state


def return_state():
    with open('state.json', 'r') as js_fh:
        state = json.loads(js_fh.read())
    return state


def new_event(state, cmd):
    if cmd == 'esc':
        state['is_finished'] = True
        save_state(state)
    elif cmd == 'new':
        pass
    elif cmd in ['left', 'right', 'up', 'down', 'a', 'd', 'w', 's']:
        step(state, cmd)
    return state


def is_win(state):
    if max(el for row in state['matrix'] for el in row) >= 2048:
        if_continue = input(
            'YOU WIN!\nWould you like to continue?\n(press"y" for "Yes" or "n" for "No"')
        if if_continue != 'y':
            state['is_finished'] = True
            save_state(state)
        else:
            state['continue'] = True
            save_state(state)
            return False
    return False


def is_loose(state):
    matrix = state['matrix']
    if all([cell for row in matrix for cell in row]) != 0 and all([aggregate(matrix)[0] == matrix, aggregate(turn(matrix))[0] == turn(matrix)]):
        state['is_finished'] = True
        save_state(state)
        print('Game over!')
        return True
    return False


@click.command()
@click.option('--size', default=4, help='size of the game grid (rows and columns')
def run(size):
    state = init_state(size)
    show_state(state)

    while True:
        event = keyboard.read_event()
        if event.event_type != 'up':
            continue
        cmd = event.name
        state = new_event(state, cmd)
        show_state(state)
        if not 'continue' in state:
            if is_win(state):
                break
        if is_loose(state):
            break
        if state['is_finished'] == True:
            break


if __name__ == '__main__':
    run()
