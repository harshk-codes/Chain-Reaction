import pygame as py
import networkx as nx
import sys
import button

BLACK = (21, 21, 21)
WHITE = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 720
GRID_ROWS = 6
GRID_COLS = 6
CELL_WIDTH = WINDOW_WIDTH // GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT // GRID_ROWS
max_depth = 10

# initializing game
py.init()

# icons
icon = py.image.load('icon.png')
py.display.set_icon(icon)

# creating start screen window
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# game variables
game_paused = False
game_over = False
winner = None

# define font
text_font = py.font.Font(None, 100)

# button images
start_img = py.image.load("start.png").convert_alpha()
exit_img = py.image.load("exit.png").convert_alpha()
background_img = py.image.load("background.jpg")

# button instances
start_button = button.Button(270, 300, start_img, 0.8)
exit_button = button.Button(280, 450, exit_img, 0.7)
exit_button_gameover = button.Button(280, 340, exit_img, 0.7)

# text
head_text = text_font.render('CHAIN REACTION', True, (169, 29, 58))
red_win_text = text_font.render("RED WINS", True, (255, 0, 0))
blue_win_text = text_font.render("BLUE WINS", True, (0, 0, 255))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def main_menu():
    global game_over, winner
    game_over = False
    winner = None
    run = True
    while run:
        screen.blit(background_img, (-300, -100))
        screen.blit(head_text, (50, 150))
        start_button.draw(screen)
        exit_button.draw(screen)

        # Check if the exit button is clicked
        if exit_button.check_click():
            run = False

        # start if the start button is clicked
        if start_button.check_click():
            game()

        # event handler
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False

        py.display.update()

def game():
    global game_over, winner
    # Create a grid graph
    def create_grid_graph(height, width):
        G = nx.Graph()
        for i in range(height):
            for j in range(width):
                node = i * width + j
                G.add_node(node, pos=(i, j), value=0, color=None)
                if i > 0:
                    G.add_edge(node, (i - 1) * width + j)
                if j > 0:
                    G.add_edge(node, i * width + (j - 1))
        return G

    # Draw the graph
    def draw_grid_graph(G, current_player):
        pos = nx.get_node_attributes(G, 'pos')
        for node in G.nodes():
            pos_x, pos_y = pos[node]
            value = G.nodes[node]['value']
            color = G.nodes[node]['color']
            if color == 'red':
                py.draw.circle(screen, RED,
                               (pos_x * CELL_WIDTH + CELL_WIDTH // 2, pos_y * CELL_HEIGHT + CELL_HEIGHT // 2),
                               min(CELL_WIDTH, CELL_HEIGHT) // 4)
            elif color == 'blue':
                py.draw.circle(screen, BLUE,
                               (pos_x * CELL_WIDTH + CELL_WIDTH // 2, pos_y * CELL_HEIGHT + CELL_HEIGHT // 2),
                               min(CELL_WIDTH, CELL_HEIGHT) // 4)
            py.draw.rect(screen, current_player, (pos_x * CELL_WIDTH, pos_y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT),
                         1)
            font = py.font.Font(None, 36)
            text_surface = font.render(str(value), True, WHITE)
            screen.blit(text_surface, (pos_x * CELL_WIDTH + 10, pos_y * CELL_HEIGHT + 10))

    # function for game logic
    def logic(selected_cell, G, max_depth):
        if max_depth == 0:
            return

        if grid_graph.nodes[selected_cell]['value'] >= grid_graph.degree[selected_cell]:
            grid_graph.nodes[selected_cell]['value'] = 0

            for neighbor in grid_graph.neighbors(selected_cell):
                grid_graph.nodes[neighbor]['value'] += 1
                grid_graph.nodes[neighbor]['color'] = grid_graph.nodes[selected_cell]['color']
                logic(neighbor, G, max_depth - 1)

                # Draw circle in neighbor cell if it has the same color
                if grid_graph.nodes[neighbor]['color'] == grid_graph.nodes[selected_cell]['color']:
                    pos = nx.get_node_attributes(G, 'pos')
                    pos_x, pos_y = pos[neighbor]
                    color = grid_graph.nodes[neighbor]['color']
                    if color == 'red':
                        py.draw.circle(screen, RED,
                                       (pos_x * CELL_WIDTH + CELL_WIDTH // 2,
                                        pos_y * CELL_HEIGHT + CELL_HEIGHT // 2),
                                       min(CELL_WIDTH, CELL_HEIGHT) // 4)
                    elif color == 'blue':
                        py.draw.circle(screen, BLUE,
                                       (pos_x * CELL_WIDTH + CELL_WIDTH // 2,
                                        pos_y * CELL_HEIGHT + CELL_HEIGHT // 2),
                                       min(CELL_WIDTH, CELL_HEIGHT) // 4)

            if grid_graph.nodes[selected_cell]['value'] == 0:
                grid_graph.nodes[selected_cell]['color'] = None

        else:
            return

    # function for winning condition check
    def wincheck(G, source):
        global game_over, winner
        red_count = 0
        blue_count = 0
        non_empty = 0
        bfs_nodes = nx.bfs_tree(G, source)
        for node in bfs_nodes:
            if G.nodes[node]['color'] == 'red':
                red_count += 1
                non_empty += 1

            elif G.nodes[node]['color'] == 'blue':
                blue_count += 1
                non_empty += 1

        # blue wins:
        if non_empty >= 2 and red_count == 0:
            game_over = True
            winner = 'blue'

        # red wins:
        if non_empty >= 2 and blue_count == 0:
            game_over = True
            winner = 'red'

    # Function to draw a grid
    def draw_grid():
        for x in range(0, WINDOW_WIDTH, CELL_WIDTH):
            for y in range(0, WINDOW_HEIGHT, CELL_HEIGHT):
                rect = py.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
                py.draw.rect(screen, WHITE, rect, 1)

    # Game loop
    running = True
    current_player = RED  # Player 1 starts
    grid_graph = create_grid_graph(GRID_ROWS, GRID_COLS)

    while running:
        # Event handling
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.MOUSEBUTTONDOWN and not game_over:
                mouse_pos = py.mouse.get_pos()
                cell_row = mouse_pos[0] // CELL_WIDTH
                cell_col = mouse_pos[1] // CELL_HEIGHT
                selected_cell = cell_row * GRID_COLS + cell_col
                if grid_graph.nodes[selected_cell]['color'] is None or \
                        (grid_graph.nodes[selected_cell]['color'] == 'red' and current_player == RED) or \
                        (grid_graph.nodes[selected_cell]['color'] == 'blue' and current_player == BLUE):
                    grid_graph.nodes[selected_cell]['color'] = 'red' if current_player == RED else 'blue'
                    grid_graph.nodes[selected_cell]['value'] += 1
                    logic(selected_cell, grid_graph, max_depth - 1)
                    wincheck(grid_graph, selected_cell)  # winning condition check
                    if not game_over:
                        current_player = RED if current_player == BLUE else BLUE  # Change player

        # Screen background
        screen.fill(BLACK)

        # Draw grid
        draw_grid()

        # Draw the graph over the grid
        draw_grid_graph(grid_graph, current_player)

        if game_over:
            if winner == 'red':
                screen.fill(BLACK)
                screen.blit(red_win_text, (180, 300))
            elif winner == 'blue':
                screen.fill(BLACK)
                screen.blit(blue_win_text, (180, 300))
            exit_button_gameover.draw(screen)
            if exit_button_gameover.check_click():
                running = False

        py.display.update()

main_menu()
py.quit()
