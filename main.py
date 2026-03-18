
import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
GRID_SIZE = 6
CELL_SIZE = 60
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 100
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (34, 177, 76)
BLUE = (0, 112, 192)
RED = (192, 0, 0)
YELLOW = (255, 192, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (220, 220, 220)

COLORS = [GREEN, BLUE, RED, YELLOW, PURPLE, CYAN, ORANGE]


@dataclass
class Position:
    """Represents a 2D position"""
    x: int
    y: int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class BlockShape(Enum):
    """Different block shapes available"""
    SINGLE = [(0, 0)]
    DOUBLE = [(0, 0), (1, 0)]
    TRIPLE = [(0, 0), (1, 0), (2, 0)]
    L_SHAPE = [(0, 0), (1, 0), (1, 1)]
    SQUARE = [(0, 0), (1, 0), (0, 1), (1, 1)]
    T_SHAPE = [(0, 0), (1, 0), (2, 0), (1, 1)]
    Z_SHAPE = [(0, 0), (1, 0), (1, 1), (2, 1)]


class Block:
    """Represents a playable block"""
    
    def __init__(self, shape: BlockShape, color: Tuple[int, int, int], position: Position):
        self.shape = shape
        self.color = color
        self.position = position
        self.cells = [Position(x, y) for x, y in shape.value]
        self.is_placed = False

    def get_global_positions(self) -> List[Position]:
        """Get the absolute positions of all cells in this block"""
        return [self.position + cell for cell in self.cells]

    def move(self, dx: int, dy: int):
        """Move the block by the given delta"""
        self.position = Position(self.position.x + dx, self.position.y + dy)

    def rotate(self):
        """Rotate the block 90 degrees clockwise"""
        # Rotate each cell 90 degrees around origin
        new_cells = []
        for cell in self.cells:
            new_x = cell.y
            new_y = -cell.x
            new_cells.append((new_x, new_y))

        # Normalize to positive coordinates
        if new_cells:
            min_x = min(x for x, y in new_cells)
            min_y = min(y for x, y in new_cells)
            new_cells = [(x - min_x, y - min_y) for x, y in new_cells]

        self.cells = [Position(x, y) for x, y in new_cells]

    def contains_position(self, pos: Position) -> bool:
        """Check if this block contains a given position"""
        return pos in self.get_global_positions()


class GameBoard:
    """Manages the game grid and block placement"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def is_valid_position(self, block: Block) -> bool:
        """Check if block position is valid (all cells within bounds and not occupied)"""
        for pos in block.get_global_positions():
            if pos.x < 0 or pos.x >= self.width or pos.y < 0 or pos.y >= self.height:
                return False
            if self.grid[pos.y][pos.x] is not None:
                return False
        return True

    def place_block(self, block: Block) -> bool:
        """Place a block on the board"""
        if not self.is_valid_position(block):
            return False

        for pos in block.get_global_positions():
            self.grid[pos.y][pos.x] = block.color

        block.is_placed = True
        return True

    def clear_lines(self) -> int:
        """Clear complete rows and return the number cleared"""
        lines_to_clear = []

        for y in range(self.height):
            if all(self.grid[y][x] is not None for x in range(self.width)):
                lines_to_clear.append(y)

        # Remove cleared lines
        for y in reversed(lines_to_clear):
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(self.width)])

        return len(lines_to_clear)

    def clear_columns(self) -> int:
        """Clear complete columns and return the number cleared"""
        columns_to_clear = []

        for x in range(self.width):
            if all(self.grid[y][x] is not None for y in range(self.height)):
                columns_to_clear.append(x)

        # Remove cleared columns
        for x in reversed(columns_to_clear):
            for y in range(self.height):
                self.grid[y][x] = None

        return len(columns_to_clear)

    def get_available_moves(self, block: Block) -> List[Position]:
        """Get all valid positions where the block can be placed"""
        available = []
        for y in range(self.height):
            for x in range(self.width):
                block.position = Position(x, y)
                if self.is_valid_position(block):
                    available.append(Position(x, y))
        return available


class Game:
    """Main game logic"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Block Puzzle Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        self.board = GameBoard(GRID_SIZE, GRID_SIZE)
        self.current_block: Optional[Block] = None
        self.next_blocks: List[Block] = []
        self.selected_block_index = -1
        self.dragging = False
        self.drag_offset = Position(0, 0)

        self.score = 0
        self.combo = 0
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self._spawn_next_blocks()
        self._draw_selection()

    def _spawn_next_blocks(self):
        """Generate next blocks to play with"""
        self.next_blocks = []
        for _ in range(3):
            shape = random.choice(list(BlockShape))
            color = random.choice(COLORS)
            block = Block(shape, color, Position(0, 0))
            self.next_blocks.append(block)

    def _draw_selection(self):
        """Select the first available block"""
        if self.next_blocks:
            self.current_block = self.next_blocks.pop(0)
            self.current_block.position = Position(GRID_SIZE // 2, 0)
            self.selected_block_index = 0

            # Add new block to next blocks if needed
            if len(self.next_blocks) < 3:
                shape = random.choice(list(BlockShape))
                color = random.choice(COLORS)
                block = Block(shape, color, Position(0, 0))
                self.next_blocks.append(block)

    def handle_events(self) -> bool:
        """Handle user input"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.rotate_current_block()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self._handle_mouse_click(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._handle_mouse_release(mouse_pos)

        # Handle dragging
        if mouse_pressed and self.dragging and self.current_block:
            grid_x = (mouse_pos[0] - BOARD_OFFSET_X) // CELL_SIZE
            grid_y = (mouse_pos[1] - BOARD_OFFSET_Y) // CELL_SIZE
            self.current_block.position = Position(grid_x - self.drag_offset.x, 
                                                    grid_y - self.drag_offset.y)

        return True

    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]):
        """Handle mouse click for selecting and dragging blocks"""
        grid_x = (mouse_pos[0] - BOARD_OFFSET_X) // CELL_SIZE
        grid_y = (mouse_pos[1] - BOARD_OFFSET_Y) // CELL_SIZE

        if self.current_block and self.current_block.contains_position(Position(grid_x, grid_y)):
            self.dragging = True
            # Calculate offset from block position to click position
            self.drag_offset = Position(grid_x - self.current_block.position.x,
                                       grid_y - self.current_block.position.y)

    def _handle_mouse_release(self, mouse_pos: Tuple[int, int]):
        """Handle mouse release for placing blocks"""
        self.dragging = False

        if self.current_block:
            if self.board.place_block(self.current_block):
                self.score += 10
                cleared_lines = self.board.clear_lines()
                cleared_columns = self.board.clear_columns()

                total_cleared = cleared_lines + cleared_columns
                if total_cleared > 0:
                    self.combo += 1
                    self.score += 100 * total_cleared * self.combo
                else:
                    self.combo = 0

                self._draw_selection()
            else:
                # Reset block position if placement failed
                self.current_block.position = Position(GRID_SIZE // 2, 0)

    def rotate_current_block(self):
        """Rotate the current block"""
        if self.current_block:
            self.current_block.rotate()

    def update(self):
        """Update game state"""
        if not self.current_block:
            self.game_over = True

    def draw(self):
        """Draw everything"""
        self.screen.fill(WHITE)

        # Draw title
        title = self.font_large.render("Block Puzzle", True, BLACK)
        self.screen.blit(title, (20, 10))

        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (650, 20))

        if self.combo > 0:
            combo_text = self.font_small.render(f"Combo: {self.combo}x", True, RED)
            self.screen.blit(combo_text, (650, 60))

        # Draw board
        self._draw_board()

        # Draw current block
        if self.current_block and not self.current_block.is_placed:
            self._draw_block(self.current_block, alpha=200)

        # Draw next blocks preview
        self._draw_next_blocks()

        # Draw instructions
        insructions = [
            "Click and drag to place blocks",
            "Press R to rotate",
            "Press ESC to exit"
        ]
        y_offset = 500
        for instruction in insructions:
            text = self.font_small.render(instruction, True, DARK_GRAY)
            self.screen.blit(text, (50, y_offset))
            y_offset += 30

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_board(self):
        """Draw the game board grid"""
        board_width = GRID_SIZE * CELL_SIZE
        board_height = GRID_SIZE * CELL_SIZE

        # Draw border
        pygame.draw.rect(self.screen, BLACK, 
                        (BOARD_OFFSET_X, BOARD_OFFSET_Y, board_width, board_height), 3)

        # Draw grid
        for y in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY,
                           (BOARD_OFFSET_X, BOARD_OFFSET_Y + y * CELL_SIZE),
                           (BOARD_OFFSET_X + board_width, BOARD_OFFSET_Y + y * CELL_SIZE))
        for x in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY,
                           (BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y),
                           (BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y + board_height))

        # Draw placed blocks
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.board.grid[y][x] is not None:
                    self._draw_cell(x, y, self.board.grid[y][x])

    def _draw_cell(self, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a single cell"""
        rect = pygame.Rect(BOARD_OFFSET_X + x * CELL_SIZE + 2,
                          BOARD_OFFSET_Y + y * CELL_SIZE + 2,
                          CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)

    def _draw_block(self, block: Block, alpha: int = 255):
        """Draw a block"""
        for pos in block.get_global_positions():
            if 0 <= pos.x < GRID_SIZE and 0 <= pos.y < GRID_SIZE:
                self._draw_cell(pos.x, pos.y, block.color)

    def _draw_next_blocks(self):
        """Draw preview of next blocks"""
        preview_x = BOARD_OFFSET_X + GRID_SIZE * CELL_SIZE + 50
        preview_y = BOARD_OFFSET_Y

        next_text = self.font_medium.render("Next:", True, BLACK)
        self.screen.blit(next_text, (preview_x, preview_y))

        y_offset = preview_y + 50
        for i, block in enumerate(self.next_blocks[:3]):
            # Draw block frame
            frame_rect = pygame.Rect(preview_x, y_offset, 120, 80)
            pygame.draw.rect(self.screen, LIGHT_GRAY, frame_rect)
            pygame.draw.rect(self.screen, DARK_GRAY, frame_rect, 2)

            # Draw small preview of the block
            for cell in block.cells:
                x = preview_x + 10 + cell.x * 15
                y = y_offset + 10 + cell.y * 15
                pygame.draw.rect(self.screen, block.color, (x, y, 13, 13))
                pygame.draw.rect(self.screen, DARK_GRAY, (x, y, 13, 13), 1)

            y_offset += 100

    def _draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, RED)
        final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)

        self.screen.blit(game_over_text, 
                        (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 250))
        self.screen.blit(final_score_text,
                        (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, 350))

    def run(self):
        """Main game loop"""
        while self.running:
            self.running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
