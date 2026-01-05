"""
자율주행 AI 시각화 - 메인 프로그램
NEAT 알고리즘을 사용한 신경망 진화
"""
import pygame
import neat
import os
import sys
import time
from typing import List, Tuple, Optional

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    CAR_COUNT, GENERATION_TIME, SPEED_OPTIONS,
    COLORS, NEAT_CONFIG_PATH, PANEL_X
)
from track import Track
from car import Car
from visualizer import Visualizer
from ui_panel import UIPanel


class SelfDrivingSimulation:
    """자율주행 AI 시뮬레이션 클래스"""
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Self-Driving AI")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # 모듈 초기화
        self.track = Track()
        self.visualizer = Visualizer(self.screen)
        self.ui_panel = UIPanel()
        
        # 상태 변수
        self.generation = 0
        self.running = True
        self.paused = False
        
        # 배속 설정
        self.speed_multiplier = 1
        
        # 현재 세대의 차량들과 신경망
        self.cars: List[Car] = []
        self.nets: List[neat.nn.FeedForwardNetwork] = []
        self.genomes: List[neat.DefaultGenome] = []
        
        # 최고 차량 추적
        self.best_car_id: Optional[int] = None
        self.best_genome: Optional[neat.DefaultGenome] = None
        self.best_net: Optional[neat.nn.FeedForwardNetwork] = None
    
    def eval_genomes(self, genomes: List[Tuple[int, neat.DefaultGenome]], config: neat.Config):
        """
        NEAT의 적합도 평가 함수
        한 세대의 모든 유전체(신경망)를 평가
        """
        self.generation += 1
        
        # 차량과 신경망 초기화
        self.cars = []
        self.nets = []
        self.genomes = []
        
        # 시작 위치 가져오기
        start_positions = self.track.get_start_positions(len(genomes))
        
        for i, (genome_id, genome) in enumerate(genomes):
            # 신경망 생성
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            self.genomes.append(genome)
            
            # 차량 생성
            x, y, angle = start_positions[i]
            car = Car(x, y, angle, car_id=i)
            self.cars.append(car)
            
            # 적합도 초기화
            genome.fitness = 0
        
        # 세대 시뮬레이션 실행
        self._run_generation()
        
        # 적합도 기록
        best_fitness = 0
        total_fitness = 0
        
        for i, genome in enumerate(self.genomes):
            genome.fitness = self.cars[i].fitness
            total_fitness += genome.fitness
            if genome.fitness > best_fitness:
                best_fitness = genome.fitness
        
        avg_fitness = total_fitness / len(self.genomes) if self.genomes else 0
        
        # 그래프 데이터 업데이트
        self.ui_panel.update_scores(best_fitness, avg_fitness)
    
    def _run_generation(self):
        """한 세대 시뮬레이션 실행"""
        start_time = time.time()
        time_left = GENERATION_TIME
        
        while True:
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 배속 버튼 클릭 처리
                    self.ui_panel.handle_click(event.pos, self)
            
            # 일시정지 중이면 렌더링만
            if self.paused:
                self._render(time_left)
                self.clock.tick(FPS)
                continue
            
            # 경과 시간
            elapsed_time = time.time() - start_time
            time_left = max(0, GENERATION_TIME - elapsed_time)
            
            # 시간 초과 또는 모든 차량 사망 시 세대 종료
            alive_count = sum(1 for car in self.cars if car.alive)
            if elapsed_time >= GENERATION_TIME or alive_count == 0:
                break
            
            # 배속만큼 시뮬레이션 업데이트 (프레임 스킵)
            for _ in range(self.speed_multiplier):
                # 차량 업데이트
                self._update_cars()
                
                # 최고 차량 찾기
                self._find_best_car()
                
                # 모든 차량 사망 체크
                alive_count = sum(1 for car in self.cars if car.alive)
                if alive_count == 0:
                    break
            
            # 렌더링은 1번만 (프레임 스킵)
            self._render(time_left)
            
            # FPS 제한
            self.clock.tick(FPS)
    
    def _update_cars(self):
        """모든 차량 상태 업데이트"""
        for i, car in enumerate(self.cars):
            if not car.alive:
                continue
            
            # 센서 업데이트
            car.update_sensors(self.track)
            
            # 신경망 입력
            inputs = car.get_inputs()
            
            # 신경망 출력 (조향, 가속)
            outputs = self.nets[i].activate(inputs)
            
            # 차량에 출력 적용
            car.set_outputs(outputs)
            
            # 차량 물리 업데이트
            car.update(self.track)
    
    def _find_best_car(self):
        """현재 가장 높은 적합도의 차량 찾기"""
        best_fitness = -1
        self.best_car_id = None
        
        for i, car in enumerate(self.cars):
            if car.alive and car.fitness > best_fitness:
                best_fitness = car.fitness
                self.best_car_id = car.car_id
                self.best_genome = self.genomes[i]
                self.best_net = self.nets[i]
    
    def _render(self, time_left: float = 0):
        """화면 렌더링"""
        # 트랙 영역 렌더링
        self.visualizer.render(
            self.track,
            self.cars,
            self.generation,
            time_left,
            self.best_car_id
        )
        
        # UI 패널 렌더링
        alive_count = sum(1 for car in self.cars if car.alive)
        best_fitness = max((car.fitness for car in self.cars), default=0)
        
        self.ui_panel.draw(
            self.screen,
            self.generation,
            alive_count,
            len(self.cars),
            time_left,
            best_fitness,
            self.speed_multiplier,
            self.best_genome,
            self.best_net
        )
        
        # 일시정지 표시
        if self.paused:
            self._draw_pause_overlay()
        
        # 화면 업데이트
        pygame.display.flip()
    
    def _draw_pause_overlay(self):
        """일시정지 오버레이 - iOS 스타일"""
        # 반투명 오버레이
        overlay = pygame.Surface((PANEL_X, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 일시정지 텍스트
        font = pygame.font.SysFont('malgungothic', 42, bold=True)
        text = font.render("일시정지", True, COLORS['text_primary'])
        text_rect = text.get_rect(center=(PANEL_X // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(text, text_rect)
        
        # 힌트 텍스트
        font_small = pygame.font.SysFont('malgungothic', 18)
        hint = font_small.render("Space 를 눌러 계속", True, COLORS['text_secondary'])
        hint_rect = hint.get_rect(center=(PANEL_X // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(hint, hint_rect)
    
    def run(self):
        """메인 실행"""
        # NEAT 설정 로드
        config_path = os.path.join(os.path.dirname(__file__), NEAT_CONFIG_PATH)
        
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )
        
        # NEAT 집단 생성
        population = neat.Population(config)
        
        # 통계 리포터 추가 (콘솔 출력)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        
        # 진화 실행 (무한 세대)
        try:
            winner = population.run(self.eval_genomes, n=1000)
            print(f"\n최고 유전체:\n{winner}")
        except KeyboardInterrupt:
            print("\n학습이 중단되었습니다.")
        except SystemExit:
            pass
        finally:
            pygame.quit()


def main():
    """메인 함수"""
    print("=" * 50)
    print("  Self-Driving AI Visualization")
    print("=" * 50)
    print("\n조작법:")
    print("  - ESC: 종료")
    print("  - Space: 일시정지/재개")
    print("  - 마우스: 배속 버튼 클릭 (x1, x5, x10)")
    print("\n학습을 시작합니다...\n")
    
    simulation = SelfDrivingSimulation()
    simulation.run()


if __name__ == "__main__":
    main()
