"""
메인 실행 파일
- 게임 루프
- 학습 진행
- 이벤트 처리
"""
import pygame
import sys
import matplotlib.pyplot as plt
from typing import Optional

from config import (
    COLORS, CELL_SIZE, PANEL_WIDTH, WINDOW_PADDING,
    SPEED_1X, MAX_EPISODES, MAX_STEPS_PER_EPISODE
)
from environment import MazeEnvironment
from agent import QLearningAgent
from visualizer import MazeVisualizer
from ui_panel import UIPanel
from mazes import DEFAULT_MAZE


class MazeLearningApp:
    def __init__(self):
        pygame.init()
        
        # 환경 초기화
        self.env = MazeEnvironment(DEFAULT_MAZE)
        self.agent = QLearningAgent(self.env.rows, self.env.cols)
        
        # 화면 크기 계산
        maze_width = self.env.cols * CELL_SIZE
        maze_height = self.env.rows * CELL_SIZE
        
        self.screen_width = maze_width + PANEL_WIDTH + WINDOW_PADDING * 3
        self.screen_height = maze_height + WINDOW_PADDING * 2
        
        # Pygame 설정
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Q-Learning Maze AI Visualization')
        self.clock = pygame.time.Clock()
        
        # 시각화 컴포넌트
        self.visualizer = MazeVisualizer(
            self.env.rows, self.env.cols,
            offset_x=WINDOW_PADDING,
            offset_y=WINDOW_PADDING
        )
        
        panel_x = maze_width + WINDOW_PADDING * 2
        panel_height = maze_height
        self.ui_panel = UIPanel(panel_x, WINDOW_PADDING, PANEL_WIDTH, panel_height)
        
        # 콜백 설정
        self.ui_panel.on_speed_change = self._on_speed_change
        self.ui_panel.on_pause = self._on_pause
        self.ui_panel.on_reset = self._on_reset
        
        # 상태 변수
        self.running = True
        self.paused = False
        self.learning_done = False
        self.step_delay = SPEED_1X
        self.last_step_time = 0
        
        # 현재 에피소드 상태
        self.current_episode = 0
        self.current_step = 0
        self.episode_reward = 0
        self.state = self.env.reset()
        
    def _on_speed_change(self, speed: int):
        """속도 변경 콜백"""
        self.step_delay = speed
    
    def _on_pause(self, paused: bool):
        """일시정지 콜백"""
        self.paused = paused
    
    def _on_reset(self):
        """초기화 콜백"""
        self.agent.reset_learning()
        self.env.reset()
        self.visualizer.clear_trail()
        self.current_episode = 0
        self.current_step = 0
        self.episode_reward = 0
        self.state = self.env.reset()
        self.learning_done = False
        self.paused = False
        self.ui_panel.paused = False
        self.ui_panel.pause_button.text = 'PAUSE'
    
    def _handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ui_panel._toggle_pause()
                elif event.key == pygame.K_r:
                    self._on_reset()
                elif event.key == pygame.K_1:
                    self.ui_panel._set_speed(SPEED_1X)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            self.ui_panel.handle_event(event)
    
    def _do_learning_step(self):
        """학습 스텝 수행"""
        if self.paused or self.learning_done:
            return
        
        # 현재 시간 체크 (딜레이)
        current_time = pygame.time.get_ticks()
        if self.step_delay > 0 and current_time - self.last_step_time < self.step_delay:
            return
        self.last_step_time = current_time
        
        # 행동 선택
        valid_actions = self.env.get_valid_actions(self.state)
        action = self.agent.choose_action(self.state, valid_actions)
        
        # 환경에서 행동 수행
        next_state, reward, done = self.env.step(action)
        
        # Q값 업데이트
        self.agent.update(self.state, action, reward, next_state, done)
        
        # 경로 잔상 추가
        self.visualizer.add_trail(self.state)
        
        # 상태 업데이트
        self.state = next_state
        self.current_step += 1
        self.episode_reward += reward
        
        # 에피소드 종료 체크
        if done:
            success = (self.env.agent_pos == self.env.goal_pos)
            self.agent.end_episode(self.current_step, self.episode_reward, success)
            self.ui_panel.update_graph(self.agent.episode_steps)
            
            # 다음 에피소드 준비
            self.current_episode += 1
            self.current_step = 0
            self.episode_reward = 0
            self.state = self.env.reset()
            self.visualizer.clear_trail()
            
            # 학습 완료 체크
            if self.current_episode >= MAX_EPISODES:
                self.learning_done = True
                self.paused = True
                self._show_final_graph()
    
    def _get_avg_steps(self) -> float:
        """최근 평균 스텝 수"""
        if len(self.agent.episode_steps) == 0:
            return 0
        recent = self.agent.episode_steps[-50:]  # 최근 50개
        return sum(recent) / len(recent)
    
    def _render(self):
        """화면 렌더링"""
        # 배경
        self.screen.fill(COLORS['background'])
        
        # 미로 시각화
        self.visualizer.render(
            self.screen,
            self.env.maze,
            self.env.agent_pos,
            self.agent.q_table,
            is_exploring=self.agent.last_action_was_exploration,
            show_arrows=True,
            show_heatmap=True
        )
        
        # UI 패널
        self.ui_panel.draw(
            self.screen,
            episode=self.current_episode,
            step=self.current_step,
            epsilon=self.agent.epsilon,
            success_rate=self.agent.get_success_rate(),
            avg_steps=self._get_avg_steps()
        )
        
        # 학습 완료 표시
        if self.learning_done:
            font = pygame.font.SysFont('Arial', 36, bold=True)
            text = font.render('Learning Complete!', True, (50, 255, 50))
            text_rect = text.get_rect(center=(self.screen_width // 2, 30))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def _show_final_graph(self):
        """학습 완료 후 matplotlib 그래프 표시"""
        if not self.agent.episode_steps:
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # 스텝 수 그래프
        ax1 = axes[0]
        episodes = range(1, len(self.agent.episode_steps) + 1)
        ax1.plot(episodes, self.agent.episode_steps, alpha=0.3, color='blue', label='Steps')
        
        # 이동 평균
        window = 20
        if len(self.agent.episode_steps) >= window:
            smoothed = []
            for i in range(len(self.agent.episode_steps)):
                start = max(0, i - window + 1)
                smoothed.append(sum(self.agent.episode_steps[start:i+1]) / (i - start + 1))
            ax1.plot(episodes, smoothed, color='red', linewidth=2, label=f'Moving Avg ({window})')
        
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Steps')
        ax1.set_title('Steps per Episode (Learning Progress)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 누적 보상 그래프
        ax2 = axes[1]
        ax2.plot(episodes, self.agent.episode_rewards, alpha=0.5, color='green')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Total Reward')
        ax2.set_title('Total Reward per Episode')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show(block=False)
    
    def run(self):
        """메인 루프"""
        while self.running:
            self._handle_events()
            self._do_learning_step()
            self._render()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()


def main():
    app = MazeLearningApp()
    app.run()


if __name__ == '__main__':
    main()
