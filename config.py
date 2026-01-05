"""
자율주행 AI 시각화 프로젝트 설정
"""

# === 화면 설정 ===
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# === 트랙 설정 ===
TRACK_CENTER_X = 450
TRACK_CENTER_Y = 400
TRACK_WIDTH = 120  # 도로 폭
TRACK_OUTER_A = 380  # 타원 장축 (가로)
TRACK_OUTER_B = 300  # 타원 단축 (세로)

# === 차량 설정 ===
CAR_COUNT = 20
CAR_WIDTH = 30
CAR_HEIGHT = 16
CAR_MAX_SPEED = 8
CAR_MIN_SPEED = 2
CAR_ACCELERATION = 0.3
CAR_FRICTION = 0.05
CAR_TURN_SPEED = 5  # 회전 속도 (도/프레임)

# === 센서 설정 ===
SENSOR_COUNT = 5
SENSOR_MAX_LENGTH = 200
SENSOR_ANGLES = [-90, -45, 0, 45, 90]  # 도 단위

# === 진화 설정 ===
GENERATION_TIME = 30  # 초
CHECKPOINT_REWARD = 100
DISTANCE_REWARD = 1

# === UI 패널 설정 ===
PANEL_X = 920
PANEL_WIDTH = 460
PANEL_PADDING = 20

# === 색상 (RGB) ===
COLORS = {
    # 배경
    'background': (40, 45, 50),
    
    # 트랙
    'track_grass': (34, 139, 34),
    'track_road': (60, 60, 65),
    'track_border': (255, 255, 255),
    'track_center_line': (255, 255, 100),
    'checkpoint': (255, 100, 100),
    
    # 차량
    'car_alive': (0, 200, 255),
    'car_best': (255, 215, 0),  # 1위 차량
    'car_dead': (100, 100, 100),
    'sensor_line': (255, 100, 100),
    
    # UI 패널
    'panel_bg': (45, 50, 55),
    'panel_border': (80, 85, 90),
    'text': (255, 255, 255),
    'text_dim': (160, 165, 170),
    'text_highlight': (0, 200, 255),
    
    # 그래프
    'graph_bg': (35, 40, 45),
    'graph_line_best': (255, 215, 0),
    'graph_line_avg': (0, 200, 255),
    'graph_grid': (60, 65, 70),
    
    # 신경망 시각화
    'neuron_input': (100, 200, 255),
    'neuron_hidden': (200, 200, 200),
    'neuron_output': (255, 200, 100),
    'connection_positive': (100, 255, 100),
    'connection_negative': (255, 100, 100),
    
    # 버튼
    'button': (70, 75, 80),
    'button_hover': (90, 95, 100),
    'button_active': (0, 150, 200),
    
    # 학습 단계
    'phase_active': (0, 200, 100),
    'phase_inactive': (80, 85, 90),
}

# === 폰트 크기 ===
FONT_TITLE = 28
FONT_LARGE = 22
FONT_MEDIUM = 18
FONT_SMALL = 14

# === 파일 경로 ===
NEAT_CONFIG_PATH = 'neat_config.txt'
