import pygame
import random

TILE = 40
COLS, ROWS = 20, 15

WALL, FLOOR, CHEST, KEY, TRAP, GUARD = 0, 1, 2, 3, 4, 5

SPEED = 3
GUARD_SPEED = 2

# =============================================================
# MINI-MAP SETTINGS
# =============================================================

MINIMAP_TILE = 8
MINIMAP_MARGIN = 10


def generate_world():
    grid = [[WALL] * COLS for _ in range(ROWS)]
    rooms = []

    for _ in range(8):
        w = random.randint(3, 6)
        h = random.randint(3, 5)
        x = random.randint(1, COLS - w - 1)
        y = random.randint(1, ROWS - h - 1)

        room = pygame.Rect(x, y, w, h)

        overlap = any(
            room.inflate(2, 2).colliderect(r)
            for r in rooms
        )

        if not overlap:
            rooms.append(room)

            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    grid[ry][rx] = FLOOR

    for i in range(len(rooms) - 1):
        ax, ay = rooms[i].centerx, rooms[i].centery
        bx, by = rooms[i + 1].centerx, rooms[i + 1].centery

        cx = ax

        while cx != bx:
            grid[ay][cx] = FLOOR
            cx += 1 if bx > cx else -1

        cy = ay

        while cy != by:
            grid[cy][bx] = FLOOR
            cy += 1 if by > cy else -1

    if len(rooms) >= 2:
        cr, ck = rooms[-1], rooms[-2]

        grid[cr.centery][cr.centerx] = CHEST
        grid[ck.centery][ck.centerx] = KEY

    start = rooms[0] if rooms else None

    # =========================================================
    # TASK 1: GENERATE TRAPS
    # =========================================================

    trap_candidates = []

    for r in range(ROWS):
        for c in range(COLS):

            if grid[r][c] != FLOOR:
                continue

            if start and start.collidepoint(c, r):
                continue

            trap_candidates.append((r, c))

    trap_count = min(6, len(trap_candidates))

    if trap_count > 0:
        trap_positions = random.sample(
            trap_candidates,
            trap_count
        )

        for r, c in trap_positions:
            grid[r][c] = TRAP

    return grid, start


COLORS = {
    WALL: (60, 50, 70),
    FLOOR: (200, 190, 170),
    CHEST: (200, 160, 30),
    KEY: (220, 220, 60),
    TRAP: (180, 50, 50),
    GUARD: (170, 40, 40),
}


class Player:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.color = (60, 120, 220)
        self.has_key = False

    def move(self, keys, grid, rows, cols):

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        self._try_move(dx, 0, grid, rows, cols)
        self._try_move(0, dy, grid, rows, cols)

    def _try_move(self, dx, dy, grid, rows, cols):

        new = self.rect.move(dx, dy)

        for px, py in [
            (new.left, new.top),
            (new.right - 1, new.top),
            (new.left, new.bottom - 1),
            (new.right - 1, new.bottom - 1)
        ]:

            c = px // TILE
            r = py // TILE

            if (
                not (0 <= r < rows and 0 <= c < cols)
                or grid[r][c] == WALL
            ):
                return

        self.rect = new

    def draw(self, screen):

        pygame.draw.ellipse(
            screen,
            self.color,
            self.rect
        )


# =============================================================
# TASK 2: ENEMY GUARD
# =============================================================

class Guard:

    def __init__(
        self,
        x,
        y,
        left_limit,
        right_limit
    ):

        self.rect = pygame.Rect(
            x,
            y,
            28,
            28
        )

        self.color = (170, 40, 40)

        self.speed = GUARD_SPEED

        self.left_limit = left_limit
        self.right_limit = right_limit

        self.direction = 1

    def update(self):

        self.rect.x += (
            self.speed * self.direction
        )

        if self.rect.left <= self.left_limit:

            self.rect.left = self.left_limit
            self.direction = 1

        if self.rect.right >= self.right_limit:

            self.rect.right = self.right_limit
            self.direction = -1

    def draw(self, screen):

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=6
        )

        pygame.draw.circle(
            screen,
            (230, 180, 150),
            (
                self.rect.centerx,
                self.rect.top + 7
            ),
            6
        )

        pygame.draw.circle(
            screen,
            (20, 20, 20),
            (
                self.rect.centerx - 3,
                self.rect.top + 6
            ),
            1
        )

        pygame.draw.circle(
            screen,
            (20, 20, 20),
            (
                self.rect.centerx + 3,
                self.rect.top + 6
            ),
            1
        )


WIDTH = COLS * TILE
HEIGHT = ROWS * TILE + 80

FPS = 60


class GameEngine:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Treasure Hunt"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            22
        )

        self.small_font = pygame.font.SysFont(
            "monospace",
            16
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            40,
            bold=True
        )

        self.reset()

    def reset(self):

        self.grid, start = generate_world()

        if start:

            sx = start.x * TILE + 6
            sy = start.y * TILE + 6

        else:

            sx = TILE + 6
            sy = TILE + 6

        self.start_position = (
            sx,
            sy
        )

        self.player = Player(
            sx,
            sy
        )

        # =====================================================
        # TASK 2: CREATE GUARD NEAR CHEST
        # =====================================================

        chest_position = None

        for r in range(ROWS):

            for c in range(COLS):

                if self.grid[r][c] == CHEST:

                    chest_position = (c, r)
                    break

            if chest_position is not None:
                break

        self.guard = None

        if chest_position is not None:

            chest_c, chest_r = chest_position

            patrol_tiles = []

            for c in range(COLS):

                if self.grid[chest_r][c] == FLOOR:

                    patrol_tiles.append(c)

            if patrol_tiles:

                patrol_left = max(
                    min(patrol_tiles),
                    chest_c - 3
                )

                patrol_right = min(
                    max(patrol_tiles),
                    chest_c + 3
                )

                valid_patrol = [
                    c
                    for c in patrol_tiles
                    if patrol_left <= c <= patrol_right
                ]

                if len(valid_patrol) >= 2:

                    guard_c = valid_patrol[0]

                    left_limit = (
                        patrol_left * TILE + 6
                    )

                    right_limit = (
                        patrol_right * TILE + 34
                    )

                    guard_x = (
                        guard_c * TILE + 6
                    )

                    guard_y = (
                        chest_r * TILE + 6
                    )

                    self.guard = Guard(
                        guard_x,
                        guard_y,
                        left_limit,
                        right_limit
                    )

        self.won = False

        self.status = (
            "Find the KEY, then the CHEST!"
        )

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):

                self.reset()

        return True

    def update(self):

        if self.won:
            return

        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.grid,
            ROWS,
            COLS
        )

        # =====================================================
        # TASK 2: UPDATE GUARD
        # =====================================================

        if self.guard is not None:

            self.guard.update()

            if self.player.rect.colliderect(
                self.guard.rect
            ):

                self.player.rect.topleft = (
                    self.start_position
                )

                self.status = (
                    "Guard caught you! Back to start!"
                )

                return

        # =====================================================
        # PLAYER TILE
        # =====================================================

        pr = self.player.rect.centery // TILE
        pc = self.player.rect.centerx // TILE

        if 0 <= pr < ROWS and 0 <= pc < COLS:

            cell = self.grid[pr][pc]

            # =================================================
            # TASK 1: TRAP
            # =================================================

            if cell == TRAP:

                self.player.rect.topleft = (
                    self.start_position
                )

                self.status = (
                    "Trap triggered! Back to start!"
                )

                return

            # =================================================
            # KEY PICKUP
            # =================================================

            if cell == KEY:

                self.player.has_key = True

                self.grid[pr][pc] = FLOOR

                self.status = (
                    "Got the key! Find the CHEST!"
                )

            # =================================================
            # CHEST
            # =================================================

            elif (
                cell == CHEST
                and self.player.has_key
            ):

                self.won = True

                self.status = (
                    "Treasure found!"
                )

    # =========================================================
    # TASK 3: MINI-MAP
    # =========================================================

    def draw_minimap(self):

        map_width = COLS * MINIMAP_TILE
        map_height = ROWS * MINIMAP_TILE

        map_x = (
            WIDTH
            - map_width
            - MINIMAP_MARGIN
        )

        map_y = MINIMAP_MARGIN

        background = pygame.Rect(
            map_x - 4,
            map_y - 4,
            map_width + 8,
            map_height + 8
        )

        pygame.draw.rect(
            self.screen,
            (15, 15, 25),
            background
        )

        for r in range(ROWS):

            for c in range(COLS):

                cell = self.grid[r][c]

                mini_rect = pygame.Rect(
                    map_x + c * MINIMAP_TILE,
                    map_y + r * MINIMAP_TILE,
                    MINIMAP_TILE,
                    MINIMAP_TILE
                )

                if cell == WALL:

                    color = (35, 30, 45)

                elif cell == FLOOR:

                    color = (180, 170, 150)

                elif cell == CHEST:

                    color = (200, 150, 20)

                elif cell == KEY:

                    color = (230, 220, 50)

                elif cell == TRAP:

                    color = (180, 50, 50)

                else:

                    color = (35, 30, 45)

                pygame.draw.rect(
                    self.screen,
                    color,
                    mini_rect
                )

        # Player marker
        player_col = (
            self.player.rect.centerx // TILE
        )

        player_row = (
            self.player.rect.centery // TILE
        )

        if (
            0 <= player_col < COLS
            and 0 <= player_row < ROWS
        ):

            player_x = (
                map_x
                + player_col * MINIMAP_TILE
                + MINIMAP_TILE // 2
            )

            player_y = (
                map_y
                + player_row * MINIMAP_TILE
                + MINIMAP_TILE // 2
            )

            pygame.draw.circle(
                self.screen,
                (50, 130, 255),
                (
                    player_x,
                    player_y
                ),
                3
            )

        # Guard marker
        if self.guard is not None:

            guard_col = (
                self.guard.rect.centerx // TILE
            )

            guard_row = (
                self.guard.rect.centery // TILE
            )

            if (
                0 <= guard_col < COLS
                and 0 <= guard_row < ROWS
            ):

                guard_x = (
                    map_x
                    + guard_col * MINIMAP_TILE
                    + MINIMAP_TILE // 2
                )

                guard_y = (
                    map_y
                    + guard_row * MINIMAP_TILE
                    + MINIMAP_TILE // 2
                )

                pygame.draw.circle(
                    self.screen,
                    (255, 60, 60),
                    (
                        guard_x,
                        guard_y
                    ),
                    3
                )

        pygame.draw.rect(
            self.screen,
            (230, 230, 230),
            background,
            1
        )

        label = pygame.font.SysFont(
            "monospace",
            12,
            bold=True
        ).render(
            "MAP",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            label,
            (
                map_x,
                map_y + map_height + 4
            )
        )

    # =========================================================
    # TASK 4: INVENTORY UI
    # =========================================================

    def draw_inventory(self):

        inventory_x = 10
        inventory_y = ROWS * TILE + 8

        slot_size = 44

        # Inventory label
        label = self.small_font.render(
            "INVENTORY",
            True,
            (220, 220, 220)
        )

        self.screen.blit(
            label,
            (
                inventory_x,
                inventory_y
            )
        )

        # Empty inventory slot
        slot_x = inventory_x + 105
        slot_y = inventory_y - 4

        slot = pygame.Rect(
            slot_x,
            slot_y,
            slot_size,
            slot_size
        )

        pygame.draw.rect(
            self.screen,
            (45, 45, 60),
            slot,
            border_radius=5
        )

        pygame.draw.rect(
            self.screen,
            (150, 150, 165),
            slot,
            2,
            border_radius=5
        )

        # =====================================================
        # SHOW KEY AFTER PICKUP
        # =====================================================

        if self.player.has_key:

            center_x = slot.centerx
            center_y = slot.centery

            # Key ring
            pygame.draw.circle(
                self.screen,
                (255, 220, 60),
                (
                    center_x - 7,
                    center_y - 5
                ),
                7,
                3
            )

            # Key shaft
            pygame.draw.rect(
                self.screen,
                (255, 220, 60),
                (
                    center_x - 1,
                    center_y - 3,
                    15,
                    6
                )
            )

            # Key teeth
            pygame.draw.rect(
                self.screen,
                (255, 220, 60),
                (
                    center_x + 8,
                    center_y + 2,
                    4,
                    6
                )
            )

            pygame.draw.rect(
                self.screen,
                (255, 220, 60),
                (
                    center_x + 3,
                    center_y + 2,
                    4,
                    4
                )
            )

    def draw(self):

        self.screen.fill(
            (30, 25, 40)
        )

        # =====================================================
        # DRAW MAIN DUNGEON
        # =====================================================

        for r in range(ROWS):

            for c in range(COLS):

                cell = self.grid[r][c]

                rect = pygame.Rect(
                    c * TILE,
                    r * TILE,
                    TILE,
                    TILE
                )

                pygame.draw.rect(
                    self.screen,
                    COLORS[cell],
                    rect
                )

                # KEY
                if cell == KEY:

                    pygame.draw.circle(
                        self.screen,
                        (255, 240, 60),
                        (
                            c * TILE + TILE // 2,
                            r * TILE + TILE // 2
                        ),
                        10
                    )

                # CHEST
                elif cell == CHEST:

                    pygame.draw.rect(
                        self.screen,
                        (180, 120, 20),
                        rect.inflate(-12, -12),
                        border_radius=4
                    )

                # TRAP
                elif cell == TRAP:

                    trap_rect = rect.inflate(
                        -8,
                        -8
                    )

                    pygame.draw.rect(
                        self.screen,
                        (170, 45, 45),
                        trap_rect,
                        border_radius=5
                    )

                    pygame.draw.line(
                        self.screen,
                        (255, 220, 220),
                        trap_rect.topleft,
                        trap_rect.bottomright,
                        4
                    )

                    pygame.draw.line(
                        self.screen,
                        (255, 220, 220),
                        trap_rect.topright,
                        trap_rect.bottomleft,
                        4
                    )

        # =====================================================
        # GUARD
        # =====================================================

        if self.guard is not None:

            self.guard.draw(
                self.screen
            )

        # =====================================================
        # PLAYER
        # =====================================================

        self.player.draw(
            self.screen
        )

        # =====================================================
        # MINI-MAP
        # =====================================================

        self.draw_minimap()

        # =====================================================
        # HUD
        # =====================================================

        hud = pygame.Rect(
            0,
            ROWS * TILE,
            WIDTH,
            80
        )

        pygame.draw.rect(
            self.screen,
            (20, 20, 35),
            hud
        )

        # Status message
        st = self.font.render(
            self.status,
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            st,
            (
                8,
                ROWS * TILE + 50
            )
        )

        # Restart text
        restart_text = self.small_font.render(
            "R = Restart",
            True,
            (150, 150, 150)
        )

        self.screen.blit(
            restart_text,
            (
                WIDTH - 110,
                ROWS * TILE + 58
            )
        )

        # =====================================================
        # TASK 4: INVENTORY
        # =====================================================

        self.draw_inventory()

        # =====================================================
        # WIN SCREEN
        # =====================================================

        if self.won:

            ov = pygame.Surface(
                (WIDTH, ROWS * TILE),
                pygame.SRCALPHA
            )

            ov.fill(
                (0, 0, 0, 140)
            )

            self.screen.blit(
                ov,
                (0, 0)
            )

            msg = self.big_font.render(
                "TREASURE FOUND!",
                True,
                (220, 180, 30)
            )

            sub = self.font.render(
                "Press R to Play Again",
                True,
                (180, 180, 180)
            )

            self.screen.blit(
                msg,
                (
                    WIDTH // 2
                    - msg.get_width() // 2,
                    ROWS * TILE // 2 - 30
                )
            )

            self.screen.blit(
                sub,
                (
                    WIDTH // 2
                    - sub.get_width() // 2,
                    ROWS * TILE // 2 + 20
                )
            )

        pygame.display.flip()

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":

    engine = GameEngine()
    engine.run()