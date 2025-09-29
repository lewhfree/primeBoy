import pygame
# Make sure this import points to the file containing your PPU and FB classes
from ppufile import PPU
from framebufferfile import FB

# --- Configuration ---
SCALE = 2 # How much to scale the 160x144 screen

# --- Dummy Classes to Simulate the Rest of the Emulator ---

class TestBus:
    """A dummy Bus class for testing the PPU in isolation."""
    def __init__(self):
        self.vram = [0] * 8192  # 8KB of Video RAM
        self.oam = [0] * 160     # 160 bytes of Object Attribute Memory (for sprites)
        self.screen = None      # This will be set to the Pygame screen object

    def read(self, addr):
        if 0x8000 <= addr <= 0x9FFF:
            return self.vram[addr - 0x8000]
        if 0xFE00 <= addr <= 0xFE9F:
            return self.oam[addr - 0xFE00]
        return 0 # Default return for unhandled reads

    def write(self, addr, val):
        # The test harness doesn't need the PPU to write back to the bus,
        # so this can be left empty.
        pass

class TestIntCaller:
    """A dummy Interrupt Caller that just prints requests."""
    def callInt(self, vector):
        # In a real emulator, this would trigger a CPU interrupt.
        # For testing, we just print the vector that was called.
        print(f"--- Interrupt requested for vector: ${vector:02X} ---")

# --- Main Test Function ---

def main():
    """Initializes and runs the modified PPU test environment."""
    pygame.init()
    screen = pygame.display.set_mode((160 * SCALE, 144 * SCALE))
    pygame.display.set_caption("PPU Test Harness")

    # 1. Initialize the dummy components and the PPU
    bus = TestBus()
    bus.screen = screen
    fb = FB()
    int_caller = TestIntCaller()
    ppu = PPU(bus, fb, int_caller)

    ## --- Test Setup: Manually load data into memory ---

    # A. Load the smiley face tile into VRAM at address $8000 (Tile ID 0)
    smiley_tile = [
        0x3C, 0x3C, 0x42, 0x00, 0x99, 0x00, 0xA5, 0x00,
        0x81, 0x00, 0x42, 0x66, 0x3C, 0x00, 0x00, 0x00
    ]
    for i, byte in enumerate(smiley_tile):
        bus.vram[i] = byte

    # B. NEW: Load a solid black square tile into VRAM at address $8010 (Tile ID 1)
    #    0xFF for both bytes of a row makes every pixel the highest color ID (3), which is black.
    black_square_tile = [0xFF] * 16
    for i, byte in enumerate(black_square_tile):
        bus.vram[16 + i] = byte # Start at offset 16 to place it after the smiley tile

    # C. Fill the background tile map ($9800) with the smiley face (Tile ID 0).
    #    This remains the same to keep the background uniform.
    for i in range(1024):
        bus.vram[0x1800 + i] = 0

    # D. NEW: Write three black square sprites to OAM memory.
    #    Each sprite uses Tile ID 1, which is our new black square.
    # Sprite 1
    bus.oam[0] = 50 + 16   # Y Position
    bus.oam[1] = 40 + 8    # X Position
    bus.oam[2] = 1         # Tile ID (the black square)
    bus.oam[3] = 0         # Attributes

    # Sprite 2
    bus.oam[4] = 72 + 16   # Y Position
    bus.oam[5] = 80 + 8    # X Position
    bus.oam[6] = 1         # Tile ID
    bus.oam[7] = 0         # Attributes

    # Sprite 3
    bus.oam[8] = 94 + 16   # Y Position
    bus.oam[9] = 120 + 8   # X Position
    bus.oam[10] = 1        # Tile ID
    bus.oam[11] = 0        # Attributes
    
    # E. Set the PPU's registers to enable everything for the test.
    ppu.busWrite(0xFF47, 0xE4) # BGP: Default palette for the background
    ppu.busWrite(0xFF48, 0xE4) # OBP0: Sprite Palette 0 (also default)
    ppu.busWrite(0xFF40, 0x93) # LCDC: PPU On, BG On, Sprites On

    # --- Main Loop ---
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Scrolling controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: ppu.scx = (ppu.scx - 2) & 255
        if keys[pygame.K_RIGHT]: ppu.scx = (ppu.scx + 2) & 255
        if keys[pygame.K_UP]: ppu.scy = (ppu.scy - 2) & 255
        if keys[pygame.K_DOWN]: ppu.scy = (ppu.scy + 2) & 255
        
        # Manually render one full frame
        for i in range(144):
            ppu.ly = i
            ppu.renderLine()
        
        # Draw the completed framebuffer to the screen
        fb.drawFB(screen)
        
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
if __name__ == '__main__':
    main()
