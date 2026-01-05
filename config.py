"""
Q-Learning 미로 AI 시각화 프로젝트 설정
"""
from enum import IntEnum


# === 행동 정의 ===
class Action(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


# === 셀 타입 정의 ===
class CellType(IntEnum):
    PATH = 0
    WALL = 1
    START = 2
    GOAL = 3


# === 미로 설정 ===
MAZE_SIZE = 7  # 7x7
CELL_SIZE = 60  # 픽셀

# === 학습 하이퍼파라미터 ===
LEARNING_RATE = 0.1        # α
DISCOUNT_FACTOR = 0.95     # γ
EPSILON_START = 1.0        # 초기 탐험률
EPSILON_END = 0.01         # 최소 탐험률
EPSILON_DECAY = 0.99       # 감쇠율
MAX_STEPS_PER_EPISODE = 200
MAX_EPISODES = 500

# === 보상 ===
REWARD_GOAL = 100
REWARD_WALL = -1
REWARD_STEP = -0.1

# === 속도 설정 (에피소드 간 딜레이 ms) ===
SPEED_1X = 100    # 느림 (관찰용)
SPEED_5X = 20     # 보통
SPEED_10X = 5     # 빠름
SPEED_MAX = 0     # 최대 (렌더링 유지, 딜레이 없음)

# === 색상 (RGB) ===
COLORS = {
    'wall': (40, 40, 40),
    'path': (240, 240, 240),
    'start': (100, 149, 237),    # 파란색
    'goal': (50, 205, 50),       # 초록색
    'agent_exploit': (220, 60, 60),    # 빨간색 (활용)
    'agent_explore': (255, 165, 0),    # 주황색 (탐험)
    'trail': (255, 200, 200),    # 경로 잔상
    'heatmap_low': (255, 255, 255),    # Q값 낮음
    'heatmap_high': (255, 100, 100),   # Q값 높음
    'arrow': (80, 80, 80),       # 화살표
    'background': (30, 30, 30),
    'panel_bg': (50, 50, 50),
    'text': (255, 255, 255),
    'button': (70, 70, 70),
    'button_active': (100, 100, 100),
    'graph_line': (0, 200, 255),
    'graph_bg': (40, 40, 40),
}

# === 화면 설정 ===
PANEL_WIDTH = 280
BUTTON_HEIGHT = 40
WINDOW_PADDING = 20
