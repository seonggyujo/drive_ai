"""
UI 패널 모듈 - iOS 스타일 디자인
- 학습 현황 표시
- 신경망 시각화
- 세대별 점수 그래프
- 배속 조절
- 실시간 해설
"""
import pygame
from typing import List, Optional, Dict, Any, Tuple

from config import (
    COLORS, PANEL_X, PANEL_WIDTH, PANEL_PADDING,
    SCREEN_HEIGHT, GENERATION_TIME, SPEED_OPTIONS,
    CARD_RADIUS, CARD_PADDING, CARD_SPACING,
    FONT_TITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_CAPTION
)


class UIPanel:
    def __init__(self):
        self.x = PANEL_X
        self.y = 0
        self.width = PANEL_WIDTH
        self.height = SCREEN_HEIGHT
        
        # 폰트 초기화
        pygame.font.init()
        self.font_title = pygame.font.SysFont('malgungothic', FONT_TITLE, bold=True)
        self.font_large = pygame.font.SysFont('malgungothic', FONT_LARGE, bold=True)
        self.font_medium = pygame.font.SysFont('malgungothic', FONT_MEDIUM)
        self.font_small = pygame.font.SysFont('malgungothic', FONT_SMALL)
        self.font_caption = pygame.font.SysFont('malgungothic', FONT_CAPTION)
        
        # 그래프 데이터
        self.best_scores: List[float] = []
        self.avg_scores: List[float] = []
        
        # 배속 버튼 영역 저장 (클릭 감지용)
        self.speed_buttons: List[Tuple[pygame.Rect, int]] = []
        
        # 현재 배속
        self.current_speed = 1
    
    def update_scores(self, best: float, avg: float):
        """점수 데이터 추가"""
        self.best_scores.append(best)
        self.avg_scores.append(avg)
    
    def get_comment(self, generation: int, alive_count: int, total_count: int) -> str:
        """세대 및 상태에 따른 해설"""
        survival_rate = alive_count / total_count if total_count > 0 else 0
        
        if generation <= 3:
            return "아직 운전을 모릅니다... 벽에 부딪히는 중"
        elif generation <= 10:
            if survival_rate > 0.5:
                return "직진은 배웠습니다! 커브가 문제네요..."
            else:
                return "대부분 탈락... 더 연습이 필요합니다"
        elif generation <= 30:
            if survival_rate > 0.3:
                return "커브를 도는 법을 익히는 중!"
            else:
                return "어려운 구간에서 고전 중..."
        elif generation <= 60:
            return "점점 빨라지고 있습니다!"
        else:
            return "최적의 주행 경로를 찾았습니다!"
    
    def handle_click(self, pos: Tuple[int, int], simulation) -> bool:
        """마우스 클릭 처리 - 배속 버튼"""
        for rect, speed in self.speed_buttons:
            if rect.collidepoint(pos):
                simulation.speed_multiplier = speed
                self.current_speed = speed
                return True
        return False
    
    def _draw_card(self, surface: pygame.Surface, x: int, y: int, 
                   width: int, height: int) -> pygame.Rect:
        """iOS 스타일 카드 배경 그리기"""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, COLORS['bg_secondary'], rect, border_radius=CARD_RADIUS)
        return rect
    
    def _draw_progress_bar(self, surface: pygame.Surface, x: int, y: int, 
                           width: int, height: int, progress: float, 
                           color: Optional[Tuple[int, int, int]] = None):
        """iOS 스타일 프로그레스 바"""
        if color is None:
            color = COLORS['progress_fill']
        
        # 배경
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, COLORS['progress_bg'], bg_rect, border_radius=height // 2)
        
        # 채우기
        fill_width = int(width * min(progress, 1.0))
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(surface, color, fill_rect, border_radius=height // 2)
    
    def draw(self, surface: pygame.Surface, 
             generation: int, 
             alive_count: int, 
             total_count: int,
             time_left: float,
             best_fitness: float,
             speed_multiplier: int = 1,
             best_genome: Optional[Any] = None,
             best_net: Optional[Any] = None):
        """UI 패널 전체 그리기"""
        
        self.current_speed = speed_multiplier
        
        # 패널 배경
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS['bg_primary'], panel_rect)
        
        # 좌측 구분선
        pygame.draw.line(surface, COLORS['separator'], 
                        (self.x, 0), (self.x, self.height), 1)
        
        content_x = self.x + PANEL_PADDING
        content_width = self.width - PANEL_PADDING * 2
        y = PANEL_PADDING
        
        # ===== 헤더: 세대 + 배속 =====
        # 세대 (큰 숫자)
        gen_label = self.font_small.render("세대", True, COLORS['text_secondary'])
        surface.blit(gen_label, (content_x, y))
        
        gen_value = self.font_title.render(str(generation), True, COLORS['text_primary'])
        surface.blit(gen_value, (content_x, y + 20))
        
        # 배속 표시 (우측)
        speed_label = self.font_caption.render(f"x{speed_multiplier}", True, COLORS['accent_blue'])
        surface.blit(speed_label, (content_x + content_width - speed_label.get_width(), y + 30))
        
        y += 70
        
        # ===== 시간 프로그레스 바 =====
        time_progress = time_left / GENERATION_TIME
        self._draw_progress_bar(surface, content_x, y, content_width, 6, time_progress)
        
        time_text = self.font_caption.render(f"{time_left:.1f}초 남음", True, COLORS['text_secondary'])
        surface.blit(time_text, (content_x + content_width - time_text.get_width(), y + 10))
        
        y += 35
        
        # ===== 카드 1: 생존 현황 =====
        card1 = self._draw_card(surface, content_x, y, content_width, 100)
        card_inner_x = content_x + CARD_PADDING
        card_inner_y = y + CARD_PADDING
        
        # 생존
        survival_label = self.font_small.render("생존", True, COLORS['text_secondary'])
        surface.blit(survival_label, (card_inner_x, card_inner_y))
        
        survival_progress = alive_count / total_count if total_count > 0 else 0
        bar_y = card_inner_y + 22
        self._draw_progress_bar(surface, card_inner_x, bar_y, 
                               content_width - CARD_PADDING * 2, 8, 
                               survival_progress, COLORS['accent_green'])
        
        survival_text = self.font_medium.render(f"{alive_count} / {total_count}", 
                                                True, COLORS['text_primary'])
        surface.blit(survival_text, (card_inner_x + content_width - CARD_PADDING * 2 - survival_text.get_width(), 
                                     card_inner_y))
        
        # 최고 점수
        score_y = bar_y + 20
        score_label = self.font_small.render("최고 점수", True, COLORS['text_secondary'])
        surface.blit(score_label, (card_inner_x, score_y))
        
        score_value = self.font_large.render(f"{best_fitness:,.0f}", True, COLORS['accent_orange'])
        surface.blit(score_value, (card_inner_x + content_width - CARD_PADDING * 2 - score_value.get_width(), 
                                   score_y - 4))
        
        y += 100 + CARD_SPACING
        
        # ===== 카드 2: 신경망 시각화 =====
        card2 = self._draw_card(surface, content_x, y, content_width, 160)
        
        nn_label = self.font_small.render("신경망", True, COLORS['text_secondary'])
        surface.blit(nn_label, (content_x + CARD_PADDING, y + CARD_PADDING))
        
        nn_rect = pygame.Rect(content_x + CARD_PADDING, y + CARD_PADDING + 25, 
                              content_width - CARD_PADDING * 2, 120)
        self._draw_neural_network(surface, nn_rect, best_genome, best_net)
        
        y += 160 + CARD_SPACING
        
        # ===== 카드 3: 점수 그래프 =====
        card3 = self._draw_card(surface, content_x, y, content_width, 140)
        
        graph_label = self.font_small.render("점수 추이", True, COLORS['text_secondary'])
        surface.blit(graph_label, (content_x + CARD_PADDING, y + CARD_PADDING))
        
        graph_rect = pygame.Rect(content_x + CARD_PADDING, y + CARD_PADDING + 25, 
                                 content_width - CARD_PADDING * 2, 100)
        self._draw_graph(surface, graph_rect)
        
        y += 140 + CARD_SPACING
        
        # ===== 카드 4: 배속 선택 =====
        card4 = self._draw_card(surface, content_x, y, content_width, 70)
        
        speed_label = self.font_small.render("배속", True, COLORS['text_secondary'])
        surface.blit(speed_label, (content_x + CARD_PADDING, y + CARD_PADDING))
        
        self._draw_speed_buttons(surface, content_x + CARD_PADDING, y + CARD_PADDING + 25, 
                                 content_width - CARD_PADDING * 2, speed_multiplier)
        
        y += 70 + CARD_SPACING
        
        # ===== 카드 5: 해설 =====
        comment = self.get_comment(generation, alive_count, total_count)
        card5 = self._draw_card(surface, content_x, y, content_width, 60)
        
        comment_surf = self.font_medium.render(comment, True, COLORS['text_primary'])
        comment_x = content_x + CARD_PADDING
        comment_y = y + (60 - comment_surf.get_height()) // 2
        surface.blit(comment_surf, (comment_x, comment_y))
        
        y += 60 + CARD_SPACING
        
        # ===== 범례 =====
        legend_y = y + 5
        legends = [
            (COLORS['car_best'], "1위"),
            (COLORS['car_alive'], "생존"),
            (COLORS['car_dead'], "탈락"),
        ]
        
        legend_x = content_x
        for color, name in legends:
            pygame.draw.circle(surface, color, (legend_x + 6, legend_y + 8), 6)
            label = self.font_caption.render(name, True, COLORS['text_secondary'])
            surface.blit(label, (legend_x + 18, legend_y + 2))
            legend_x += 70
    
    def _draw_speed_buttons(self, surface: pygame.Surface, x: int, y: int, 
                            width: int, current_speed: int):
        """배속 버튼 그리기"""
        self.speed_buttons = []
        
        button_count = len(SPEED_OPTIONS)
        button_spacing = 10
        button_width = (width - button_spacing * (button_count - 1)) // button_count
        button_height = 32
        
        for i, speed in enumerate(SPEED_OPTIONS):
            btn_x = x + i * (button_width + button_spacing)
            btn_rect = pygame.Rect(btn_x, y, button_width, button_height)
            
            # 선택 상태에 따른 색상
            if speed == current_speed:
                bg_color = COLORS['accent_blue']
                text_color = COLORS['text_primary']
            else:
                bg_color = COLORS['bg_tertiary']
                text_color = COLORS['text_secondary']
            
            pygame.draw.rect(surface, bg_color, btn_rect, border_radius=8)
            
            # 텍스트
            btn_text = self.font_medium.render(f"x{speed}", True, text_color)
            text_x = btn_x + (button_width - btn_text.get_width()) // 2
            text_y = y + (button_height - btn_text.get_height()) // 2
            surface.blit(btn_text, (text_x, text_y))
            
            # 클릭 영역 저장
            self.speed_buttons.append((btn_rect, speed))
    
    def _draw_neural_network(self, surface: pygame.Surface, rect: pygame.Rect,
                             genome: Optional[Any], net: Optional[Any]):
        """신경망 구조 시각화"""
        if genome is None:
            no_data = self.font_small.render("대기 중...", True, COLORS['text_tertiary'])
            surface.blit(no_data, (rect.centerx - no_data.get_width()//2, 
                                   rect.centery - no_data.get_height()//2))
            return
        
        # 레이어 위치
        padding_x = 50
        padding_y = 15
        
        input_x = rect.x + padding_x
        output_x = rect.x + rect.width - padding_x
        
        # 입력 노드 (5개)
        input_nodes = []
        input_labels = ["전방", "좌45", "우45", "좌90", "우90"]
        node_spacing = (rect.height - padding_y * 2) / 4
        
        for i in range(5):
            node_y = rect.y + padding_y + i * node_spacing
            input_nodes.append((input_x, node_y))
        
        # 출력 노드 (2개)
        output_nodes = []
        output_labels = ["조향", "가속"]
        output_spacing = (rect.height - padding_y * 2) / 1
        
        for i in range(2):
            node_y = rect.y + padding_y + rect.height // 2 - 30 + i * 60
            output_nodes.append((output_x, node_y))
        
        # 연결선 그리기
        for inp in input_nodes:
            for out in output_nodes:
                pygame.draw.line(surface, COLORS['separator'], inp, out, 1)
        
        # 입력 노드 그리기
        for i, (nx, ny) in enumerate(input_nodes):
            pygame.draw.circle(surface, COLORS['neuron_input'], (int(nx), int(ny)), 8)
            pygame.draw.circle(surface, COLORS['bg_secondary'], (int(nx), int(ny)), 8, 2)
            label = self.font_caption.render(input_labels[i], True, COLORS['text_tertiary'])
            surface.blit(label, (nx - 35, ny - 6))
        
        # 출력 노드 그리기
        for i, (nx, ny) in enumerate(output_nodes):
            pygame.draw.circle(surface, COLORS['neuron_output'], (int(nx), int(ny)), 8)
            pygame.draw.circle(surface, COLORS['bg_secondary'], (int(nx), int(ny)), 8, 2)
            label = self.font_caption.render(output_labels[i], True, COLORS['text_tertiary'])
            surface.blit(label, (nx + 12, ny - 6))
    
    def _draw_graph(self, surface: pygame.Surface, rect: pygame.Rect):
        """점수 그래프 그리기"""
        if len(self.best_scores) < 2:
            no_data = self.font_small.render("데이터 수집 중...", True, COLORS['text_tertiary'])
            surface.blit(no_data, (rect.centerx - no_data.get_width()//2, 
                                   rect.centery - no_data.get_height()//2))
            return
        
        padding = 10
        graph_width = rect.width - padding * 2
        graph_height = rect.height - padding * 2
        
        max_score = max(max(self.best_scores), max(self.avg_scores)) if self.best_scores else 1
        min_score = 0
        score_range = max(max_score - min_score, 1)
        
        # 그리드 라인 (미니멀)
        for i in range(3):
            y = rect.y + padding + (graph_height * i // 2)
            pygame.draw.line(surface, COLORS['graph_grid'], 
                           (rect.x + padding, y), (rect.x + rect.width - padding, y), 1)
        
        # 최고 점수 라인
        if len(self.best_scores) >= 2:
            points = []
            for i, score in enumerate(self.best_scores[-50:]):  # 최근 50개만
                x = rect.x + padding + (i / max(len(self.best_scores[-50:]) - 1, 1)) * graph_width
                y = rect.y + padding + graph_height - ((score - min_score) / score_range) * graph_height
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, COLORS['graph_line_best'], False, points, 2)
        
        # 평균 점수 라인
        if len(self.avg_scores) >= 2:
            points = []
            for i, score in enumerate(self.avg_scores[-50:]):  # 최근 50개만
                x = rect.x + padding + (i / max(len(self.avg_scores[-50:]) - 1, 1)) * graph_width
                y = rect.y + padding + graph_height - ((score - min_score) / score_range) * graph_height
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, COLORS['graph_line_avg'], False, points, 2)
        
        # 범례 (우상단)
        legend_x = rect.x + rect.width - 80
        legend_y = rect.y + 5
        
        pygame.draw.line(surface, COLORS['graph_line_best'], 
                        (legend_x, legend_y + 5), (legend_x + 15, legend_y + 5), 2)
        best_label = self.font_caption.render("최고", True, COLORS['text_tertiary'])
        surface.blit(best_label, (legend_x + 20, legend_y))
        
        pygame.draw.line(surface, COLORS['graph_line_avg'], 
                        (legend_x, legend_y + 20), (legend_x + 15, legend_y + 20), 2)
        avg_label = self.font_caption.render("평균", True, COLORS['text_tertiary'])
        surface.blit(avg_label, (legend_x + 20, legend_y + 15))
