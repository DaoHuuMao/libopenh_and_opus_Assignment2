import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 1080, 1900

# Tạo surface để render (không mở cửa sổ)
screen = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

# Tạo thư mục lưu ảnh
os.makedirs("frames", exist_ok=True)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (0, 100, 100)
CYAN = (75, 0, 75)

# Clock (dùng để giới hạn tốc độ cập nhật trong vòng lặp)
clock = pygame.time.Clock()

# Fonts
codec_font = pygame.font.SysFont(None, 28)

students = [
    "Dao Huu Mao - 20233865",
    "Vu Minh Hien - 20224311",
    "Vu Xuan Anh - 20233832",
    "Le Hoang Anh - 20224297",
    "Pham Thi Thanh Truc - 20224293"
]

animated_codecs = ["libopenh264", "Opus"]

class GraphicObject:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.choice([-3, 3])
        self.vy = random.choice([-3, 3])

    def draw(self, surface):
        pass

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.x - self.width // 2 < 0 or self.x + self.width // 2 > screen_width:
            self.vx = -self.vx
        if self.y - self.height // 2 < 0 or self.y + self.height // 2 > screen_height:
            self.vy = -self.vy

class StudentBlock(GraphicObject):
    def __init__(self, x, y, width, height, color, student_name):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.student_name = student_name

    def draw(self, surface):
        text_surface = codec_font.render(self.student_name, True, self.color)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        surface.blit(text_surface, text_rect)

    def update(self):
        super().update()
        self.x = max(self.width // 2, min(self.x, screen_width - self.width // 2))
        self.y = max(self.height // 2, min(self.y, screen_height - self.height // 2))

class CodecBlock(GraphicObject):
    def __init__(self, x, y, width, height, color, codec_name):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.codec_name = codec_name

    def draw(self, surface):
        block_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(block_surface, self.color, (0, 0, self.width, self.height))
        text_surface = codec_font.render(self.codec_name, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        block_surface.blit(text_surface, text_rect)
        surface.blit(block_surface, (self.x - self.width // 2, self.y - self.height // 2))

    def update(self):
        super().update()
        self.x = max(self.width // 2, min(self.x, screen_width - self.width // 2))
        self.y = max(self.height // 2, min(self.y, screen_height - self.height // 2))

# Tạo đối tượng
colors = [RED, GREEN, BLUE, YELLOW, PURPLE]
objects = [
    StudentBlock(
        random.randint(100, screen_width - 100),
        random.randint(100, screen_height - 100),
        160, 60, colors[i], student
    ) for i, student in enumerate(students)
]

codec_colors = [CYAN, PURPLE]
objects.extend([
    CodecBlock(
        random.randint(100, screen_width - 100),
        random.randint(100, screen_height - 100),
        150, 40, codec_colors[i], codec
    ) for i, codec in enumerate(animated_codecs)
])

# Render và lưu ảnh frame
for i in range(1800):  # 30 giây ở 60fps - 60s 30fps
    screen.fill((0, 0, 0, 0))  # Xóa nền trong suốt (RGBA)
    for obj in objects:
        obj.update()
        obj.draw(screen)

    pygame.image.save(screen, f"frames/frame_{i:04d}.png")
    clock.tick(60)

pygame.quit()
