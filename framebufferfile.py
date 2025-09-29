import pygame

SCALE = 2

class FB:
    def __init__(self):
        self.buffer = [0] * (160 * 144)
        self.colors = [
            (255, 255, 255), # 0
            (192, 192, 192), # 1
            (96, 96, 96), # 2
            (0, 0, 0) # 3
        ]

    def writePixel(self, x, y, color_id):
        if 0 <= x < 160 and 0 <= y < 144:
            self.buffer[y * 160 + x] = color_id

    def drawFB(self, screen):
        surface = pygame.Surface((160, 144))
        for y in range(144):
            for x in range(160):
                color_id = self.buffer[y * 160 + x]
                color = self.colors[color_id]
                surface.set_at((x, y), color)

        scaled = pygame.transform.scale(surface, (160 * SCALE, 144 * SCALE))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
