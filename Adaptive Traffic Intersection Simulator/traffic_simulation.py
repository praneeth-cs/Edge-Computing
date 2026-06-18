
import pygame
import random
import math

WIDTH = 1000
HEIGHT = 1000
FPS = 60

CENTER = (500, 500)
LANE_OFFSET = 20
TURN_ZONE = 70
SAFE_GAP = 25

VEHICLE_SIZE = 12
SPAWN_PROB = 0.02
MAX_LANE_CAPACITY = 15

GREEN = "GREEN"
ORANGE = "ORANGE"
RED = "RED"

ORANGE_TIME = 3 * FPS

COLORS = {
    "N": (0, 120, 255),
    "S": (255, 150, 0),
    "E": (255, 0, 255),
    "W": (0, 255, 255),
}

ROAD = (60, 60, 60)
LANE = (230, 230, 230)
STOP = (255, 255, 255)
BG = (20, 120, 20)
SIGNAL_GREEN = (0, 200, 0)
SIGNAL_ORANGE = (255, 150, 0)
SIGNAL_RED = (200, 0, 0)

lane_centers = {
    "N": (CENTER[0] - LANE_OFFSET, 0),
    "S": (CENTER[0] + LANE_OFFSET, HEIGHT),
    "E": (WIDTH, CENTER[1] - LANE_OFFSET),
    "W": (0, CENTER[1] + LANE_OFFSET),
}

stop_lines = {
    "N": CENTER[1] - 60,
    "S": CENTER[1] + 60,
    "E": CENTER[0] + 60,
    "W": CENTER[0] - 60,
}

lanes = {"N": [], "S": [], "E": [], "W": []}
vehicles = []

turn_probabilities = [
    ("straight", 0.45),
    ("left", 0.25),
    ("right", 0.25),
    ("uturn", 0.05),
]

turn_map = {
    "N": {"straight": "S", "left": "E", "right": "W", "uturn": "N"},
    "S": {"straight": "N", "left": "W", "right": "E", "uturn": "S"},
    "E": {"straight": "W", "left": "N", "right": "S", "uturn": "E"},
    "W": {"straight": "E", "left": "S", "right": "N", "uturn": "W"},
}

velocity_map = {
    "N": (0, 1),
    "S": (0, -1),
    "E": (-1, 0),
    "W": (1, 0),
}


def choose_turn():
    r = random.random()
    total = 0
    for t, p in turn_probabilities:
        total += p
        if r <= total:
            return t
    return "straight"


def bezier(t, p0, p1, p2):
    x = (1-t)**2 * p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1]
    return x, y


class Vehicle:

    def __init__(self, origin):

        self.origin = origin
        self.turn_type = choose_turn()
        self.target = turn_map[origin][self.turn_type]

        self.speed = 2.0
        self.vx, self.vy = velocity_map[origin]

        if origin == "N":
            self.x = CENTER[0] - LANE_OFFSET
            self.y = -20
        elif origin == "S":
            self.x = CENTER[0] + LANE_OFFSET
            self.y = HEIGHT + 20
        elif origin == "E":
            self.x = WIDTH + 20
            self.y = CENTER[1] - LANE_OFFSET
        elif origin == "W":
            self.x = -20
            self.y = CENTER[1] + LANE_OFFSET

        self.color = COLORS[origin]
        self.passed_stop_line = False

        self.turn_progress = 0
        self.turning = False
        self.turn_path = None

    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def setup_turn(self):

        start = (self.x, self.y)

        if self.turn_type == "straight":
            return

        control = CENTER

        if self.target == "N":
            end = (CENTER[0] - LANE_OFFSET, -100)
        elif self.target == "S":
            end = (CENTER[0] + LANE_OFFSET, HEIGHT + 100)
        elif self.target == "E":
            end = (WIDTH + 100, CENTER[1] - LANE_OFFSET)
        else:
            end = (-100, CENTER[1] + LANE_OFFSET)

        self.turn_path = (start, control, end)
        self.turning = True
        self.turn_progress = 0

    def update(self, front_vehicle, signal_state):

        if front_vehicle:
            if self.distance_to(front_vehicle) < SAFE_GAP:
                return

        if not self.passed_stop_line:

            if self.origin == "N":
                if self.y >= stop_lines["N"]:
                    if signal_state != GREEN:
                        return
                    self.passed_stop_line = True

            elif self.origin == "S":
                if self.y <= stop_lines["S"]:
                    if signal_state != GREEN:
                        return
                    self.passed_stop_line = True

            elif self.origin == "E":
                if self.x <= stop_lines["E"]:
                    if signal_state != GREEN:
                        return
                    self.passed_stop_line = True

            elif self.origin == "W":
                if self.x >= stop_lines["W"]:
                    if signal_state != GREEN:
                        return
                    self.passed_stop_line = True

        if not self.turning:
            if abs(self.x - CENTER[0]) < TURN_ZONE and abs(self.y - CENTER[1]) < TURN_ZONE:
                if self.turn_type != "straight":
                    self.setup_turn()

        if self.turning:
            self.turn_progress += 0.01
            if self.turn_progress > 1:
                self.turning = False
            else:
                self.x, self.y = bezier(self.turn_progress, *self.turn_path)
                return

        self.x += self.vx * self.speed
        self.y += self.vy * self.speed

    def draw(self, screen):
        rect = pygame.Rect(
            self.x - VEHICLE_SIZE//2,
            self.y - VEHICLE_SIZE//2,
            VEHICLE_SIZE,
            VEHICLE_SIZE
        )
        pygame.draw.rect(screen, self.color, rect)


class TrafficController:

    def __init__(self):
        self.directions = ["N", "E", "S", "W"]
        self.current = "N"
        self.state = GREEN
        self.orange_timer = 0

    def update(self):

        if self.state == GREEN:

            waiting = {d: len(lanes[d]) for d in lanes}
            best = max(waiting, key=waiting.get)

            if best != self.current:
                self.state = ORANGE
                self.orange_timer = ORANGE_TIME

        elif self.state == ORANGE:

            if self.orange_timer > 0:
                self.orange_timer -= 1
            else:
                self.current = self.next_direction()
                self.state = GREEN

    def next_direction(self):

        waiting = {d: len(lanes[d]) for d in lanes}
        best = max(waiting, key=waiting.get)

        if waiting[best] == 0:
            return "N"

        return best

    def get_signal(self, direction):

        if direction == self.current:

            if self.state == GREEN:
                return GREEN
            if self.state == ORANGE:
                return ORANGE

        return RED


def spawn_vehicle():

    for d in lanes:

        if len(lanes[d]) >= MAX_LANE_CAPACITY:
            continue

        if random.random() < SPAWN_PROB:
            v = Vehicle(d)
            lanes[d].append(v)
            vehicles.append(v)


def draw_roads(screen):

    pygame.draw.rect(screen, ROAD, (450, 0, 100, HEIGHT))
    pygame.draw.rect(screen, ROAD, (0, 450, WIDTH, 100))

    pygame.draw.line(screen, LANE, (480, 0), (480, HEIGHT), 2)
    pygame.draw.line(screen, LANE, (520, 0), (520, HEIGHT), 2)

    pygame.draw.line(screen, LANE, (0, 480), (WIDTH, 480), 2)
    pygame.draw.line(screen, LANE, (0, 520), (WIDTH, 520), 2)

    pygame.draw.line(screen, STOP, (440, stop_lines["N"]), (500, stop_lines["N"]), 3)
    pygame.draw.line(screen, STOP, (500, stop_lines["S"]), (560, stop_lines["S"]), 3)

    pygame.draw.line(screen, STOP, (stop_lines["W"], 500), (stop_lines["W"], 560), 3)
    pygame.draw.line(screen, STOP, (stop_lines["E"], 440), (stop_lines["E"], 500), 3)


def draw_signals(screen, controller):

    signal_positions = {
        "N": (470, 420),
        "S": (530, 580),
        "E": (580, 470),
        "W": (420, 530)
    }

    for d, pos in signal_positions.items():

        state = controller.get_signal(d)

        if state == GREEN:
            color = SIGNAL_GREEN
        elif state == ORANGE:
            color = SIGNAL_ORANGE
        else:
            color = SIGNAL_RED

        pygame.draw.circle(screen, color, pos, 8)


def main():

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    controller = TrafficController()

    running = True

    while running:

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        spawn_vehicle()
        controller.update()

        for d in lanes:

            lane_list = lanes[d]

            for i, v in enumerate(lane_list):

                front = None
                if i > 0:
                    front = lane_list[i-1]

                signal = controller.get_signal(d)

                v.update(front, signal)

        for v in vehicles[:]:

            if v.x < -200 or v.x > WIDTH+200 or v.y < -200 or v.y > HEIGHT+200:
                vehicles.remove(v)
                if v in lanes[v.origin]:
                    lanes[v.origin].remove(v)

        screen.fill(BG)

        draw_roads(screen)
        draw_signals(screen, controller)

        for v in vehicles:
            v.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
