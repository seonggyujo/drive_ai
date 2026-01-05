# Self-Driving AI Visualization

NEAT 알고리즘을 사용한 자율주행 AI 학습 시각화 프로젝트입니다.

20대의 차량이 타원형 트랙에서 동시에 학습하며, 신경망이 어떻게 진화하는지 실시간으로 관찰할 수 있습니다.

## 데모

![demo](https://via.placeholder.com/800x450?text=Demo+GIF+Coming+Soon)

## 주요 기능

- **20대 동시 학습**: 20대의 차량이 동시에 트랙을 주행하며 학습
- **NEAT 알고리즘**: 신경망 구조가 자동으로 진화 (NeuroEvolution of Augmenting Topologies)
- **5방향 센서**: 각 차량은 5개의 거리 센서를 통해 트랙을 인식
- **가속/감속 제어**: 조향뿐 아니라 속도 제어도 학습
- **실시간 시각화**: 
  - 신경망 구조 시각화
  - 세대별 점수 그래프
  - 실시간 학습 해설 (한국어)

## 설치

```bash
# 저장소 클론
git clone https://github.com/seonggyujo/drive_ai.git
cd drive_ai

# 의존성 설치
pip install pygame-ce neat-python numpy matplotlib
```

## 실행

```bash
python main.py
```

### 조작법

| 키 | 기능 |
|---|---|
| `ESC` | 종료 |
| `Space` | 일시정지/재개 |

## 프로젝트 구조

```
drive_ai/
├── main.py          # 메인 프로그램 (NEAT 통합)
├── config.py        # 설정값 (화면, 차량, 트랙 등)
├── neat_config.txt  # NEAT 알고리즘 설정
├── track.py         # 타원형 트랙 모듈
├── car.py           # 차량 클래스 (물리, 센서)
├── visualizer.py    # 트랙/차량 렌더링
└── ui_panel.py      # UI 패널 (한국어)
```

## 학습 과정

1. **탐험 단계** (세대 1-20): 무작위로 움직이며 기본 운전법 습득
2. **학습 단계** (세대 21-40): 커브를 도는 방법 학습
3. **최적화 단계** (세대 41+): 최적의 주행 경로 탐색

## 설정 변경

`config.py`에서 다음 값들을 조정할 수 있습니다:

| 설정 | 기본값 | 설명 |
|---|---|---|
| `CAR_COUNT` | 20 | 동시 학습 차량 수 |
| `GENERATION_TIME` | 30 | 세대당 시간 (초) |
| `CAR_MAX_SPEED` | 8 | 최대 속도 |
| `SENSOR_MAX_LENGTH` | 200 | 센서 최대 거리 |

## 기술 스택

- **Python 3.10+**
- **Pygame-CE** - 게임 렌더링
- **NEAT-Python** - 신경망 진화 알고리즘
- **NumPy** - 수치 계산

## 라이선스

MIT License
