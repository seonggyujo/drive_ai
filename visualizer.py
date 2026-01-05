"""
시각화 모듈
- 미로 렌더링
- Q-value Heatmap
- 방향 화살표
- 에이전트 표시
"""
import pygame
import numpy as np
from typing import Tuple, List, Optional

from config import (
    Action, CellType, COLORS, CELL_SIZE
)


class MazeVisualizer:
    def __init__(self, rows: int, cols: int, offset_x: int = 0, offset_y: int = 0):
        self.rows = rows
        self.cols = cols
        self.cell_size = CELL_SIZE
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # 미로 영역 크기
        self.width = cols * self.cell_size
        self.height = rows * self.cell_size
        
        # 경로 잔상 저장
        self.trail: List[Tuple[int, int]] = []
        self.max_trail_length = 50
        
    def clear_trail(self):
        """경로 잔상 초기화"""
        self.trail = []
    
    def add_trail(self, pos: Tuple[int, int]):
        """경로 잔상 추가"""
        if pos not in self.trail:
            self.trail.append(pos)
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def _get_cell_rect(self, row: int, col: int) -> pygame.Rect:
        """셀의 화면 좌표 반환"""
        x = self.offset_x + col * self.cell_size
        y = self.offset_y + row * self.cell_size
        return pygame.Rect(x, y, self.cell_size, self.cell_size)
    
    def _get_heatmap_color(self, value: float, min_val: float, max_val: float) -> Tuple[int, int, int]:
        """Q값에 따른 Heatmap 색상 반환"""
        if max_val == min_val:
            t = 0
        else:
            t = (value - min_val) / (max_val - min_val)
        
        # 흰색 → 빨간색 그라데이션
        r = int(COLORS['heatmap_low'][0] + t * (COLORS['heatmap_high'][0] - COLORS['heatmap_low'][0]))
        g = int(COLORS['heatmap_low'][1] + t * (COLORS['heatmap_high'][1] - COLORS['heatmap_low'][1]))
        b = int(COLORS['heatmap_low'][2] + t * (COLORS['heatmap_high'][2] - COLORS['heatmap_low'][2]))
        
        return (r, g, b)
    
    def draw_maze(self, surface: pygame.Surface, maze: List[List[int]], 
                  q_table: Optional[np.ndarray] = None, show_heatmap: bool = True):
        """미로 그리기 (Heatmap 포함)"""
        
        # Q값 범위 계산 (Heatmap용)
        min_q, max_q = 0.0, 0.0
        if q_table is not None and show_heatmap:
            max_q_values = []
            for row in range(self.rows):
                for col in range(self.cols):
                    if maze[row][col] != CellType.WALL:
                        max_q_values.append(np.max(q_table[row, col]))
            
            if max_q_values:
                min_q = min(max_q_values)
                max_q = max(max_q_values)
        
        # 셀 그리기
        for row in range(self.rows):
            for col in range(self.cols):
                rect = self._get_cell_rect(row, col)
                cell_type = maze[row][col]
                
                if cell_type == CellType.WALL:
                    color = COLORS['wall']
                elif cell_type == CellType.START:
                    color = COLORS['start']
                elif cell_type == CellType.GOAL:
                    color = COLORS['goal']
                else:
                    # 일반 경로 - Heatmap 적용
                    if q_table is not None and show_heatmap and max_q > min_q:
                        max_q_val = np.max(q_table[row, col])
                        color = self._get_heatmap_color(max_q_val, min_q, max_q)
                    else:
                        color = COLORS['path']
                
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, COLORS['wall'], rect, 1)  # 테두리
    
    def draw_trail(self, surface: pygame.Surface):
        """경로 잔상 그리기"""
        for i, pos in enumerate(self.trail):
            row, col = pos
            rect = self._get_cell_rect(row, col)
            
            # 오래된 잔상일수록 투명하게
            alpha = int(100 * (i + 1) / len(self.trail)) if self.trail else 0
            trail_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            trail_color = (*COLORS['trail'], alpha)
            pygame.draw.rect(trail_surface, trail_color, (0, 0, self.cell_size, self.cell_size))
            surface.blit(trail_surface, rect.topleft)
    
    def draw_arrows(self, surface: pygame.Surface, maze: List[List[int]], q_table: np.ndarray):
        """각 셀에 최적 행동 방향 화살표 그리기"""
        arrow_size = self.cell_size // 3
        
        for row in range(self.rows):
            for col in range(self.cols):
                if maze[row][col] == CellType.WALL or maze[row][col] == CellType.GOAL:
                    continue
                
                # 최대 Q값인 행동 찾기
                q_values = q_table[row, col]
                if np.max(q_values) == 0:  # 아직 학습되지 않은 셀
                    continue
                
                best_action = Action(np.argmax(q_values))
                
                # 셀 중심
                rect = self._get_cell_rect(row, col)
                cx, cy = rect.center
                
                # 화살표 방향 계산
                points = []
                if best_action == Action.UP:
                    points = [(cx, cy - arrow_size), (cx - arrow_size//2, cy + arrow_size//2), 
                              (cx + arrow_size//2, cy + arrow_size//2)]
                elif best_action == Action.DOWN:
                    points = [(cx, cy + arrow_size), (cx - arrow_size//2, cy - arrow_size//2), 
                              (cx + arrow_size//2, cy - arrow_size//2)]
                elif best_action == Action.LEFT:
                    points = [(cx - arrow_size, cy), (cx + arrow_size//2, cy - arrow_size//2), 
                              (cx + arrow_size//2, cy + arrow_size//2)]
                elif best_action == Action.RIGHT:
                    points = [(cx + arrow_size, cy), (cx - arrow_size//2, cy - arrow_size//2), 
                              (cx - arrow_size//2, cy + arrow_size//2)]
                
                if points:
                    pygame.draw.polygon(surface, COLORS['arrow'], points)
    
    def draw_agent(self, surface: pygame.Surface, pos: Tuple[int, int], is_exploring: bool = False):
        """에이전트 그리기"""
        row, col = pos
        rect = self._get_cell_rect(row, col)
        
        # 탐험/활용에 따른 색상
        color = COLORS['agent_explore'] if is_exploring else COLORS['agent_exploit']
        
        # 원으로 표시
        center = rect.center
        radius = self.cell_size // 3
        pygame.draw.circle(surface, color, center, radius)
        
        # 탐험 중이면 ? 표시
        if is_exploring:
            font = pygame.font.SysFont('Arial', self.cell_size // 3)
            text = font.render('?', True, (255, 255, 255))
            text_rect = text.get_rect(center=center)
            surface.blit(text, text_rect)
    
    def render(self, surface: pygame.Surface, maze: List[List[int]], 
               agent_pos: Tuple[int, int], q_table: Optional[np.ndarray] = None,
               is_exploring: bool = False, show_arrows: bool = True, show_heatmap: bool = True):
        """전체 렌더링"""
        # 1. 미로 + Heatmap
        self.draw_maze(surface, maze, q_table, show_heatmap)
        
        # 2. 경로 잔상
        self.draw_trail(surface)
        
        # 3. 방향 화살표
        if show_arrows and q_table is not None:
            self.draw_arrows(surface, maze, q_table)
        
        # 4. 에이전트
        self.draw_agent(surface, agent_pos, is_exploring)
