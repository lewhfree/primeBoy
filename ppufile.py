import pygame
import busfile
WIDTH, HEIGHT = 256, 256
SCALE = 2
class FB:
    def __init__(self):
        self.buffer = [0] * (256 * 256)
    def writePixel(self, x, y, color):
        self.buffer[x + y*256] = color

def drawFB(fb, screen, scx, scy):
    surface = pygame.Surface((WIDTH, HEIGHT))
    # Set pixels row by row
    for y in range(HEIGHT):
        for x in range(WIDTH):
            gray = fb.buffer[x + y * 256]
            color = (gray, gray, gray)  # expand grayscale → RGB
            surface.set_at((x, y), color)

    # Scale up for visibility
    scaled = pygame.transform.scale(surface, (WIDTH * SCALE, HEIGHT * SCALE))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

class PPU:
    def __init__(self, bus, fb):
        self.fb = fb
        self.dots = 0
        self.bgpallete = 0
        self.objpallete0 = 0
        self.objpallete1 = 0
        self.ctrl = 0
        self.stat = 0
        self.scx = 0
        self.scy = 0
        self.lyc = 0
        self.wy  = 0
        self.wx = 0
        self.ly = 0
    def step(clocks):
        if not (self.reg & 0b10000000):
            return
        mode = self.ctrl & 0b11
        

        
    def busWrite(val, addr):
        if addr == 0xFF40:
            self.ctrl = val
        elif addr == 0xFF41:
            self.stat = (val & 0b11111000) | (self.stat & 0b111)
        elif addr == 0xFF42:
            self.scx = val
        elif addr == 0xFF43:
            self.scy = val
        elif addr == 0xFF45: #44 is read only
            self.lyc = val
        #46 is a dma request
        elif addr == 0xFF47:
            self.bgpallete = val
        elif addr == 0xFF48:
            self.objpallete0 = val
        elif addr == 0xFF49:
            self.objpallete1 = val
        elif addr == 0xFF4A:
            self.wy = val
        elif addr == 0xFF4B:
            self.wx = val
    def busRead(addr):
        if addr == 0xFF40:
            return self.ctrl
        elif addr == 0xFF41:
            return self.stat
        elif addr == 0xFF42:
            return self.scx
        elif addr == 0xFF43:
            return self.scy
        elif addr == 0xFF44:
            return self.ly
        elif addr == 0xFF45:
            return self.lyc
        #46 is a dma request
        elif addr == 0xFF47:
            return self.bgpallete
        elif addr == 0xFF48:
            return self.objpallete0
        elif addr == 0xFF49:
            return self.objpallete1
        elif addr == 0xFF4A:
            return self.wy
        elif addr == 0xFF4B:
            return self.wx
