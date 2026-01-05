"""
자율주행 AI 시각화 프로젝트 설정
iOS 스타일 디자인
"""

# === 화면 설정 ===
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

# === 트랙 설정 ===
TRACK_CENTER_X = 480
TRACK_CENTER_Y = 450
TRACK_WIDTH = 120  # 도로 폭
TRACK_OUTER_A = 400  # 타원 장축 (가로)
TRACK_OUTER_B = 320  # 타원 단축 (세로)

# === 차량 설정 ===
CAR_COUNT = 20
CAR_WIDTH = 30
CAR_HEIGHT = 16
CAR_MAX_SPEED = 8
CAR_MIN_SPEED = 0  # 멈출 수 있도록 0으로 변경
CAR_ACCELERATION = 0.3
CAR_FRICTION = 0.05
CAR_TURN_SPEED = 3  # 회전 속도 (도/프레임) - 더 부드럽게

# === 센서 설정 ===
SENSOR_COUNT = 5
SENSOR_MAX_LENGTH = 200
SENSOR_ANGLES = [-90, -45, 0, 45, 90]  # 도 단위

# === 진화 설정 ===
GENERATION_TIME = 30  # 초
CHECKPOINT_REWARD = 100
DISTANCE_REWARD = 1

# === 배속 옵션 ===
SPEED_OPTIONS = [1, 5, 10]

# === UI 패널 설정 ===
PANEL_X = 1020
PANEL_WIDTH = 560
PANEL_PADDING = 20
CARD_RADIUS = 16  # 카드 모서리 반경
CARD_PADDING = 16  # 카드 내부 패딩
CARD_SPACING = 12  # 카드 간격

# === iOS 색상 팔레트 ===
COLORS = {
    # iOS 다크 배경
    'bg_primary': (0, 0, 0),
    'bg_secondary': (28, 28, 30),
    'bg_tertiary': (44, 44, 46),
    'bg_elevated': (58, 58, 60),
    
    # iOS 시스템 컬러
    'accent_blue': (10, 132, 255),
    'accent_green': (48, 209, 88),
    'accent_orange': (255, 159, 10),
    'accent_red': (255, 69, 58),
    'accent_yellow': (255, 214, 10),
    'accent_purple': (191, 90, 242),
    'accent_teal': (100, 210, 255),
    
    # 텍스트
    'text_primary': (255, 255, 255),
    'text_secondary': (142, 142, 147),
    'text_tertiary': (99, 99, 102),
    
    # 구분선/테두리
    'separator': (56, 56, 58),
    'card_border': (56, 56, 58),
    
    # 트랙
    'track_grass': (15, 20, 15),
    'track_road': (45, 45, 50),
    'track_border': (100, 100, 105),
    'track_center_line': (80, 80, 85),
    'checkpoint': (255, 69, 58),
    
    # 차량
    'car_alive': (10, 132, 255),      # iOS 블루
    'car_best': (255, 214, 10),       # iOS 옐로우
    'car_dead': (72, 72, 74),
    'sensor_line': (255, 69, 58),
    
    # 신경망 시각화
    'neuron_input': (10, 132, 255),
    'neuron_hidden': (142, 142, 147),
    'neuron_output': (255, 159, 10),
    'connection_positive': (48, 209, 88),
    'connection_negative': (255, 69, 58),
    
    # 그래프
    'graph_line_best': (255, 214, 10),
    'graph_line_avg': (10, 132, 255),
    'graph_grid': (44, 44, 46),
    
    # 버튼
    'button_inactive': (44, 44, 46),
    'button_active': (10, 132, 255),
    
    # 프로그레스 바
    'progress_bg': (44, 44, 46),
    'progress_fill': (10, 132, 255),
    'progress_fill_green': (48, 209, 88),
}

# === 폰트 크기 ===
FONT_TITLE = 32
FONT_LARGE = 24
FONT_MEDIUM = 17
FONT_SMALL = 14
FONT_CAPTION = 12

# === 파일 경로 ===
NEAT_CONFIG_PATH = 'neat_config.txt'
