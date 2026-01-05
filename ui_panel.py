"""
UI 패널 모듈 (한국어)
- 학습 현황 표시
- 신경망 시각화
- 세대별 점수 그래프
- 실시간 해설
"""
import pygame
from typing import List, Optional, Dict, Any

from config import (
    COLORS, PANEL_X, PANEL_WIDTH, PANEL_PADDING,
    SCREEN_HEIGHT, GENERATION_TIME,
    FONT_TITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL
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
        self.font_large = pygame.font.SysFont('malgungothic', FONT_LARGE)
        self.font_medium = pygame.font.SysFont('malgungothic', FONT_MEDIUM)
        self.font_small = pygame.font.SysFont('malgungothic', FONT_SMALL)
        
        # 그래프 데이터
        self.best_scores: List[float] = []
        self.avg_scores: List[float] = []
        
        # 현재 상태
        self.current_comment = "학습을 시작합니다..."
    
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
    
    def draw(self, surface: pygame.Surface, 
             generation: int, 
             alive_count: int, 
             total_count: int,
             time_left: float,
             best_fitness: float,
             best_genome: Optional[Any] = None,
             best_net: Optional[Any] = None):
        """UI 패널 전체 그리기"""
        
        # 패널 배경
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS['panel_bg'], panel_rect)
        pygame.draw.line(surface, COLORS['panel_border'], 
                        (self.x, 0), (self.x, self.height), 2)
        
        y_offset = PANEL_PADDING
        
        # === 제목 ===
        title = self.font_title.render("🚗 학습 현황", True, COLORS['text'])
        surface.blit(title, (self.x + PANEL_PADDING, y_offset))
        y_offset += 45
        
        # === 학습 정보 ===
        infos = [
            ("세대", f"{generation}"),
            ("생존", f"{alive_count} / {total_count}"),
            ("남은 시간", f"{time_left:.1f}초"),
            ("최고 점수", f"{best_fitness:.0f}"),
        ]
        
        for label, value in infos:
            label_surf = self.font_small.render(f"{label}:", True, COLORS['text_dim'])
            value_surf = self.font_medium.render(value, True, COLORS['text'])
            surface.blit(label_surf, (self.x + PANEL_PADDING, y_offset))
            surface.blit(value_surf, (self.x + 120, y_offset - 2))
            y_offset += 30
        
        y_offset += 10
        
        # === 학습 단계 ===
        phase_title = self.font_small.render("학습 단계:", True, COLORS['text_dim'])
        surface.blit(phase_title, (self.x + PANEL_PADDING, y_offset))
        y_offset += 25
        
        phases = ["탐험", "학습", "최적화"]
        phase_idx = min(generation // 20, 2)
        
        phase_width = 100
        phase_spacing = 10
        for i, phase in enumerate(phases):
            rect = pygame.Rect(
                self.x + PANEL_PADDING + i * (phase_width + phase_spacing),
                y_offset, phase_width, 8
            )
            color = COLORS['phase_active'] if i <= phase_idx else COLORS['phase_inactive']
            pygame.draw.rect(surface, color, rect, border_radius=4)
            
            label = self.font_small.render(phase, True, 
                                          COLORS['text'] if i <= phase_idx else COLORS['text_dim'])
            surface.blit(label, (rect.x + phase_width//2 - label.get_width()//2, y_offset + 12))
        
        y_offset += 50
        
        # === 실시간 해설 ===
        comment_rect = pygame.Rect(self.x + 10, y_offset, self.width - 20, 60)
        pygame.draw.rect(surface, COLORS['graph_bg'], comment_rect, border_radius=8)
        
        comment = self.get_comment(generation, alive_count, total_count)
        
        # 💡 아이콘
        icon_surf = self.font_medium.render("💡", True, COLORS['text'])
        surface.blit(icon_surf, (self.x + 20, y_offset + 10))
        
        # 해설 텍스트
        comment_surf = self.font_small.render(comment, True, COLORS['text'])
        surface.blit(comment_surf, (self.x + 50, y_offset + 12))
        
        # 부제목
        sub_comment = f"세대 {generation} - {phases[phase_idx]} 단계"
        sub_surf = self.font_small.render(sub_comment, True, COLORS['text_dim'])
        surface.blit(sub_surf, (self.x + 20, y_offset + 36))
        
        y_offset += 75
        
        # === 신경망 시각화 ===
        nn_title = self.font_small.render("🧠 신경망 (1위 차량)", True, COLORS['text_dim'])
        surface.blit(nn_title, (self.x + PANEL_PADDING, y_offset))
        y_offset += 25
        
        nn_rect = pygame.Rect(self.x + 10, y_offset, self.width - 20, 150)
        pygame.draw.rect(surface, COLORS['graph_bg'], nn_rect, border_radius=8)
        
        self._draw_neural_network(surface, nn_rect, best_genome, best_net)
        y_offset += 165
        
        # === 세대별 점수 그래프 ===
        graph_title = self.font_small.render("📈 세대별 점수", True, COLORS['text_dim'])
        surface.blit(graph_title, (self.x + PANEL_PADDING, y_offset))
        y_offset += 25
        
        graph_rect = pygame.Rect(self.x + 10, y_offset, self.width - 20, 150)
        pygame.draw.rect(surface, COLORS['graph_bg'], graph_rect, border_radius=8)
        
        self._draw_graph(surface, graph_rect)
        y_offset += 165
        
        # === 범례 ===
        legend_title = self.font_small.render("🎨 색상 설명", True, COLORS['text_dim'])
        surface.blit(legend_title, (self.x + PANEL_PADDING, y_offset))
        y_offset += 25
        
        legends = [
            (COLORS['car_best'], "금색", "1위 차량 (센서 표시)"),
            (COLORS['car_alive'], "파란색", "생존 차량"),
            (COLORS['car_dead'], "회색", "탈락 차량"),
        ]
        
        for color, name, desc in legends:
            pygame.draw.circle(surface, color, (self.x + 25, y_offset + 8), 8)
            text = self.font_small.render(f"{name} = {desc}", True, COLORS['text'])
            surface.blit(text, (self.x + 45, y_offset))
            y_offset += 25
    
    def _draw_neural_network(self, surface: pygame.Surface, rect: pygame.Rect,
                             genome: Optional[Any], net: Optional[Any]):
        """신경망 구조 시각화"""
        if genome is None:
            no_data = self.font_small.render("데이터 없음", True, COLORS['text_dim'])
            surface.blit(no_data, (rect.centerx - no_data.get_width()//2, 
                                   rect.centery - no_data.get_height()//2))
            return
        
        # 입력/출력 노드 위치 계산
        padding = 30
        layer_x = [rect.x + padding, rect.x + rect.width//2, rect.x + rect.width - padding]
        
        # 입력 노드 (5개)
        input_nodes = []
        input_labels = ["전방", "좌45°", "우45°", "좌90°", "우90°"]
        for i in range(5):
            y = rect.y + padding + i * 22
            input_nodes.append((layer_x[0], y))
        
        # 출력 노드 (2개)
        output_nodes = []
        output_labels = ["조향", "가속"]
        for i in range(2):
            y = rect.y + rect.height//2 - 15 + i * 30
            output_nodes.append((layer_x[2], y))
        
        # 연결선 그리기 (간단한 버전 - 모든 입력에서 출력으로)
        for inp in input_nodes:
            for out in output_nodes:
                pygame.draw.line(surface, COLORS['connection_positive'], inp, out, 1)
        
        # 입력 노드 그리기
        for i, (x, y) in enumerate(input_nodes):
            pygame.draw.circle(surface, COLORS['neuron_input'], (int(x), int(y)), 10)
            label = self.font_small.render(input_labels[i], True, COLORS['text_dim'])
            surface.blit(label, (x + 15, y - 8))
        
        # 출력 노드 그리기
        for i, (x, y) in enumerate(output_nodes):
            pygame.draw.circle(surface, COLORS['neuron_output'], (int(x), int(y)), 10)
            label = self.font_small.render(output_labels[i], True, COLORS['text_dim'])
            surface.blit(label, (x - 45, y - 8))
    
    def _draw_graph(self, surface: pygame.Surface, rect: pygame.Rect):
        """점수 그래프 그리기"""
        if len(self.best_scores) < 2:
            no_data = self.font_small.render("데이터 수집 중...", True, COLORS['text_dim'])
            surface.blit(no_data, (rect.centerx - no_data.get_width()//2, 
                                   rect.centery - no_data.get_height()//2))
            return
        
        padding = 20
        graph_width = rect.width - padding * 2
        graph_height = rect.height - padding * 2
        
        max_score = max(max(self.best_scores), max(self.avg_scores)) if self.best_scores else 1
        min_score = 0
        score_range = max(max_score - min_score, 1)
        
        # 그리드
        for i in range(5):
            y = rect.y + padding + (graph_height * i // 4)
            pygame.draw.line(surface, COLORS['graph_grid'], 
                           (rect.x + padding, y), (rect.x + rect.width - padding, y), 1)
        
        # 최고 점수 라인
        if len(self.best_scores) >= 2:
            points = []
            for i, score in enumerate(self.best_scores):
                x = rect.x + padding + (i / max(len(self.best_scores) - 1, 1)) * graph_width
                y = rect.y + padding + graph_height - ((score - min_score) / score_range) * graph_height
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, COLORS['graph_line_best'], False, points, 2)
        
        # 평균 점수 라인
        if len(self.avg_scores) >= 2:
            points = []
            for i, score in enumerate(self.avg_scores):
                x = rect.x + padding + (i / max(len(self.avg_scores) - 1, 1)) * graph_width
                y = rect.y + padding + graph_height - ((score - min_score) / score_range) * graph_height
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, COLORS['graph_line_avg'], False, points, 2)
        
        # 범례
        pygame.draw.line(surface, COLORS['graph_line_best'], 
                        (rect.x + padding, rect.y + 10), (rect.x + padding + 20, rect.y + 10), 2)
        best_label = self.font_small.render("최고", True, COLORS['text_dim'])
        surface.blit(best_label, (rect.x + padding + 25, rect.y + 4))
        
        pygame.draw.line(surface, COLORS['graph_line_avg'], 
                        (rect.x + padding + 70, rect.y + 10), (rect.x + padding + 90, rect.y + 10), 2)
        avg_label = self.font_small.render("평균", True, COLORS['text_dim'])
        surface.blit(avg_label, (rect.x + padding + 95, rect.y + 4))
