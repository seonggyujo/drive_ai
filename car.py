"""
차량 클래스 모듈
- 물리 엔진 (가속, 감속, 회전)
- 5방향 센서
- 충돌 감지
"""
import pygame
import math
from typing import List, Tuple, Optional

from config import (
    CAR_WIDTH, CAR_HEIGHT,
    CAR_MAX_SPEED, CAR_MIN_SPEED,
    CAR_ACCELERATION, CAR_FRICTION, CAR_TURN_SPEED,
    SENSOR_COUNT, SENSOR_MAX_LENGTH, SENSOR_ANGLES,
    COLORS
)


class Car:
    def __init__(self, x: float, y: float, angle: float, car_id: int = 0):
        # 위치 및 방향
        self.x = x
        self.y = y
        self.angle = angle  # 도 단위 (0 = 오른쪽, 90 = 위)
        
        # 속도
        self.speed = 0
        self.acceleration = 0
        
        # 상태
        self.alive = True
        self.car_id = car_id
        
        # 점수
        self.fitness = 0
        self.distance_traveled = 0
        self.last_checkpoint = 0
        self.checkpoints_passed = 0
        self.time_alive = 0
        
        # 센서 데이터
        self.sensor_data: List[float] = [0] * SENSOR_COUNT
        
        # 크기
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        
        # 색상 (나중에 순위에 따라 변경)
        self.color = COLORS['car_alive']
    
    def reset(self, x: float, y: float, angle: float):
        """차량 상태 초기화"""
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0
        self.acceleration = 0
        self.alive = True
        self.fitness = 0
        self.distance_traveled = 0
        self.last_checkpoint = 0
        self.checkpoints_passed = 0
        self.time_alive = 0
        self.sensor_data = [0] * SENSOR_COUNT
    
    def get_inputs(self) -> List[float]:
        """신경망 입력값 반환 (정규화된 센서 데이터)"""
        # 센서 데이터를 0~1 범위로 정규화
        return [s / SENSOR_MAX_LENGTH for s in self.sensor_data]
    
    def set_outputs(self, outputs: List[float]):
        """
        신경망 출력값 적용
        outputs[0]: 조향 (-1 = 좌회전, 1 = 우회전)
        outputs[1]: 가속 (-1 = 감속, 1 = 가속)
        """
        if not self.alive:
            return
        
        # 조향
        turn = outputs[0] * CAR_TURN_SPEED
        self.angle += turn
        
        # 가속/감속
        self.acceleration = outputs[1] * CAR_ACCELERATION
    
    def update(self, track) -> bool:
        """
        차량 상태 업데이트
        Returns: 생존 여부
        """
        if not self.alive:
            return False
        
        # 마찰력 적용
        if self.speed > 0:
            self.speed -= CAR_FRICTION
        elif self.speed < 0:
            self.speed += CAR_FRICTION
        
        # 가속도 적용
        self.speed += self.acceleration
        
        # 속도 제한
        self.speed = max(CAR_MIN_SPEED, min(CAR_MAX_SPEED, self.speed))
        
        # 위치 업데이트
        rad = math.radians(self.angle)
        old_x, old_y = self.x, self.y
        
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed  # pygame 좌표계
        
        # 이동 거리 업데이트
        self.distance_traveled += math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
        
        # 충돌 감지
        if not track.is_on_track(self.x, self.y):
            self.alive = False
            return False
        
        # 체크포인트 확인
        new_checkpoint = track.get_checkpoint_index(self.x, self.y, self.last_checkpoint)
        if new_checkpoint != self.last_checkpoint:
            self.last_checkpoint = new_checkpoint
            self.checkpoints_passed += 1
        
        # 시간 업데이트
        self.time_alive += 1
        
        # 적합도 계산
        self._calculate_fitness()
        
        return True
    
    def update_sensors(self, track):
        """센서 데이터 업데이트"""
        if not self.alive:
            return
        
        for i, sensor_angle in enumerate(SENSOR_ANGLES):
            # 차량 방향 기준으로 센서 각도 계산
            absolute_angle = self.angle + sensor_angle
            
            # 트랙 경계까지의 거리 측정
            distance = track.get_distance_to_edge(self.x, self.y, absolute_angle)
            self.sensor_data[i] = min(distance, SENSOR_MAX_LENGTH)
    
    def _calculate_fitness(self):
        """적합도 계산"""
        # 체크포인트 통과 보상 + 이동 거리 보상
        self.fitness = (self.checkpoints_passed * 1000) + self.distance_traveled
    
    def get_corners(self) -> List[Tuple[float, float]]:
        """차량의 4개 모서리 좌표 반환 (회전 적용)"""
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # 반폭, 반높이
        hw = self.width / 2
        hh = self.height / 2
        
        # 각 모서리 (차량 중심 기준)
        corners_local = [
            (-hw, -hh),  # 좌상
            (hw, -hh),   # 우상
            (hw, hh),    # 우하
            (-hw, hh),   # 좌하
        ]
        
        # 회전 적용
        corners = []
        for lx, ly in corners_local:
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            corners.append((self.x + rx, self.y + ry))
        
        return corners
    
    def draw(self, surface: pygame.Surface, is_best: bool = False, show_sensors: bool = False):
        """차량 그리기"""
        if not self.alive:
            color = COLORS['car_dead']
            alpha = 100
        else:
            color = COLORS['car_best'] if is_best else self.color
            alpha = 255
        
        # 차량 본체 (회전된 사각형)
        corners = self.get_corners()
        
        if self.alive:
            pygame.draw.polygon(surface, color, corners)
            pygame.draw.polygon(surface, (255, 255, 255), corners, 1)
        else:
            # 죽은 차량은 반투명
            s = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            local_corners = [
                (5, 5),
                (self.width + 5, 5),
                (self.width + 5, self.height + 5),
                (5, self.height + 5)
            ]
            pygame.draw.polygon(s, (*color, alpha), local_corners)
            
            # 회전 적용
            rotated = pygame.transform.rotate(s, self.angle)
            rect = rotated.get_rect(center=(self.x, self.y))
            surface.blit(rotated, rect)
            return
        
        # 차량 전면 표시 (방향)
        rad = math.radians(self.angle)
        front_x = self.x + math.cos(rad) * self.width * 0.4
        front_y = self.y - math.sin(rad) * self.width * 0.4
        pygame.draw.circle(surface, (255, 255, 255), (int(front_x), int(front_y)), 3)
        
        # 센서 그리기 (최고 차량만)
        if show_sensors and self.alive:
            self._draw_sensors(surface)
    
    def _draw_sensors(self, surface: pygame.Surface):
        """센서 레이저 그리기"""
        for i, sensor_angle in enumerate(SENSOR_ANGLES):
            absolute_angle = self.angle + sensor_angle
            rad = math.radians(absolute_angle)
            
            end_x = self.x + math.cos(rad) * self.sensor_data[i]
            end_y = self.y - math.sin(rad) * self.sensor_data[i]
            
            # 센서 선 (거리에 따라 색상 변화)
            ratio = self.sensor_data[i] / SENSOR_MAX_LENGTH
            color = (
                int(255 * (1 - ratio)),  # 가까우면 빨강
                int(255 * ratio),         # 멀면 초록
                0
            )
            
            pygame.draw.line(surface, color, 
                           (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), 2)
            
            # 끝점 표시
            pygame.draw.circle(surface, color, (int(end_x), int(end_y)), 4)
