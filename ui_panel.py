"""
UI 패널 모듈
- 정보 표시 (Episode, Step, ε, 성공률)
- 속도 버튼 (1x, 5x, 10x, MAX)
- 학습 곡선 그래프
- 제어 버튼 (Pause, Reset)
"""
import pygame
from typing import List, Tuple, Optional, Callable

from config import (
    COLORS, PANEL_WIDTH, BUTTON_HEIGHT, WINDOW_PADDING,
    SPEED_1X, SPEED_5X, SPEED_10X, SPEED_MAX, MAX_EPISODES
)


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback: Callable):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.active = False
        self.hovered = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if self.active:
            color = COLORS['button_active']
        elif self.hovered:
            color = (90, 90, 90)
        else:
            color = COLORS['button']
        
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['text'], self.rect, 1, border_radius=5)
        
        text_surface = font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False


class UIPanel:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
        # 폰트 초기화
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 14)
        
        # 버튼들
        self.buttons: List[Button] = []
        self.speed_buttons: List[Button] = []
        
        # 현재 속도
        self.current_speed = SPEED_1X
        self.paused = False
        
        # 학습 곡선 데이터
        self.graph_data: List[int] = []
        self.graph_rect = pygame.Rect(x + 10, y + 250, width - 20, 120)
        
        # 콜백 (main.py에서 설정)
        self.on_speed_change: Optional[Callable] = None
        self.on_pause: Optional[Callable] = None
        self.on_reset: Optional[Callable] = None
        
        self._setup_buttons()
    
    def _setup_buttons(self):
        """버튼 초기화"""
        btn_width = 55
        btn_height = 35
        btn_y = self.y + 180
        spacing = 5
        start_x = self.x + 10
        
        # 속도 버튼
        speeds = [('1x', SPEED_1X), ('5x', SPEED_5X), ('10x', SPEED_10X), ('MAX', SPEED_MAX)]
        for i, (label, speed) in enumerate(speeds):
            btn = Button(
                start_x + i * (btn_width + spacing), btn_y,
                btn_width, btn_height, label,
                lambda s=speed: self._set_speed(s)
            )
            if speed == self.current_speed:
                btn.active = True
            self.speed_buttons.append(btn)
        
        # 제어 버튼
        ctrl_y = btn_y + btn_height + 10
        ctrl_width = (btn_width * 2 + spacing)
        
        self.pause_button = Button(
            start_x, ctrl_y, ctrl_width, btn_height,
            'PAUSE', self._toggle_pause
        )
        self.reset_button = Button(
            start_x + ctrl_width + spacing, ctrl_y, ctrl_width, btn_height,
            'RESET', self._do_reset
        )
        
        self.buttons = self.speed_buttons + [self.pause_button, self.reset_button]
    
    def _set_speed(self, speed: int):
        """속도 변경"""
        self.current_speed = speed
        for btn in self.speed_buttons:
            btn.active = False
        for btn in self.speed_buttons:
            if (btn.text == '1x' and speed == SPEED_1X) or \
               (btn.text == '5x' and speed == SPEED_5X) or \
               (btn.text == '10x' and speed == SPEED_10X) or \
               (btn.text == 'MAX' and speed == SPEED_MAX):
                btn.active = True
        if self.on_speed_change:
            self.on_speed_change(speed)
    
    def _toggle_pause(self):
        """일시정지 토글"""
        self.paused = not self.paused
        self.pause_button.text = 'RESUME' if self.paused else 'PAUSE'
        if self.on_pause:
            self.on_pause(self.paused)
    
    def _do_reset(self):
        """초기화"""
        self.graph_data = []
        if self.on_reset:
            self.on_reset()
    
    def handle_event(self, event: pygame.event.Event):
        """이벤트 처리"""
        for btn in self.buttons:
            btn.handle_event(event)
    
    def update_graph(self, episode_steps: List[int]):
        """그래프 데이터 업데이트"""
        self.graph_data = episode_steps
    
    def draw(self, surface: pygame.Surface, episode: int, step: int, 
             epsilon: float, success_rate: float, avg_steps: float):
        """패널 전체 그리기"""
        # 배경
        pygame.draw.rect(surface, COLORS['panel_bg'], self.rect, border_radius=10)
        
        # 제목
        title = self.font_large.render('Learning Status', True, COLORS['text'])
        surface.blit(title, (self.x + 10, self.y + 10))
        
        # 정보 표시
        info_y = self.y + 50
        line_height = 28
        
        infos = [
            f'Episode: {episode} / {MAX_EPISODES}',
            f'Step: {step}',
            f'Epsilon: {epsilon:.3f}',
            f'Success Rate: {success_rate*100:.1f}%',
            f'Avg Steps: {avg_steps:.1f}' if avg_steps > 0 else 'Avg Steps: -'
        ]
        
        for i, text in enumerate(infos):
            rendered = self.font_medium.render(text, True, COLORS['text'])
            surface.blit(rendered, (self.x + 15, info_y + i * line_height))
        
        # 버튼 그리기
        for btn in self.buttons:
            btn.draw(surface, self.font_small)
        
        # 학습 곡선 그래프
        self._draw_graph(surface)
    
    def _draw_graph(self, surface: pygame.Surface):
        """학습 곡선 그래프 그리기"""
        # 그래프 배경
        pygame.draw.rect(surface, COLORS['graph_bg'], self.graph_rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['text'], self.graph_rect, 1, border_radius=5)
        
        # 제목
        title = self.font_small.render('Steps per Episode', True, COLORS['text'])
        surface.blit(title, (self.graph_rect.x + 5, self.graph_rect.y - 18))
        
        if len(self.graph_data) < 2:
            # 데이터 없음
            no_data = self.font_small.render('Waiting for data...', True, (150, 150, 150))
            no_data_rect = no_data.get_rect(center=self.graph_rect.center)
            surface.blit(no_data, no_data_rect)
            return
        
        # 그래프 그리기
        padding = 10
        graph_width = self.graph_rect.width - padding * 2
        graph_height = self.graph_rect.height - padding * 2
        
        max_steps = max(self.graph_data) if self.graph_data else 1
        min_steps = min(self.graph_data) if self.graph_data else 0
        step_range = max(max_steps - min_steps, 1)
        
        # 이동 평균 계산 (최근 10개)
        window = 10
        smoothed = []
        for i in range(len(self.graph_data)):
            start = max(0, i - window + 1)
            smoothed.append(sum(self.graph_data[start:i+1]) / (i - start + 1))
        
        # 포인트 계산
        points = []
        for i, val in enumerate(smoothed):
            x = self.graph_rect.x + padding + (i / max(len(smoothed) - 1, 1)) * graph_width
            y = self.graph_rect.y + padding + graph_height - ((val - min_steps) / step_range) * graph_height
            points.append((x, y))
        
        # 선 그리기
        if len(points) >= 2:
            pygame.draw.lines(surface, COLORS['graph_line'], False, points, 2)
        
        # 최신값 표시
        if self.graph_data:
            latest = self.graph_data[-1]
            latest_text = self.font_small.render(f'{latest}', True, COLORS['graph_line'])
            surface.blit(latest_text, (self.graph_rect.right - 30, self.graph_rect.y + 5))
