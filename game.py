import pygame
import random

TILE = 40
COLS, ROWS = 20, 15
WALL, FLOOR, CHEST, KEY = 0, 1, 2, 3
TRAP_SPIKE = 4
TRAP_PIT = 5
TRAP_RUNE = 6
TRAP_DART = 7
TRAP = TRAP_SPIKE

ALL_TRAPS = (TRAP_SPIKE, TRAP_PIT, TRAP_RUNE, TRAP_DART)

TRAP_INFO = {
    TRAP_SPIKE: {
        "name": "Spike Trap",
        "message": "Triggered a spike trap! Sent back to start!",
    },
    TRAP_PIT: {
        "name": "Pitfall Trap",
        "message": "Fell into a pitfall trap! Sent back to start!",
    },
    TRAP_RUNE: {
        "name": "Cursed Rune",
        "message": "Stepped on a cursed rune! Sent back to start!",
    },
    TRAP_DART: {
        "name": "Dart Vent",
        "message": "Hit by a poison dart trap! Sent back to start!",
    },
}

SPEED = 3

def is_reachable(grid, start_pos, target_pos):
    """Checks if target_pos is reachable from start_pos using only safe floor tiles."""
    if start_pos == target_pos:
        return True
    queue = [start_pos]
    visited = {start_pos}
    while queue:
        cx, cy = queue.pop(0)
        if (cx, cy) == target_pos:
            return True
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= ny < ROWS and 0 <= nx < COLS and (nx, ny) not in visited:
                if grid[ny][nx] in (FLOOR, KEY, CHEST):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return False

def draw_trap(screen, trap_type, rect):
    """Renders distinct, subtle hazard visuals for each trap type on the stone floor."""
    cx, cy = rect.centerx, rect.centery

    if trap_type == TRAP_SPIKE:
        # Subtle pressure plate with spike release pinholes
        pygame.draw.rect(screen, (175, 165, 145), rect.inflate(-12, -12), width=1, border_radius=2)
        for ox, oy in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
            pygame.draw.circle(screen, (150, 140, 122), (cx + ox, cy + oy), 2)
        pygame.draw.line(screen, (170, 160, 140), (cx - 4, cy - 2), (cx + 3, cy + 3), 1)

    elif trap_type == TRAP_PIT:
        # Subtle false floor with dark recessed pit void
        pygame.draw.rect(screen, (170, 160, 140), rect.inflate(-10, -10), width=1)
        pygame.draw.rect(screen, (115, 105, 95), rect.inflate(-20, -20), border_radius=2)
        pygame.draw.rect(screen, (70, 60, 55), rect.inflate(-26, -26), border_radius=1)
        # Fissure cracks
        pygame.draw.line(screen, (160, 150, 135), (cx - 10, cy - 10), (cx - 5, cy - 5), 1)
        pygame.draw.line(screen, (160, 150, 135), (cx + 10, cy + 10), (cx + 5, cy + 5), 1)

    elif trap_type == TRAP_RUNE:
        # Ancient faded magical glyph inscribed into stone
        pygame.draw.circle(screen, (165, 150, 155), (cx, cy), 9, width=1)
        pygame.draw.polygon(screen, (170, 145, 155), [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)], width=1)
        pygame.draw.circle(screen, (185, 130, 145), (cx, cy), 2)

    elif trap_type == TRAP_DART:
        # Perforated dart/gas vent grate
        pygame.draw.rect(screen, (168, 158, 140), rect.inflate(-14, -14), width=1)
        for dx in (-5, 0, 5):
            for dy in (-5, 0, 5):
                pygame.draw.circle(screen, (135, 125, 110), (cx + dx, cy + dy), 1)

def generate_world():
    rooms = []
    while len(rooms) < 2:
        grid = [[WALL]*COLS for _ in range(ROWS)]
        rooms = []
        for _ in range(8):
            w = random.randint(3,6)
            h = random.randint(3,5)
            x = random.randint(1, COLS-w-1)
            y = random.randint(1, ROWS-h-1)
            room = pygame.Rect(x, y, w, h)
            overlap = any(room.inflate(2,2).colliderect(r) for r in rooms)
            if not overlap:
                rooms.append(room)
                for ry in range(y, y+h):
                    for rx in range(x, x+w):
                        grid[ry][rx] = FLOOR

    for i in range(len(rooms)-1):
        ax, ay = rooms[i].centerx, rooms[i].centery
        bx, by = rooms[i+1].centerx, rooms[i+1].centery
        cx = ax
        while cx != bx:
            grid[ay][cx] = FLOOR
            cx += 1 if bx > cx else -1
        cy = ay
        while cy != by:
            grid[cy][bx] = FLOOR
            cy += 1 if by > cy else -1

    cr, ck = None, None
    if len(rooms) >= 2:
        cr, ck = rooms[-1], rooms[-2]
        grid[cr.centery][cr.centerx] = CHEST
        grid[ck.centery][ck.centerx] = KEY

    start = rooms[0] if rooms else None

    # Place subtle, fair traps that never block the player's only path
    key_pos = (ck.centerx, ck.centery) if ck else None
    chest_pos = (cr.centerx, cr.centery) if cr else None
    start_pos = (start.centerx, start.centery) if start else None

    eligible_tiles = []
    for ry in range(ROWS):
        for rx in range(COLS):
            if grid[ry][rx] == FLOOR:
                # Do not place traps in the starting room or chest room
                if start and (start.x <= rx < start.x + start.w) and (start.y <= ry < start.y + start.h):
                    continue
                if cr and (cr.x <= rx < cr.x + cr.w) and (cr.y <= ry < cr.y + cr.h):
                    continue
                eligible_tiles.append((rx, ry))

    random.shuffle(eligible_tiles)
    target_traps = 2 if len(rooms) >= 3 else 1
    traps_placed = 0

    # Ensure each placed trap is a distinct trap variety
    trap_pool = list(ALL_TRAPS)
    random.shuffle(trap_pool)

    for tx, ty in eligible_tiles:
        if traps_placed >= target_traps:
            break
        trap_type = trap_pool[traps_placed % len(trap_pool)]
        # Speculatively place trap
        grid[ty][tx] = trap_type
        # Ensure fair, trap-free path exists: start -> key -> chest
        path_valid = True
        if start_pos and key_pos and not is_reachable(grid, start_pos, key_pos):
            path_valid = False
        if key_pos and chest_pos and not is_reachable(grid, key_pos, chest_pos):
            path_valid = False

        if path_valid:
            traps_placed += 1
        else:
            # Revert to floor if this candidate blocks the only path
            grid[ty][tx] = FLOOR

    return grid, start, cr

COLORS = {
    WALL: (60,50,70),
    FLOOR: (200,190,170),
    CHEST: (200,160,30),
    KEY: (220,220,60),
    TRAP_SPIKE: (200,190,170),
    TRAP_PIT: (200,190,170),
    TRAP_RUNE: (200,190,170),
    TRAP_DART: (200,190,170),
}

class Guard:
    def __init__(self, p1, p2, speed=2):
        self.p1 = pygame.math.Vector2(p1)
        self.p2 = pygame.math.Vector2(p2)
        self.pos = pygame.math.Vector2(p1)
        self.target = self.p2
        self.speed = speed
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), 26, 26)
        self.color = (210, 50, 50)

    def update(self):
        direction = self.target - self.pos
        dist = direction.length()
        if dist <= self.speed:
            self.pos = pygame.math.Vector2(self.target)
            self.target = self.p1 if self.target == self.p2 else self.p2
        else:
            self.pos += direction.normalize() * self.speed
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
        pygame.draw.ellipse(screen, (130, 25, 25), self.rect, width=2)
        vx = self.rect.centerx - 6
        vy = self.rect.centery - 2
        pygame.draw.rect(screen, (255, 220, 60), (vx, vy, 12, 4), border_radius=1)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.color = (60,120,220)
        self.has_key = False

    def reset_pos(self, pos):
        self.rect.topleft = pos

    def move(self, keys, grid, rows, cols):
        dx=dy=0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx=-SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx=SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy=-SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy=SPEED
        self._try_move(dx,0,grid,rows,cols)
        self._try_move(0,dy,grid,rows,cols)

    def _try_move(self, dx, dy, grid, rows, cols):
        new = self.rect.move(dx,dy)
        for px,py in [(new.left,new.top),(new.right-1,new.top),(new.left,new.bottom-1),(new.right-1,new.bottom-1)]:
            c,r=px//TILE,py//TILE
            if not(0<=r<rows and 0<=c<cols) or grid[r][c]==WALL:
                return
        self.rect=new

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
        if self.has_key:
            pygame.draw.circle(screen, (220,220,60), (self.rect.right-6, self.rect.top+6), 5)


WIDTH = COLS * TILE
HEIGHT = ROWS * TILE + 50
FPS = 60

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Treasure Hunt")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24)
        self.big_font = pygame.font.SysFont("monospace", 40, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 14, bold=True)
        self.reset()

    def reset(self):
        self.grid, start, cr = generate_world()
        if start:
            sx = start.x * TILE + 6
            sy = start.y * TILE + 6
        else:
            sx, sy = TILE+6, TILE+6
        self.start_pos = (sx, sy)
        self.player = Player(sx, sy)
        self.won = False
        self.status = "Find the KEY, then the CHEST!"

        # Initialize patrolling guard between the player's approach doorway and the chest
        self.guard = None
        if cr:
            # Find the entrance doorway to the chest room
            door = None
            for ry in range(cr.top, cr.bottom):
                for rx in range(cr.left, cr.right):
                    for dx, dy in ((-1,0), (1,0), (0,-1), (0,1)):
                        nx, ny = rx + dx, ry + dy
                        if 0 <= ny < ROWS and 0 <= nx < COLS:
                            if not (cr.left <= nx < cr.right and cr.top <= ny < cr.bottom):
                                if self.grid[ny][nx] in (FLOOR, KEY, *ALL_TRAPS):
                                    door = (rx, ry)
                                    break
                    if door: break
                if door: break

            if not door:
                door = (cr.centerx, cr.bottom - 1)

            diff_x = door[0] - cr.centerx
            diff_y = door[1] - cr.centery

            if abs(diff_y) >= abs(diff_x):
                # Approach is north/south: patrol horizontally on the approach side of chest
                if diff_y >= 0:
                    py = cr.centery + 1 if cr.centery + 1 < cr.bottom else cr.centery
                else:
                    py = cr.centery - 1 if cr.centery - 1 >= cr.top else cr.centery
                p1 = (cr.left * TILE + 7, py * TILE + 7)
                p2 = ((cr.right - 1) * TILE + 7, py * TILE + 7)
            else:
                # Approach is east/west: patrol vertically on the approach side of chest
                if diff_x >= 0:
                    px = cr.centerx + 1 if cr.centerx + 1 < cr.right else cr.centerx
                else:
                    px = cr.centerx - 1 if cr.centerx - 1 >= cr.left else cr.centerx
                p1 = (px * TILE + 7, cr.top * TILE + 7)
                p2 = (px * TILE + 7, (cr.bottom - 1) * TILE + 7)

            self.guard = Guard(p1, p2, speed=1.8)

        # Select the corner with the least dungeon overlap (preferring top-right as default)
        corners = {
            'top-right': [(r, c) for r in range(0, 3) for c in range(COLS - 3, COLS)],
            'top-left': [(r, c) for r in range(0, 3) for c in range(0, 3)],
            'bottom-left': [(r, c) for r in range(ROWS - 3, ROWS) for c in range(0, 3)],
            'bottom-right': [(r, c) for r in range(ROWS - 3, ROWS) for c in range(COLS - 3, COLS)],
        }
        order = ['top-right', 'top-left', 'bottom-left', 'bottom-right']
        self.minimap_corner = min(order, key=lambda name: sum(1 for r, c in corners[name] if self.grid[r][c] != WALL))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
        return True

    def update(self):
        if self.won: return
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.grid, ROWS, COLS)

        # Update guard movement and check player collision
        if self.guard:
            self.guard.update()
            if self.player.rect.colliderect(self.guard.rect):
                self.player.reset_pos(self.start_pos)
                self.status = "Caught by the guard! Sent back to start!"

        pr = self.player.rect.centery // TILE
        pc = self.player.rect.centerx // TILE
        if 0<=pr<ROWS and 0<=pc<COLS:
            cell = self.grid[pr][pc]
            if cell == KEY:
                self.player.has_key = True
                self.grid[pr][pc] = FLOOR
                self.status = "Got the key! Find the CHEST!"
            elif cell == CHEST and self.player.has_key:
                self.won = True
                self.status = "Treasure found!"
            elif cell in TRAP_INFO:
                self.player.reset_pos(self.start_pos)
                self.status = TRAP_INFO[cell]["message"]

    def draw(self):
        self.screen.fill((30,25,40))
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                rect = pygame.Rect(c*TILE, r*TILE, TILE, TILE)
                pygame.draw.rect(self.screen, COLORS[cell], rect)
                if cell == KEY:
                    pygame.draw.circle(self.screen, (255,240,60),(c*TILE+TILE//2, r*TILE+TILE//2),10)
                elif cell == CHEST:
                    pygame.draw.rect(self.screen,(180,120,20),rect.inflate(-12,-12),border_radius=4)
                elif cell in TRAP_INFO:
                    draw_trap(self.screen, cell, rect)
        if self.guard:
            self.guard.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_minimap()
        hud = pygame.Rect(0,ROWS*TILE,WIDTH,50)
        pygame.draw.rect(self.screen,(20,20,35),hud)
        st = self.font.render(self.status+"  |  R=Restart", True, (200,200,200))
        self.screen.blit(st,(8,ROWS*TILE+13))
        self.draw_inventory()
        if self.won:
            ov=pygame.Surface((WIDTH,ROWS*TILE),pygame.SRCALPHA)
            ov.fill((0,0,0,140))
            self.screen.blit(ov,(0,0))
            msg=self.big_font.render("TREASURE FOUND!", True,(220,180,30))
            sub=self.font.render("Press R to Play Again",True,(180,180,180))
            self.screen.blit(msg,(WIDTH//2-msg.get_width()//2,ROWS*TILE//2-30))
            self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,ROWS*TILE//2+20))
        pygame.display.flip()

    def draw_inventory(self):
        slot_x = WIDTH - 48
        slot_y = ROWS * TILE + 7
        slot_size = 36
        slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)

        # Inventory label
        lbl = self.small_font.render("KEY", True, (130, 125, 145))
        self.screen.blit(lbl, (slot_x - lbl.get_width() - 8, slot_y + 10))

        # Slot background and border frame
        border_color = (210, 180, 50) if self.player.has_key else (65, 60, 80)
        bg_color = (25, 22, 35) if self.player.has_key else (14, 13, 22)
        pygame.draw.rect(self.screen, bg_color, slot_rect, border_radius=4)
        pygame.draw.rect(self.screen, border_color, slot_rect, width=1, border_radius=4)

        cx, cy = slot_rect.centerx, slot_rect.centery

        if self.player.has_key:
            # Filled state: gleaming golden key icon
            pygame.draw.circle(self.screen, (255, 225, 50), (cx - 5, cy - 5), 6)
            pygame.draw.circle(self.screen, bg_color, (cx - 5, cy - 5), 3)
            pygame.draw.line(self.screen, (255, 215, 40), (cx - 2, cy - 2), (cx + 8, cy + 8), 3)
            pygame.draw.line(self.screen, (255, 215, 40), (cx + 4, cy + 4), (cx + 1, cy + 7), 2)
            pygame.draw.line(self.screen, (255, 215, 40), (cx + 7, cy + 7), (cx + 4, cy + 10), 2)
            pygame.draw.circle(self.screen, (255, 255, 210), (cx - 7, cy - 7), 1)
        else:
            # Empty state: faint silhouette outline
            dim_color = (55, 50, 70)
            pygame.draw.circle(self.screen, dim_color, (cx - 5, cy - 5), 6, width=1)
            pygame.draw.line(self.screen, dim_color, (cx - 2, cy - 2), (cx + 8, cy + 8), 2)
            pygame.draw.line(self.screen, dim_color, (cx + 4, cy + 4), (cx + 1, cy + 7), 2)
            pygame.draw.line(self.screen, dim_color, (cx + 7, cy + 7), (cx + 4, cy + 10), 2)

    def draw_minimap(self):
        scale = 5
        map_w = COLS * scale
        map_h = ROWS * scale

        if self.minimap_corner == 'top-left':
            mm_x = 12
            mm_y = 12
        elif self.minimap_corner == 'bottom-left':
            mm_x = 12
            mm_y = ROWS * TILE - map_h - 12
        elif self.minimap_corner == 'bottom-right':
            mm_x = WIDTH - map_w - 12
            mm_y = ROWS * TILE - map_h - 12
        else: # 'top-right'
            mm_x = WIDTH - map_w - 12
            mm_y = 12

        frame_w = map_w + 6
        frame_h = map_h + 6
        frame_rect = pygame.Rect(mm_x - 3, mm_y - 3, frame_w, frame_h)

        # Render minimap onto a surface to support exact visual look and proximity ghosting
        map_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        map_surf.fill((20, 18, 28, 200))
        pygame.draw.rect(map_surf, (85, 75, 100), (0, 0, frame_w, frame_h), width=1, border_radius=3)

        # Draw dungeon tiles
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                tile_rect = pygame.Rect(3 + c * scale, 3 + r * scale, scale, scale)
                color = (42, 35, 52) if cell == WALL else (165, 155, 140)
                pygame.draw.rect(map_surf, color, tile_rect)
                if cell == KEY:
                    pygame.draw.rect(map_surf, (240, 220, 50), tile_rect)
                elif cell == CHEST:
                    pygame.draw.rect(map_surf, (200, 140, 25), tile_rect)

        # Draw real-time player position marker
        px = 3 + (self.player.rect.centerx * scale) / TILE
        py = 3 + (self.player.rect.centery * scale) / TILE
        pygame.draw.circle(map_surf, (60, 150, 255), (int(px), int(py)), 3)
        pygame.draw.circle(map_surf, (255, 255, 255), (int(px), int(py)), 1)

        # If player ever walks near or under the minimap, ghost it so map underneath is fully visible
        if frame_rect.inflate(16, 16).colliderect(self.player.rect):
            map_surf.set_alpha(70)
        else:
            map_surf.set_alpha(255)

        self.screen.blit(map_surf, frame_rect.topleft)

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
