import pygame
import numpy as np

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
HIGHLIGHT = (255, 255, 0)

# 물리 변수
GRAVITY = 0.5
BOUNCE = 0.7  # 탄성 계수
FRICTION = 0.9  # 마찰력

# 원형 객체 클래스
class Circle:
    def __init__(self, x, y, radius, color=BLUE):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = 0
        self.vy = 0
        self.held = False  # 잡혀 있는 상태인지 확인

    def render(self, surface):
        """원을 화면에 그리기"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        if self.held:
            pygame.draw.circle(surface, HIGHLIGHT, (int(self.x), int(self.y)), self.radius + 3, 2)

    def update(self):
        """중력 및 물리적 업데이트"""
        if not self.held:
            self.vy += GRAVITY  # 중력 추가
            self.x += self.vx
            self.y += self.vy

        # 화면 경계와의 충돌
        if self.x - self.radius <= 0:  # 왼쪽 벽
            self.x = self.radius
            self.vx = -self.vx * BOUNCE
        elif self.x + self.radius >= WIDTH:  # 오른쪽 벽
            self.x = WIDTH - self.radius
            self.vx = -self.vx * BOUNCE

        if self.y - self.radius <= 0:  # 천장
            self.y = self.radius
            self.vy = -self.vy * BOUNCE
        elif self.y + self.radius >= HEIGHT:  # 바닥
            self.y = HEIGHT - self.radius
            self.vy = -self.vy * BOUNCE
            self.vx *= FRICTION  # 바닥에서의 마찰

    def check_collision(self, other):
        """다른 원과의 충돌 처리"""
        dx = self.x - other.x
        dy = self.y - other.y
        distance = np.hypot(dx, dy)

        if distance < self.radius + other.radius:  # 충돌이 발생했을 경우
            if distance == 0:  # 같은 위치 방지
                nx, ny = 1, 0
            else:
                nx, ny = dx / distance, dy / distance

            # 겹침 해결
            overlap = self.radius + other.radius - distance
            self.x += nx * overlap / 2
            self.y += ny * overlap / 2
            other.x -= nx * overlap / 2
            other.y -= ny * overlap / 2

            # 속도 분해 및 교환
            tx, ty = -ny, nx
            self_normal = self.vx * nx + self.vy * ny
            self_tangent = self.vx * tx + self.vy * ty
            other_normal = other.vx * nx + other.vy * ny
            other_tangent = other.vx * tx + other.vy * ty

            # 속도 교환 (탄성 충돌)
            self_normal, other_normal = other_normal, self_normal

            # 속도 재구성
            self.vx = self_normal * nx + self_tangent * tx
            self.vy = self_normal * ny + self_tangent * ty
            other.vx = other_normal * nx + other_tangent * tx
            other.vy = other_normal * ny + other_tangent * ty

            # 작은 속도 제거 (떨림 방지)
            if abs(self.vx) < 0.1:
                self.vx = 0
            if abs(self.vy) < 0.1:
                self.vy = 0
            if abs(other.vx) < 0.1:
                other.vx = 0
            if abs(other.vy) < 0.1:
                other.vy = 0

# 메인 루프
def main():
    running = True
    circles = []  # 생성된 원 리스트
    held_circle = None  # 현재 잡고 있는 원

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:  # 좌클릭
                    for circle in circles:
                        if (circle.x - mx)**2 + (circle.y - my)**2 <= circle.radius**2:
                            held_circle = circle
                            circle.held = True
                            break
                    if not held_circle:
                        circles.append(Circle(mx, my, radius=20))

                elif event.button == 3:  # 우클릭
                    if circles:
                        closest_circle = min(circles, key=lambda c: (c.x - mx)**2 + (c.y - my)**2)
                        circles.remove(closest_circle)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and held_circle:
                    held_circle.held = False
                    held_circle.vx = 0
                    held_circle.vy = 0
                    held_circle = None

            elif event.type == pygame.MOUSEMOTION and held_circle:
                mx, my = pygame.mouse.get_pos()
                held_circle.x, held_circle.y = mx, my

        # 물리 업데이트 및 렌더링
        for circle in circles:
            circle.update()
            circle.render(screen)
            for other in circles:
                if circle is not other:
                    circle.check_collision(other)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
