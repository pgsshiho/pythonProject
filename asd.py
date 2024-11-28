import os
import pygame
import sys
import math
import json
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ibooni")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
font_path = "C:/Users/user/Desktop/NanumGothic.otf"
TILE_SIZE = 40
MOVE_SPEED = 2
game_started = False
save_file = "save_data.json"
chase_mode = False
aooni_chase_time = 0
aooni_timer_start = False
aooni_disappear = False
game_over = False
last_map_change_time = 0
teleport_tiles = {}
assets = {}
def load_game():
    global player_pos, current_map
    if not os.path.exists(save_file):
        print("No save file found!")
        return
    title_buttons = [
        Button(WIDTH // 2 - 140, HEIGHT // 2 - 100, 300, 50, "Start New Game", start_game),
        Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Load Game", load_and_start_game) if os.path.exists(
            save_file) else None,
        Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Exit", quit_game)
    ]
    load_map_data(MAP_FILE_PATH)
    with open(save_file, "r", encoding="utf-8") as file:
        save_data = json.load(file)
    player_pos = save_data.get("player_pos", [365, 480])  # 기본값: 시작 위치
    map_name = save_data.get("current_map", "Robby")  # 기본값: Robby
    current_map = next((room for room in map_data["rooms"] if room["name"] == map_name), None)
    if not current_map:
        print(f"Error: Map '{map_name}' not found in map data!")
    else:
        print(f"Game loaded: Current map is {current_map['name']}.")
def load_and_start_game():
    load_game()  # 저장된 데이터 불러오기
    game_loop()  # 게임 루프 실행
# 리소스 로드 함수
def load_assets():
    global assets
    assets["font"] = pygame.font.Font(font_path, 40)
    def load_image(path, size=None):
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size) if size else image
    assets["floor"] = load_image("C:/Users/user/Desktop/Pproject/floor.png", (TILE_SIZE, TILE_SIZE))
    assets["teleport_tiles"] = load_image("C:/Users/user/Desktop/Pproject/floor.png", (TILE_SIZE, TILE_SIZE))
    assets["wall"] = load_image("C:/Users/user/Desktop/Pproject/wall.png", (TILE_SIZE, TILE_SIZE))
    assets["door"] = load_image("C:/Users/user/Desktop/Pproject/door.png", (TILE_SIZE, TILE_SIZE))
    assets["stairs"] = load_image("C:/Users/user/Desktop/Pproject/stairs.png", (TILE_SIZE, TILE_SIZE))
    assets["title_background"] = load_image("C:/Users/user/Desktop/Pproject/Aooni,Ib.webp", (WIDTH, HEIGHT))
    assets["game_over"] = load_image("C:/Users/user/Desktop/Pproject/Gameover.jpeg", (WIDTH, HEIGHT))
    assets["music"] = {
        "title": "C:/Users/user/Desktop/Pproject/maintitle.wav",
        "chase": "C:/Users/user/Desktop/Pproject/horor-b.wav",
        "main": "C:/Users/user/Desktop/Pproject/Mainmusic.wav",
        "game_over": "C:/Users/user/Desktop/Pproject/garry_s-theme.wav",
    }
def load_map_data(file_path):
    global map_data, current_map
    with open(file_path, "r", encoding="utf-8") as file:
        map_data = json.load(file)
    for room in map_data["rooms"]:
        # 맵이 비어 있는 경우 기본 빈 맵을 생성
        if not room.get("map"):
            room["map"] = [[6] * 10 for _ in range(10)]
    # 초기 맵 설정
    current_map = next((room for room in map_data["rooms"] if room["name"] == "Robby"), None)
    if not current_map:
        raise ValueError("Initial map (Robby) not found in map data!")
    print("Loaded map data for:", current_map["name"])
def play_music(file, loop=True):
    # 현재 음악이 재생 중이면 멈춤
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    # 새로운 음악 로드 및 재생
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(-1 if loop else 0)
def title_screen():
    play_music(assets["music"]["title"])  # 메인 타이틀 음악 재생
    running = True
    title_buttons = [
        Button(WIDTH // 2 - 140, HEIGHT // 2 - 100, 300, 50, "Start New Game", start_game),
        Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Load Game", load_and_start_game) if os.path.exists(save_file) else None,
        Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Exit", quit_game)
    ]
    title_buttons = [btn for btn in title_buttons if btn]  # None 값 제거
    while running:
        screen.fill(BLACK)  # 배경을 검은색으로 설정
        screen.blit(assets["title_background"], (0, 0))
        for button in title_buttons:
            button.draw(screen, assets["font"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in title_buttons:
                    if button.rect.collidepoint(event.pos):
                        button.callback()
        pygame.display.flip()
def typewriter_effect(text, x, y, font, color, delay=50, start_delay=500):
    rendered_text = ""
    clock = pygame.time.Clock()

    # 초기 대기 시간
    pygame.time.wait(start_delay)

    for char in text:
        rendered_text += char
        screen.fill(BLACK)  # 메시지 출력 중 배경은 검은색 유지
        text_surface = font.render(rendered_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(delay)
        clock.tick(60)

# 세이브 데이터 로드 및 게임 시작
def load_and_start_game():
    global paused
    load_game()  # 세이브 데이터 로드
    paused = False  # 일시 정지 상태 해제
    play_music(assets["music"]["chase"])  # 추적 음악 재생
    game_loop()  # 게임 루프 실행

# 게임 종료
def quit_game():
    pygame.quit()
    sys.exit()

# 음악 정지
def stop_music():
    pygame.mixer.music.stop()

# 초기 위치 설정
def initialize_positions():
    global player_pos, aooni_pos
    player_pos = [365, 480]  # 플레이어의 초기 위치
    aooni_pos = [-100, -100]  # 초기에는 화면 밖에 배치

# 텔레포트 타일의 기능을 처리
def handle_tile_interaction(player_x, player_y, current_map):
    """
    플레이어의 위치를 기반으로 전환 타일을 확인하고 맵 전환.
    """
    for transition in current_map["rooms"]:  # 전체 맵 데이터에서 transitions 검색
        if transition.get("name") == current_map["name"]:  # 현재 맵에 대한 transitions 탐색
            for t in transition.get("transitions", []):
                if t["x"] == player_x and t["y"] == player_y:
                    return t["to"]
    return None

# 플레이어 이동 처리
def handle_player_movement(keys):
    global player_pos, current_map

    dx, dy = 0, 0
    if keys[pygame.K_UP]: dy -= MOVE_SPEED
    if keys[pygame.K_DOWN]: dy += MOVE_SPEED
    if keys[pygame.K_LEFT]: dx -= MOVE_SPEED
    if keys[pygame.K_RIGHT]: dx += MOVE_SPEED

    # 이동 후 좌표 계산
    new_x, new_y = player_pos[0] + dx, player_pos[1] + dy

    # 이동 가능 여부 확인
    if can_move(new_x, new_y, current_map):
        player_pos[0], player_pos[1] = new_x, new_y

    # 플레이어 타일 좌표 확인
    tile_x = player_pos[0] // TILE_SIZE
    tile_y = player_pos[1] // TILE_SIZE

    # 텔레포트 타일 확인
    for transition in current_map.get("transitions", []):
        if transition["x"] == tile_x and transition["y"] == tile_y:
            change_map(transition["to"])
            break


# 맵 이동 처리
def draw_buttons():
    """
    현재 맵의 모든 버튼을 화면에 그립니다.
    """
    for button in buttons:
        button.draw(screen)


DIALOG_BOX_HEIGHT = 150  # 대화창의 높이
FONT_PATH = "C:/Users/user/Desktop/NanumGothic.otf" # 한글 폰트 파일 경로 (예: Windows에서는 'malgun.ttf')
FONT_SIZE = 24  # 폰트 크기

# 한글 폰트 로드
FONT = pygame.font.Font(FONT_PATH, FONT_SIZE)
DIALOG_BOX_COLOR = (0, 0, 0)  # 대화창 배경 색상 (검은색)
TEXT_COLOR = (255, 255, 255)  # 텍스트 색상 (흰색)

# 대화창 상태
dialog_text = []
dialog_index = 0
show_dialog = False


def draw_dialog_box():
    """ 대화창을 화면에 그리기 """
    if show_dialog:
        # 텍스트 렌더링
        text = FONT.render(dialog_text[dialog_index], True, TEXT_COLOR)

        # 대화창의 너비와 텍스트의 너비를 계산하여 중앙 배치
        text_width = text.get_width()
        text_height = text.get_height()

        # 대화창의 중앙 위치 계산
        box_width = text_width + 40  # 여백 추가
        box_height = text_height + 40
        box_x = (WIDTH - box_width) // 2
        box_y = HEIGHT - DIALOG_BOX_HEIGHT - box_height // 2

        # 대화창 그리기
        pygame.draw.rect(screen, DIALOG_BOX_COLOR, (box_x, box_y, box_width, box_height))
        screen.blit(text, (box_x + 20, box_y + 20))  # 텍스트 위치 조정
def start_dialog(messages):
    """ 대화 시작 """
    global dialog_text, dialog_index, show_dialog
    dialog_text = messages
    dialog_index = 0
    show_dialog = True


def handle_dialog_event():
    """마우스 클릭으로 대화 진행"""
    global dialog_index, show_dialog
    mouse_pressed = pygame.mouse.get_pressed()

    # 마우스 왼쪽 버튼 클릭 시 대화 진행
    if mouse_pressed[0]:  # 0은 왼쪽 버튼
        if dialog_index < len(dialog_text) - 1:
            dialog_index += 1  # 다음 텍스트로 넘어감
        else:
            show_dialog = False  # 대화가 끝나면 대화창을 닫음


def handle_button_events(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        for button in buttons:
            if button.rect.collidepoint(event.pos):
                button.callback()  # 버튼의 콜백 함수 호출
class ArrowButton:
    def __init__(self, x, y, direction, callback):
        """
        화살표 버튼 생성
        - x, y: 버튼 중심 좌표
        - direction: 화살표 방향 ('left', 'right', 'up', 'down')
        - callback: 클릭 시 호출할 함수
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.callback = callback
        self.size = 40  # 버튼 크기
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def draw(self, screen, font=None):
        """
        화살표 버튼과 텍스트를 그립니다.
        - font: 텍스트를 표시할 폰트 (선택 사항)
        """
        # 화살표 그리기
        color = (255, 255, 0)  # 노란색
        points = []
        if self.direction == "left":
            points = [(self.x + self.size // 2, self.y - self.size // 2),  # 위쪽
                      (self.x - self.size // 2, self.y),  # 왼쪽
                      (self.x + self.size // 2, self.y + self.size // 2)]  # 아래쪽
        elif self.direction == "right":
            points = [(self.x - self.size // 2, self.y - self.size // 2),  # 위쪽
                      (self.x + self.size // 2, self.y),  # 오른쪽
                      (self.x - self.size // 2, self.y + self.size // 2)]  # 아래쪽
        elif self.direction == "up":
            points = [(self.x, self.y - self.size // 2),  # 위쪽
                      (self.x - self.size // 2, self.y + self.size // 2),  # 왼쪽
                      (self.x + self.size // 2, self.y + self.size // 2)]  # 오른쪽
        elif self.direction == "down":
            points = [(self.x, self.y + self.size // 2),  # 아래쪽
                      (self.x - self.size // 2, self.y - self.size // 2),  # 왼쪽
                      (self.x + self.size // 2, self.y - self.size // 2)]  # 오른쪽

        pygame.draw.polygon(screen, color, points)

        # 텍스트 그리기
        if font and self.text:
            text_surface = font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """
        클릭 이벤트를 처리합니다.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()


# 맵 변경 처리 수정 (버튼 생성 포함)
def change_map(target_map_name):
    global current_map
    target_map = next((room for room in map_data["rooms"] if room["name"] == target_map_name), None)
    if not target_map:
        print(f"Target map '{target_map_name}' not found in map data!")
        return

    current_map = target_map
    print(f"Changed map to: {current_map['name']}")

    # 맵 변경 후 버튼 재생성
    create_buttons()
door_locked_message = "문이 잠겨 있습니다."

def game_loop():
    global game_over, current_map, dialog_index, show_dialog

    clock = pygame.time.Clock()
    play_music(assets["music"]["main"])

    # 게임 시작 후 첫 번째 대화
    start_dialog([
        "게임이 시작되었습니다.",
        "여긴 아오오니의 저택..?"
    ])

    while not game_over:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()

        handle_player_movement(keys)

        # 화면 중앙에 맵 렌더링
        screen.fill(BLACK)  # 배경 검은색으로 채우기
        if "map" in current_map and current_map["map"]:
            map_width = len(current_map["map"][0]) * TILE_SIZE
            map_height = len(current_map["map"]) * TILE_SIZE
            offset_x = (WIDTH - map_width) // 2
            offset_y = (HEIGHT - map_height) // 2

            for row_idx, row in enumerate(current_map["map"]):
                for col_idx, tile in enumerate(row):
                    x = offset_x + col_idx * TILE_SIZE
                    y = offset_y + row_idx * TILE_SIZE
                    if tile == 0:
                        screen.blit(assets["floor"], (x, y))
                    elif tile == 1:
                        screen.blit(assets["wall"], (x, y))
                    elif tile == 2:  # 문 타일
                        screen.blit(assets["door"], (x, y))
                        if pygame.mouse.get_pressed()[0]:  # 왼쪽 클릭
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            if x <= mouse_x <= x + TILE_SIZE and y <= mouse_y <= y + TILE_SIZE:
                                start_dialog([door_locked_message])  # 문이 잠겨있다는 메시지 표시
                    elif tile == 3:
                        screen.blit(assets["stairs"], (x, y))
                    elif tile == 4:
                        screen.blit(assets["teleport_tiles"], (x, y))
                    elif tile == 6:
                        pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))

        # 대화창 그리기
        draw_dialog_box()

        # 버튼 그리기
        draw_buttons()

        # 마우스 클릭 이벤트 처리 (대화 진행)
        handle_dialog_event()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC 키 눌렀을 때 메뉴 호출
                    menu_screen()
            handle_button_events(event)

        pygame.display.flip()

    if game_over:  # 게임 루프 종료 후 게임 오버 화면
        game_over_screen()

def menu_screen():
    """
    ESC 키를 눌렀을 때 표시되는 메뉴 화면.
    """
    running = True
    menu_buttons = [
        Button(WIDTH // 2 - 100, HEIGHT // 2 - 150, 200, 50, "Resume", lambda: None),  # Resume 버튼
        Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Save", save_game),  # Save 버튼
        Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Exit", lambda: return_to_title())  # Exit 버튼
    ]

    while running:
        screen.fill(BLACK)  # 메뉴 배경은 검은색
        for button in menu_buttons:
            button.draw(screen, assets["font"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in menu_buttons:
                    if button.rect.collidepoint(event.pos):
                        if button.text == "Resume":
                            running = False  # Resume 버튼 클릭 시 메뉴 종료
                        else:
                            button.callback()

        pygame.display.flip()
class DialogBox:
    def __init__(self, x, y, width, height, font, color, background_color=(0, 0, 0, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.color = color
        self.background_color = background_color
        self.text = ""
        self.is_visible = False

    def draw(self, screen):
        if self.is_visible:
            # Draw the background of the dialog box with transparency
            pygame.draw.rect(screen, self.background_color, self.rect)

            # Render and display the text
            text_surface = self.font.render(self.text, True, self.color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def set_text(self, text):
        self.text = text
        self.is_visible = True

    def hide(self):
        self.is_visible = False

def return_to_title():
    title_screen()
def save_game():
    save_data = {
        "player_pos": player_pos,
        "current_map": current_map["name"]
    }
    with open(save_file, "w", encoding="utf-8") as file:
        json.dump(save_data, file, indent=4)
    print("Game saved successfully.")
def check_game_over_condition():
    if player_pos == [0, 0]:  # 예시 조건
        return True
    return False
def handle_game_over():
    global game_over
    game_over = True  # 게임 루프 종료
    print("Game Over triggered.")  # 디버깅용 메시지
    game_over_screen()
def can_move(x, y, current_map):
    if "map" not in current_map or not current_map["map"]:
        print(f"Error: Map data is missing or empty for room {current_map['name']}")
        return False
    tiles = current_map["map"]
    tile_x = x // TILE_SIZE
    tile_y = y // TILE_SIZE
    if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
        return tiles[tile_y][tile_x] != 1  # 벽(1) 여부 확인
    return False
# JSON 파일 경로
MAP_FILE_PATH = "C:/Users/user/Desktop/Pproject/map_data.json"
def game_over_screen():
    while True:
        screen.fill((0, 0, 0))  # 검은색 화면
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        prompt_text = font.render("Press SPACEBAR", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    title_screen()  # 메인 타이틀로 돌아가기
                    return
def start_game():
    play_music(assets["music"]["main"])
    global paused, current_map
    paused = False
    load_map_data(MAP_FILE_PATH)
    current_map = next((room for room in map_data["rooms"] if room["name"] == "Robby"), None)
    play_music(assets["music"]["main"])
    font = assets["font"]
    screen.fill(BLACK)  # 배경 검은색으로 설정
    pygame.display.flip()
    typewriter_effect("오늘도 평범하게 게임을 즐기고 있던 나", WIDTH // 2 - 300, HEIGHT // 2 - 50, font, WHITE, delay=100)
    typewriter_effect("갑자기 게임 속으로 빨려들어가는 데....", WIDTH // 2 - 300, HEIGHT // 2, font, WHITE, delay=100)
    reset_game_state(reset_positions=True)
    create_buttons()  # 초기 버튼 생성
    game_loop()
def reset_game_state(reset_positions=True):
    global player_pos, aooni_pos, chase_mode, aooni_disappear, game_over
    chase_mode = False
    aooni_disappear = False
    game_over = False
    if reset_positions:
        initialize_positions()
class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback  # 버튼 클릭 시 호출할 함수
        self.color = GRAY
        self.text_color = BLACK
    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()  # 버튼 클릭 시 콜백 호출
buttons = []


def create_buttons():
    """
    현재 맵에 따라 적절한 화살표 버튼을 생성합니다.
    """
    global buttons
    buttons.clear()  # 기존 버튼 초기화

    if not current_map or "name" not in current_map:
        print(f"Error: current_map is invalid or missing 'name' attribute.")
        return

    if current_map["name"] == "Robby":
        # 로비에서는 왼쪽과 오른쪽 화살표
        buttons.append(ArrowButton(50, HEIGHT // 2, "left", lambda: change_map("bathroom")))
        buttons.append(ArrowButton(WIDTH - 50, HEIGHT // 2, "right", lambda: change_map("Robby to kitchen")))
    elif current_map["name"] == "Robby to kitchen":
        # 로비에서 부엌으로 가는 연결 맵
        buttons.append(ArrowButton(50, HEIGHT // 2, "left", lambda: change_map("Robby")))
        buttons.append(ArrowButton(WIDTH - 50, HEIGHT // 2, "right", lambda: change_map("kitchen")))
    elif current_map["name"] == "kitchen":
        # 부엌에서는 왼쪽 화살표만
        buttons.append(ArrowButton(50, HEIGHT // 2, "left", lambda: change_map("Robby to kitchen")))
    elif current_map["name"] == "bathroom":
        # 욕실에서는 오른쪽 화살표만
        buttons.append(ArrowButton(WIDTH - 50, HEIGHT // 2, "right", lambda: change_map("Robby")))
    else:
        print(f"Warning: No button configuration for map '{current_map['name']}'.")

    print(f"Arrow buttons created for map '{current_map['name']}': {len(buttons)}")


map_data = {}  # 맵 데이터
current_map = None  # 현재 맵 데이터
if __name__ == "__main__":
    load_assets()  # 리소스 로드
    load_map_data(MAP_FILE_PATH)  # 맵 데이터 로드
    initialize_positions()  # 초기 위치 설정
    title_screen()  # 타이틀 화면 실행

