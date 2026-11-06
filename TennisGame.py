"""
Two-player tennis game (top-down court, Pong-style rules).

Player 1 (left):  W = up,  S = down
Player 2 (right): Up arrow = up,  Down arrow = down
SPACE = start / play again,  P = pause,  ESC = quit

Rules
- The ball rebounds off the rackets and off the top and bottom sidelines.
- Where the ball hits the racket changes its angle: near the edge of the
  racket sends it off steeply, the middle sends it back flat.
- The ball speeds up a little with every hit.
- If the ball goes out past a player's edge, the OTHER player wins the point.
- First to 7 points wins, but you must win by 2 (8-6, 9-7, ...).

Needs pygame:  pip install pygame
"""

import math
import random
import sys

import pygame

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1000, 640
FPS = 60

SCORE_BAR_HEIGHT = 90          # space at the top for the scoreboard
POINTS_TO_WIN = 7
WIN_BY = 2

# Court (the ball bounces off the top and bottom lines of this rectangle)
COURT_LEFT, COURT_RIGHT = 100, WIDTH - 100
COURT_TOP, COURT_BOTTOM = SCORE_BAR_HEIGHT + 30, HEIGHT - 30

RACKET_HEAD_W, RACKET_HEAD_H = 22, 90
RACKET_SPEED = 520             # pixels per second
RACKET_X_OFFSET = 50           # distance of racket from the window edge

BALL_RADIUS = 9
BALL_START_SPEED = 420         # pixels per second
BALL_SPEEDUP = 1.06            # multiplied in on every racket hit
BALL_MAX_SPEED = 1000
MAX_BOUNCE_ANGLE = math.radians(60)

PAUSE_AFTER_POINT = 1.0        # seconds before the next serve

# Colours
SURROUND = (46, 110, 64)       # grass around the court
COURT = (38, 92, 160)          # hard-court blue
LINE = (245, 245, 245)
NET = (230, 230, 230)
NET_SHADOW = (20, 50, 90)
BALL_COLOUR = (215, 240, 60)
BALL_SHADOW = (20, 40, 70)
SCORE_BG = (20, 28, 40)
TEXT = (240, 240, 240)
P1_COLOUR = (230, 80, 70)
P2_COLOUR = (250, 190, 50)
HANDLE = (40, 40, 40)


# ---------------------------------------------------------------------------
# Game objects
# ---------------------------------------------------------------------------
class Racket:
    def __init__(self, x, colour, up_key, down_key, faces_right):
        self.rect = pygame.Rect(0, 0, RACKET_HEAD_W, RACKET_HEAD_H)
        self.rect.center = (x, (COURT_TOP + COURT_BOTTOM) // 2)
        self.y = float(self.rect.centery)
        self.colour = colour
        self.up_key = up_key
        self.down_key = down_key
        self.faces_right = faces_right

    def reset(self):
        self.y = (COURT_TOP + COURT_BOTTOM) / 2
        self.rect.centery = round(self.y)

    def update(self, keys, dt):
        direction = 0
        if keys[self.up_key]:
            direction -= 1
        if keys[self.down_key]:
            direction += 1
        self.y += direction * RACKET_SPEED * dt

        # Keep the racket on the court
        half = RACKET_HEAD_H / 2
        self.y = max(COURT_TOP + half, min(COURT_BOTTOM - half, self.y))
        self.rect.centery = round(self.y)

    @property
    def hitting_face_x(self):
        """x-position of the side of the racket that faces the net."""
        return self.rect.right if self.faces_right else self.rect.left

    def draw(self, surface):
        head = self.rect
        # Handle sticks out behind the player (away from the net)
        handle_len = 34
        if self.faces_right:
            handle = pygame.Rect(head.left - handle_len + 4, head.centery - 4,
                                 handle_len, 8)
        else:
            handle = pygame.Rect(head.right - 4, head.centery - 4,
                                 handle_len, 8)
        pygame.draw.rect(surface, HANDLE, handle, border_radius=3)

        # Oval racket head with strings
        pygame.draw.ellipse(surface, self.colour, head)
        inner = head.inflate(-8, -10)
        pygame.draw.ellipse(surface, (250, 250, 250), inner)
        for sy in range(inner.top + 8, inner.bottom - 4, 8):
            pygame.draw.line(surface, (180, 180, 180),
                             (inner.left + 2, sy), (inner.right - 2, sy))
        pygame.draw.line(surface, (180, 180, 180),
                         (inner.centerx, inner.top + 3),
                         (inner.centerx, inner.bottom - 3))
        pygame.draw.ellipse(surface, self.colour, head, 3)


class Ball:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = (COURT_TOP + COURT_BOTTOM) / 2
        self.vx = 0.0
        self.vy = 0.0

    def serve(self, towards_right):
        """Start from the centre, heading towards one player at a gentle angle."""
        self.x = WIDTH / 2
        self.y = random.uniform(COURT_TOP + 80, COURT_BOTTOM - 80)
        angle = random.uniform(-math.radians(30), math.radians(30))
        direction = 1 if towards_right else -1
        self.vx = direction * BALL_START_SPEED * math.cos(angle)
        self.vy = BALL_START_SPEED * math.sin(angle)

    def stop(self):
        self.vx = self.vy = 0.0

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)

    def update(self, dt, rackets):
        old_x = self.x
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Rebound off the top and bottom sidelines
        if self.y - BALL_RADIUS < COURT_TOP:
            self.y = COURT_TOP + BALL_RADIUS
            self.vy = abs(self.vy)
        elif self.y + BALL_RADIUS > COURT_BOTTOM:
            self.y = COURT_BOTTOM - BALL_RADIUS
            self.vy = -abs(self.vy)

        for racket in rackets:
            self._check_racket(racket, old_x)

    def _check_racket(self, racket, old_x):
        """Bounce off the racket.

        Uses the ball's previous position as well as the new one, so a fast
        ball can't skip straight through the racket between two frames.
        """
        face = racket.hitting_face_x
        if racket.faces_right:          # left player, ball must be moving left
            if self.vx >= 0:
                return
            crossed = (old_x - BALL_RADIUS >= face - 1 and
                       self.x - BALL_RADIUS <= face)
        else:                           # right player, ball must be moving right
            if self.vx <= 0:
                return
            crossed = (old_x + BALL_RADIUS <= face + 1 and
                       self.x + BALL_RADIUS >= face)

        in_reach = (racket.rect.top - BALL_RADIUS <= self.y
                    <= racket.rect.bottom + BALL_RADIUS)
        if not (crossed and in_reach):
            return

        # -1 = hit the very top of the racket, 0 = middle, +1 = very bottom
        offset = (self.y - racket.rect.centery) / (RACKET_HEAD_H / 2)
        offset = max(-1.0, min(1.0, offset))
        angle = offset * MAX_BOUNCE_ANGLE

        new_speed = min(self.speed * BALL_SPEEDUP, BALL_MAX_SPEED)
        direction = 1 if racket.faces_right else -1
        self.vx = direction * new_speed * math.cos(angle)
        self.vy = new_speed * math.sin(angle)

        # Put the ball on the front of the racket so it doesn't stick
        self.x = face + direction * BALL_RADIUS

    def draw(self, surface):
        cx, cy = round(self.x), round(self.y)
        pygame.draw.circle(surface, BALL_SHADOW, (cx + 4, cy + 5), BALL_RADIUS)
        pygame.draw.circle(surface, BALL_COLOUR, (cx, cy), BALL_RADIUS)
        # The curved seam of a tennis ball
        seam = pygame.Rect(0, 0, BALL_RADIUS * 2, BALL_RADIUS * 2)
        seam.center = (cx - BALL_RADIUS + 3, cy)
        pygame.draw.arc(surface, (255, 255, 255), seam,
                        -math.pi / 3, math.pi / 3, 2)
        seam.center = (cx + BALL_RADIUS - 3, cy)
        pygame.draw.arc(surface, (255, 255, 255), seam,
                        2 * math.pi / 3, 4 * math.pi / 3, 2)


# ---------------------------------------------------------------------------
# Drawing the court and scoreboard
# ---------------------------------------------------------------------------
def draw_court(surface):
    surface.fill(SURROUND)

    court = pygame.Rect(COURT_LEFT, COURT_TOP,
                        COURT_RIGHT - COURT_LEFT, COURT_BOTTOM - COURT_TOP)
    pygame.draw.rect(surface, COURT, court)

    # Outer lines (doubles court): sidelines and baselines
    pygame.draw.rect(surface, LINE, court, 4)

    # Singles sidelines (the tramlines)
    alley = round(court.height * 0.125)
    pygame.draw.line(surface, LINE, (court.left, court.top + alley),
                     (court.right, court.top + alley), 3)
    pygame.draw.line(surface, LINE, (court.left, court.bottom - alley),
                     (court.right, court.bottom - alley), 3)

    # Service lines and centre service line
    service_dist = round(court.width * 0.27)
    left_service = court.centerx - service_dist
    right_service = court.centerx + service_dist
    for x in (left_service, right_service):
        pygame.draw.line(surface, LINE, (x, court.top + alley),
                         (x, court.bottom - alley), 3)
    pygame.draw.line(surface, LINE, (left_service, court.centery),
                     (right_service, court.centery), 3)

    # Centre marks on the baselines
    for x, dx in ((court.left, 10), (court.right, -10)):
        pygame.draw.line(surface, LINE, (x, court.centery),
                         (x + dx, court.centery), 3)

    # Net with posts
    net_top, net_bottom = court.top - 12, court.bottom + 12
    pygame.draw.line(surface, NET_SHADOW, (court.centerx + 4, net_top),
                     (court.centerx + 4, net_bottom), 6)
    pygame.draw.line(surface, NET, (court.centerx, net_top),
                     (court.centerx, net_bottom), 4)
    for y in range(net_top, net_bottom, 10):
        pygame.draw.line(surface, (190, 190, 190),
                         (court.centerx - 4, y), (court.centerx + 4, y), 1)
    for y in (net_top, net_bottom):
        pygame.draw.circle(surface, (60, 60, 60), (court.centerx, y), 6)


def draw_scoreboard(surface, fonts, score1, score2, message):
    big, medium, small = fonts
    bar = pygame.Rect(0, 0, WIDTH, SCORE_BAR_HEIGHT)
    pygame.draw.rect(surface, SCORE_BG, bar)

    # Player names
    name1 = medium.render("PLAYER 1", True, P1_COLOUR)
    name2 = medium.render("PLAYER 2", True, P2_COLOUR)
    surface.blit(name1, (40, (SCORE_BAR_HEIGHT - name1.get_height()) // 2))
    surface.blit(name2, (WIDTH - 40 - name2.get_width(),
                         (SCORE_BAR_HEIGHT - name2.get_height()) // 2))

    # Points in the middle
    s1 = big.render(str(score1), True, TEXT)
    s2 = big.render(str(score2), True, TEXT)
    dash = big.render("-", True, TEXT)
    y = 6
    surface.blit(dash, (WIDTH // 2 - dash.get_width() // 2, y))
    surface.blit(s1, (WIDTH // 2 - 40 - s1.get_width(), y))
    surface.blit(s2, (WIDTH // 2 + 40, y))

    # Status line under the score
    status = small.render(message, True, (180, 190, 200))
    surface.blit(status, (WIDTH // 2 - status.get_width() // 2,
                          SCORE_BAR_HEIGHT - status.get_height() - 6))


def draw_centre_message(surface, fonts, title, subtitle):
    big, medium, _ = fonts
    panel = pygame.Surface((560, 150), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 170))
    rect = panel.get_rect(center=(WIDTH // 2, (COURT_TOP + COURT_BOTTOM) // 2))
    surface.blit(panel, rect)
    t = big.render(title, True, TEXT)
    s = medium.render(subtitle, True, (210, 210, 210))
    surface.blit(t, t.get_rect(center=(rect.centerx, rect.centery - 25)))
    surface.blit(s, s.get_rect(center=(rect.centerx, rect.centery + 35)))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def winner(score1, score2):
    """Return 1 or 2 if someone has won, otherwise None."""
    if score1 >= POINTS_TO_WIN and score1 - score2 >= WIN_BY:
        return 1
    if score2 >= POINTS_TO_WIN and score2 - score1 >= WIN_BY:
        return 2
    return None


def score_message(score1, score2):
    """Text shown under the score: deuce, advantage, match point, etc."""
    if score1 >= POINTS_TO_WIN - 1 and score1 == score2:
        return "DEUCE - win by 2"
    if min(score1, score2) >= POINTS_TO_WIN - 1:
        leader = 1 if score1 > score2 else 2
        return f"ADVANTAGE PLAYER {leader}"
    if score1 >= POINTS_TO_WIN - 1 and score1 > score2:
        return "MATCH POINT PLAYER 1"
    if score2 >= POINTS_TO_WIN - 1 and score2 > score1:
        return "MATCH POINT PLAYER 2"
    return f"First to {POINTS_TO_WIN} - win by {WIN_BY}"


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tennis")
    clock = pygame.time.Clock()
    fonts = (pygame.font.SysFont("arial", 64, bold=True),
             pygame.font.SysFont("arial", 30, bold=True),
             pygame.font.SysFont("arial", 18, bold=True))

    player1 = Racket(RACKET_X_OFFSET, P1_COLOUR, pygame.K_w, pygame.K_s,
                     faces_right=True)
    player2 = Racket(WIDTH - RACKET_X_OFFSET, P2_COLOUR, pygame.K_UP,
                     pygame.K_DOWN, faces_right=False)
    rackets = (player1, player2)
    ball = Ball()

    score1 = score2 = 0
    state = "start"            # start -> playing -> point -> ... -> game_over
    paused = False
    serve_timer = 0.0
    serve_to_right = random.choice((True, False))
    match_winner = None

    def new_match():
        nonlocal score1, score2, state, serve_timer, match_winner
        score1 = score2 = 0
        match_winner = None
        for r in rackets:
            r.reset()
        ball.stop()
        ball.x, ball.y = WIDTH / 2, (COURT_TOP + COURT_BOTTOM) / 2
        state = "point"
        serve_timer = PAUSE_AFTER_POINT

    while True:
        dt = clock.tick(FPS) / 1000.0

        # --- Events -------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and state in ("start", "game_over"):
                    new_match()
                if event.key == pygame.K_p and state in ("playing", "point"):
                    paused = not paused

        # --- Update -------------------------------------------------------
        if not paused and state in ("playing", "point"):
            keys = pygame.key.get_pressed()
            for r in rackets:
                r.update(keys, dt)

            if state == "point":
                # Short pause, then serve
                serve_timer -= dt
                if serve_timer <= 0:
                    ball.serve(serve_to_right)
                    state = "playing"

            elif state == "playing":
                ball.update(dt, rackets)

                # Ball out on the left edge -> point to Player 2
                if ball.x + BALL_RADIUS < 0:
                    score2 += 1
                    serve_to_right = False   # serve towards whoever lost the point
                    state = "point"
                # Ball out on the right edge -> point to Player 1
                elif ball.x - BALL_RADIUS > WIDTH:
                    score1 += 1
                    serve_to_right = True
                    state = "point"

                if state == "point":
                    ball.stop()
                    serve_timer = PAUSE_AFTER_POINT
                    match_winner = winner(score1, score2)
                    if match_winner:
                        state = "game_over"

        # --- Draw ---------------------------------------------------------
        draw_court(screen)
        for r in rackets:
            r.draw(screen)
        if state == "playing":
            ball.draw(screen)

        if match_winner:
            message = f"PLAYER {match_winner} WINS {max(score1, score2)}-{min(score1, score2)}"
        else:
            message = score_message(score1, score2)
        draw_scoreboard(screen, fonts, score1, score2, message)

        if state == "start":
            draw_centre_message(screen, fonts, "TENNIS",
                                "W/S  vs  Up/Down  -  SPACE to start")
        elif state == "game_over":
            draw_centre_message(screen, fonts, f"PLAYER {match_winner} WINS!",
                                "SPACE to play again  -  ESC to quit")
        elif paused:
            draw_centre_message(screen, fonts, "PAUSED", "Press P to continue")

        pygame.display.flip()


if __name__ == "__main__":
    main()
