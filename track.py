"""
타원형 트랙 모듈
- 트랙 경계 생성
- 충돌 감지
- 체크포인트 관리
"""
import pygame
import math
from typing import List, Tuple, Optional

from config import (
    TRACK_CENTER_X, TRACK_CENTER_Y,
    TRACK_WIDTH, TRACK_OUTER_A, TRACK_OUTER_B,
    COLORS
)


class Track:
    def __init__(self):
        self.center_x = TRACK_CENTER_X
        self.center_y = TRACK_CENTER_Y
        self.outer_a = TRACK_OUTER_A  # 외곽 타원 장축
        self.outer_b = TRACK_OUTER_B  # 외곽 타원 단축
        self.inner_a = TRACK_OUTER_A - TRACK_WIDTH  # 내부 타원 장축
        self.inner_b = TRACK_OUTER_B - TRACK_WIDTH  # 내부 타원 단축
        self.track_width = TRACK_WIDTH
        
        # 체크포인트 (트랙을 따라 배치)
        self.checkpoints = self._create_checkpoints(12)
        
        # 시작 위치/각도
        self.start_x = self.center_x + self.outer_a - self.track_width // 2
        self.start_y = self.center_y
        self.start_angle = 90  # 위쪽을 향함
        
        # 트랙 경계 포인트 (충돌 감지용)
        self.outer_points = self._generate_ellipse_points(self.outer_a, self.outer_b, 100)
        self.inner_points = self._generate_ellipse_points(self.inner_a, self.inner_b, 100)
    
    def _generate_ellipse_points(self, a: float, b: float, num_points: int) -> List[Tuple[float, float]]:
        """타원 위의 점들 생성"""
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = self.center_x + a * math.cos(angle)
            y = self.center_y + b * math.sin(angle)
            points.append((x, y))
        return points
    
    def _create_checkpoints(self, count: int) -> List[dict]:
        """체크포인트 생성"""
        checkpoints = []
        for i in range(count):
            angle = 2 * math.pi * i / count
            
            # 외곽 점
            outer_x = self.center_x + self.outer_a * math.cos(angle)
            outer_y = self.center_y + self.outer_b * math.sin(angle)
            
            # 내부 점
            inner_x = self.center_x + self.inner_a * math.cos(angle)
            inner_y = self.center_y + self.inner_b * math.sin(angle)
            
            checkpoints.append({
                'index': i,
                'outer': (outer_x, outer_y),
                'inner': (inner_x, inner_y),
                'angle': math.degrees(angle)
            })
        
        return checkpoints
    
    def is_on_track(self, x: float, y: float) -> bool:
        """주어진 점이 트랙 위에 있는지 확인"""
        # 타원 방정식: (x-cx)²/a² + (y-cy)²/b² = 1
        dx = x - self.center_x
        dy = y - self.center_y
        
        # 외곽 타원 내부인지
        outer_val = (dx * dx) / (self.outer_a * self.outer_a) + (dy * dy) / (self.outer_b * self.outer_b)
        
        # 내부 타원 외부인지
        inner_val = (dx * dx) / (self.inner_a * self.inner_a) + (dy * dy) / (self.inner_b * self.inner_b)
        
        return outer_val <= 1.0 and inner_val >= 1.0
    
    def get_distance_to_edge(self, x: float, y: float, angle: float) -> float:
        """주어진 점에서 특정 방향으로 트랙 경계까지의 거리"""
        # 라디안 변환
        rad = math.radians(angle)
        dx = math.cos(rad)
        dy = -math.sin(rad)  # pygame 좌표계 (y가 아래로 증가)
        
        # 레이캐스팅
        max_dist = 300
        step = 2
        
        for dist in range(0, max_dist, step):
            check_x = x + dx * dist
            check_y = y + dy * dist
            
            if not self.is_on_track(check_x, check_y):
                return dist
        
        return max_dist
    
    def get_checkpoint_index(self, x: float, y: float, last_checkpoint: int) -> int:
        """현재 위치에서 통과한 체크포인트 인덱스 반환"""
        next_checkpoint = (last_checkpoint + 1) % len(self.checkpoints)
        cp = self.checkpoints[next_checkpoint]
        
        # 체크포인트 선분과의 거리 계산
        ox, oy = cp['outer']
        ix, iy = cp['inner']
        
        # 점과 선분 사이의 거리
        dist = self._point_to_line_distance(x, y, ox, oy, ix, iy)
        
        # 체크포인트 통과 판정 (거리가 20 이하면 통과)
        if dist < 25:
            return next_checkpoint
        
        return last_checkpoint
    
    def _point_to_line_distance(self, px: float, py: float, 
                                 x1: float, y1: float, x2: float, y2: float) -> float:
        """점에서 선분까지의 거리"""
        line_len = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_len == 0:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)))
        
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)
    
    def get_start_positions(self, count: int) -> List[Tuple[float, float, float]]:
        """
        여러 차량의 시작 위치 반환 (겹치지 않게 분산)
        Returns: [(x, y, angle), ...]
        """
        positions = []
        
        # 트랙 시작 지점 근처에 간격을 두고 배치
        for i in range(count):
            # 시작점에서 트랙을 따라 조금씩 뒤로 배치
            angle_offset = (i // 2) * 0.15  # 2대씩 같은 위치, 조금씩 뒤로
            side_offset = (i % 2) * 30 - 15  # 좌우로 번갈아 배치
            
            angle = -angle_offset  # 시작점에서 반시계 방향으로
            
            # 트랙 중심선 위치
            center_a = (self.outer_a + self.inner_a) / 2
            center_b = (self.outer_b + self.inner_b) / 2
            
            x = self.center_x + center_a * math.cos(angle)
            y = self.center_y + center_b * math.sin(angle)
            
            # 좌우 오프셋 적용 (트랙 방향에 수직으로)
            perp_angle = angle + math.pi / 2
            x += side_offset * math.cos(perp_angle) * 0.3
            y += side_offset * math.sin(perp_angle) * 0.3
            
            # 차량이 바라보는 방향 (트랙 접선 방향)
            car_angle = math.degrees(angle) + 90
            
            positions.append((x, y, car_angle))
        
        return positions
    
    def draw(self, surface: pygame.Surface):
        """트랙 그리기"""
        # 잔디 배경 (이미 배경색으로 처리됨)
        
        # 외곽 타원 (도로)
        outer_rect = pygame.Rect(
            self.center_x - self.outer_a,
            self.center_y - self.outer_b,
            self.outer_a * 2,
            self.outer_b * 2
        )
        pygame.draw.ellipse(surface, COLORS['track_road'], outer_rect)
        
        # 내부 타원 (잔디)
        inner_rect = pygame.Rect(
            self.center_x - self.inner_a,
            self.center_y - self.inner_b,
            self.inner_a * 2,
            self.inner_b * 2
        )
        pygame.draw.ellipse(surface, COLORS['track_grass'], inner_rect)
        
        # 외곽 경계선
        pygame.draw.ellipse(surface, COLORS['track_border'], outer_rect, 3)
        
        # 내부 경계선
        pygame.draw.ellipse(surface, COLORS['track_border'], inner_rect, 3)
        
        # 중앙선 (점선)
        center_a = (self.outer_a + self.inner_a) / 2
        center_b = (self.outer_b + self.inner_b) / 2
        
        for i in range(0, 60, 2):  # 점선 효과
            angle1 = 2 * math.pi * i / 60
            angle2 = 2 * math.pi * (i + 1) / 60
            
            x1 = self.center_x + center_a * math.cos(angle1)
            y1 = self.center_y + center_b * math.sin(angle1)
            x2 = self.center_x + center_a * math.cos(angle2)
            y2 = self.center_y + center_b * math.sin(angle2)
            
            pygame.draw.line(surface, COLORS['track_center_line'], 
                           (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 시작/결승선
        start_outer = (self.center_x + self.outer_a, self.center_y)
        start_inner = (self.center_x + self.inner_a, self.center_y)
        pygame.draw.line(surface, (255, 255, 255), start_outer, start_inner, 4)
    
    def draw_checkpoints(self, surface: pygame.Surface, alpha: int = 50):
        """체크포인트 그리기 (디버그용)"""
        for cp in self.checkpoints:
            color = (*COLORS['checkpoint'][:3], alpha)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (2, 2), 2)
            
            ox, oy = cp['outer']
            ix, iy = cp['inner']
            
            # 체크포인트 선
            pygame.draw.line(surface, COLORS['checkpoint'], 
                           (int(ox), int(oy)), (int(ix), int(iy)), 1)
