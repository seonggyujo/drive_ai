"""
Q-Learning 에이전트
- Q-table 관리
- ε-greedy 정책
- 학습 업데이트
"""
import numpy as np
import random
from typing import Tuple, List

from config import (
    Action,
    LEARNING_RATE, DISCOUNT_FACTOR,
    EPSILON_START, EPSILON_END, EPSILON_DECAY
)


class QLearningAgent:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.n_actions = len(Action)
        
        # Q-table 초기화: [row][col][action]
        self.q_table = np.zeros((rows, cols, self.n_actions))
        
        # 하이퍼파라미터
        self.lr = LEARNING_RATE
        self.gamma = DISCOUNT_FACTOR
        self.epsilon = EPSILON_START
        self.epsilon_min = EPSILON_END
        self.epsilon_decay = EPSILON_DECAY
        
        # 마지막 행동이 탐험이었는지 기록
        self.last_action_was_exploration = False
        
        # 학습 통계
        self.episode_steps = []  # 에피소드별 스텝 수
        self.episode_rewards = []  # 에피소드별 총 보상
        self.success_count = 0
        self.episode_count = 0
        
    def choose_action(self, state: Tuple[int, int], valid_actions: List[Action] = None) -> Action:
        """
        ε-greedy 정책으로 행동 선택
        Returns: 선택된 행동
        """
        row, col = state
        
        # 탐험 (랜덤)
        if random.random() < self.epsilon:
            self.last_action_was_exploration = True
            if valid_actions:
                return random.choice(valid_actions)
            return Action(random.randint(0, self.n_actions - 1))
        
        # 활용 (Q값 최대 행동)
        self.last_action_was_exploration = False
        q_values = self.q_table[row, col]
        
        if valid_actions:
            # 유효한 행동 중에서 최대 Q값 선택
            valid_q = [(a, q_values[a]) for a in valid_actions]
            max_q = max(valid_q, key=lambda x: x[1])[1]
            best_actions = [a for a, q in valid_q if q == max_q]
            return random.choice(best_actions)
        
        # 모든 행동 중 최대 Q값 선택
        max_q = np.max(q_values)
        best_actions = [Action(a) for a in range(self.n_actions) if q_values[a] == max_q]
        return random.choice(best_actions)
    
    def update(self, state: Tuple[int, int], action: Action, 
               reward: float, next_state: Tuple[int, int], done: bool):
        """
        Q-value 업데이트
        Q(s,a) ← Q(s,a) + α * (reward + γ * max(Q(s')) - Q(s,a))
        """
        row, col = state
        next_row, next_col = next_state
        
        current_q = self.q_table[row, col, action]
        
        if done:
            target = reward
        else:
            max_next_q = np.max(self.q_table[next_row, next_col])
            target = reward + self.gamma * max_next_q
        
        # Q값 업데이트
        self.q_table[row, col, action] += self.lr * (target - current_q)
    
    def decay_epsilon(self):
        """ε 감쇠"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def end_episode(self, steps: int, total_reward: float, success: bool):
        """에피소드 종료 처리"""
        self.episode_count += 1
        self.episode_steps.append(steps)
        self.episode_rewards.append(total_reward)
        if success:
            self.success_count += 1
        self.decay_epsilon()
    
    def get_success_rate(self) -> float:
        """성공률 반환"""
        if self.episode_count == 0:
            return 0.0
        return self.success_count / self.episode_count
    
    def get_best_action(self, state: Tuple[int, int]) -> Action:
        """최적 행동 반환 (greedy)"""
        row, col = state
        return Action(np.argmax(self.q_table[row, col]))
    
    def get_max_q_value(self, row: int, col: int) -> float:
        """특정 셀의 최대 Q값 반환"""
        return np.max(self.q_table[row, col])
    
    def get_q_values(self, row: int, col: int) -> np.ndarray:
        """특정 셀의 모든 Q값 반환"""
        return self.q_table[row, col].copy()
    
    def reset_learning(self):
        """학습 초기화"""
        self.q_table = np.zeros((self.rows, self.cols, self.n_actions))
        self.epsilon = EPSILON_START
        self.episode_steps = []
        self.episode_rewards = []
        self.success_count = 0
        self.episode_count = 0
