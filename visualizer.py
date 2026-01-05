"""
시각화 모듈
- 트랙 렌더링
- 차량 렌더링 (순위별 색상)
- 전체 화면 관리
"""
import pygame
from typing import List, Optional

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from track import Track
from car import Car


class Visualizer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
    def draw_background(self):
        """배경 그리기"""
        self.screen.fill(COLORS['track_grass'])
    
    def draw_track(self, track: Track):
        """트랙 그리기"""
        track.draw(self.screen)
    
    def draw_cars(self, cars: List[Car], best_car_id: Optional[int] = None):
        """
        모든 차량 그리기
        - 죽은 차량 먼저 (뒤에)
        - 살아있는 차량 나중에 (앞에)
        - 최고 차량은 센서 표시
        """
        # 죽은 차량 먼저
        for car in cars:
            if not car.alive:
                car.draw(self.screen, is_best=False, show_sensors=False)
        
        # 살아있는 차량 (최고 차량 제외)
        for car in cars:
            if car.alive and car.car_id != best_car_id:
                car.draw(self.screen, is_best=False, show_sensors=False)
        
        # 최고 차량 (센서 표시)
        for car in cars:
            if car.alive and car.car_id == best_car_id:
                car.draw(self.screen, is_best=True, show_sensors=True)
    
    def draw_generation_info(self, generation: int, alive_count: int, total_count: int, 
                             time_left: float, best_fitness: float):
        """화면 좌상단에 간단한 정보 표시"""
        font = pygame.font.SysFont('malgungothic', 18)
        
        texts = [
            f"세대: {generation}",
            f"생존: {alive_count}/{total_count}",
            f"남은 시간: {time_left:.1f}초",
            f"최고 점수: {best_fitness:.0f}"
        ]
        
        y = 10
        for text in texts:
            surface = font.render(text, True, (255, 255, 255))
            # 그림자 효과
            shadow = font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, (12, y + 2))
            self.screen.blit(surface, (10, y))
            y += 25
    
    def render(self, track: Track, cars: List[Car], 
               generation: int, time_left: float,
               best_car_id: Optional[int] = None):
        """전체 렌더링"""
        # 배경
        self.draw_background()
        
        # 트랙
        self.draw_track(track)
        
        # 차량들
        self.draw_cars(cars, best_car_id)
        
        # 정보 (UI 패널이 있으면 이건 생략 가능)
        alive_count = sum(1 for car in cars if car.alive)
        best_fitness = max((car.fitness for car in cars), default=0)
        self.draw_generation_info(generation, alive_count, len(cars), time_left, best_fitness)
