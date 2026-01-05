"""
미로 환경 클래스
- 상태 관리
- 행동 처리
- 보상 계산
"""
from typing import Tuple, List
import copy

from config import (
    Action, CellType,
    REWARD_GOAL, REWARD_WALL, REWARD_STEP,
    MAX_STEPS_PER_EPISODE
)
from mazes import DEFAULT_MAZE


class MazeEnvironment:
    def __init__(self, maze: List[List[int]] = None):
        self.original_maze = maze if maze else DEFAULT_MAZE
        self.maze = copy.deepcopy(self.original_maze)
        self.rows = len(self.maze)
        self.cols = len(self.maze[0])
        
        self.start_pos = self._find_cell(CellType.START)
        self.goal_pos = self._find_cell(CellType.GOAL)
        
        self.agent_pos = self.start_pos
        self.steps = 0
        self.done = False
        
    def _find_cell(self, cell_type: CellType) -> Tuple[int, int]:
        """특정 타입의 셀 위치 찾기 (row, col)"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == cell_type:
                    return (row, col)
        return (0, 0)
    
    def reset(self) -> Tuple[int, int]:
        """환경 초기화, 시작 위치 반환"""
        self.agent_pos = self.start_pos
        self.steps = 0
        self.done = False
        return self.agent_pos
    
    def get_state(self) -> Tuple[int, int]:
        """현재 상태 (에이전트 위치) 반환"""
        return self.agent_pos
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """유효한 위치인지 확인 (범위 내 + 벽 아님)"""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self.maze[row][col] != CellType.WALL
    
    def step(self, action: Action) -> Tuple[Tuple[int, int], float, bool]:
        """
        행동 수행
        Returns: (new_state, reward, done)
        """
        if self.done:
            return self.agent_pos, 0, True
        
        row, col = self.agent_pos
        
        # 행동에 따른 새 위치 계산
        if action == Action.UP:
            new_row, new_col = row - 1, col
        elif action == Action.DOWN:
            new_row, new_col = row + 1, col
        elif action == Action.LEFT:
            new_row, new_col = row, col - 1
        elif action == Action.RIGHT:
            new_row, new_col = row, col + 1
        else:
            new_row, new_col = row, col
        
        self.steps += 1
        
        # 벽 충돌 체크
        if not self.is_valid_position(new_row, new_col):
            reward = REWARD_WALL
            # 위치는 그대로
        else:
            self.agent_pos = (new_row, new_col)
            
            # 목표 도달 체크
            if self.agent_pos == self.goal_pos:
                reward = REWARD_GOAL
                self.done = True
            else:
                reward = REWARD_STEP
        
        # 최대 스텝 초과
        if self.steps >= MAX_STEPS_PER_EPISODE:
            self.done = True
        
        return self.agent_pos, reward, self.done
    
    def get_valid_actions(self, pos: Tuple[int, int] = None) -> List[Action]:
        """현재 위치에서 가능한 행동 목록"""
        if pos is None:
            pos = self.agent_pos
        
        row, col = pos
        valid = []
        
        if self.is_valid_position(row - 1, col):
            valid.append(Action.UP)
        if self.is_valid_position(row + 1, col):
            valid.append(Action.DOWN)
        if self.is_valid_position(row, col - 1):
            valid.append(Action.LEFT)
        if self.is_valid_position(row, col + 1):
            valid.append(Action.RIGHT)
        
        return valid
    
    def get_cell_type(self, row: int, col: int) -> CellType:
        """셀 타입 반환"""
        return CellType(self.maze[row][col])
