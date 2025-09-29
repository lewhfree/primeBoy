class PPU:
    def __init__(self, bus, fb, intcaller):
        self.bus = bus
        self.fb = fb
        self.intcaller = intcaller

        self.ctrl = 0 # FF40
        self.stat = 0 # FF41
        self.scy = 0 # FF42
        self.scx = 0 # FF43
        self.ly = 0 # FF44
        self.lyc = 0 # FF45
        self.wy = 0 # FF4A
        self.wx = 0 # FF4B
        self.bg_palette = 0 # FF47
        self.obj_palette0 = 0 # FF48
        self.obj_palette1 = 0 # FF49

        self.dots = 0 # current line

    def step(self, clocks):
        addedDots = clocks * 4

        if not (self.ctrl & 0b10000000):
            self.dots = 0
            self.ly = 0
            self.stat = (self.stat & 0b11111100)
            return

        for _ in range(addedDots):
            self.dots += 1
            mode = self.stat & 0b11

            if mode == 2: # OAM objects on current line
                if self.dots >= 80:
                    self.stat = (self.stat & 0b11111100) | 3
            elif mode == 3: # pixels to screen
                if self.dots >= 252:
                    self.stat &= 0b11111100
                    if self.stat & 0b00001000:
                        self.intcaller.callInt(0x48)
                    self.renderLine()
            elif mode == 0: # Hblank
                if self.dots >= 456:
                    self.dots = 0
                    self.ly += 1
                    if self.ly == 144:
                        self.stat = (self.stat & 0b11111100) | 1
                        self.intcaller.callInt(0x40)
                        if self.stat & 0b00010000:
                            self.intcaller.callInt(0x48)
                        self.fb.drawFB(self.bus.screen)
                    else:
                        self.stat = (self.stat & 0b11111100) | 2
                        if self.stat & 0b00100000:
                            self.intcaller.callInt(0x48)
                    self.isLYCeqLY()
            elif mode == 1:
                if self.dots >= 456:
                    self.dots = 0
                    self.ly += 1
                    if self.ly > 153:
                        self.ly = 0
                        self.stat = (self.stat & 0b11111100) | 2
                        if self.stat & 0b00100000:
                           self.intcaller.callInt(0x48)
                    self.isLYCeqLY()

    def isLYCeqLY(self):
        if self.ly == self.lyc:
            self.stat |= 0b00000100
            if self.stat & 0b01000000: #int if needed 
                self.intcaller.callInt(0x48)
        else:
            self.stat &= 0b11111011

    def renderLine(self):
        if self.ly >= 144: return

        bufftemp = [0] * 160
        bgPriority = [False] * 160
        
        if self.ctrl & 0b00000001:
            self.renderBGandWIN(bufftemp, bgPriority)

        if self.ctrl & 0b00000010:
            self.renderSprite(bufftemp, bgPriority)
        
        for x in range(160):
            self.fb.writePixel(x, self.ly, bufftemp[x])
            
    def renderBGandWIN(self, lineBuff, priorityBuff):
        winY = self.ly - self.wy
        winIsEnabled = (self.ctrl & 0b00100000) and (0 <= winY < 144)

        BGtilemap = 0x9C00 if (self.ctrl & 0b00001000) else 0x9800
        WINtilemap = 0x9C00 if (self.ctrl & 0b01000000) else 0x9800
        tileDataSigned = not (self.ctrl & 0b00010000)

        yBGMap = (self.scy + self.ly) & 255

        for x in range(160):
            isWindowPixel = winIsEnabled and (x >= self.wx - 7)

            if isWindowPixel:
                xMap = x - (self.wx - 7)
                yMap = winY
                tileMapBase = WINtilemap
            else:
                xMap = (self.scx + x) & 255
                yMap = yBGMap
                tileMapBase = BGtilemap

            tileY, tileX = yMap // 8, xMap // 8
            tileMapAddr = tileMapBase + tileY * 32 + tileX
            tileID = self.bus.read(tileMapAddr)

            tileDataBaseAddr = 0x8000
            if tileDataSigned:
                tileDataBaseAddr = 0x9000
                if tileID > 127: tileID -= 256

            tileAddr = tileDataBaseAddr + tileID * 16
            
            rowInTitle = yMap % 8
            byte1 = self.bus.read(tileAddr + rowInTitle * 2)
            byte2 = self.bus.read(tileAddr + rowInTitle * 2 + 1)
            
            columnInTile = 7 - (xMap % 8)
            
            colorID = ((byte2 >> columnInTile) & 1) << 1 | ((byte1 >> columnInTile) & 1)
            
            if colorID != 0:
                priorityBuff[x] = True
            
            lineBuff[x] = (self.bg_palette >> (colorID * 2)) & 0b11

    def renderSprite(self, line_buffer, priority_buffer):
        spriteH = 16 if (self.ctrl & 0b00000100) else 8
        
        visibleSprites = []
        for i in range(40):
            addr = 0xFE00 + i * 4
            Y = self.bus.read(addr) - 16
            if Y <= self.ly < Y + spriteH:
                visibleSprites.append({
                    "y": Y, "x": self.bus.read(addr + 1) - 8, 
                    "tile_id": self.bus.read(addr + 2),
                    "attrs": self.bus.read(addr + 3),
                    "oam_index": i
                })
                if len(visibleSprites) >= 10:
                    break
        
        visibleSprites.sort(key=lambda s: (s['x'], s['oam_index']), reverse=True)

        for sprite in visibleSprites:
            attrs = sprite['attrs']
            xFlip = attrs & 0b00100000
            yFilp = attrs & 0b01000000
            bgOverTop = attrs & 0b10000000
            palette = self.obj_palette1 if (attrs & 0b00010000) else self.obj_palette0
            
            rowSprite = self.ly - sprite['y']
            if yFilp: rowSprite = spriteH - 1 - rowSprite
                
            tileID = sprite['tile_id']
            if spriteH == 16: tileID &= 0xFE

            tileAddr = 0x8000 + tileID * 16
            byte1 = self.bus.read(tileAddr + rowSprite * 2)
            byte2 = self.bus.read(tileAddr + rowSprite * 2 + 1)

            for xIsInSprite in range(8):
                xIsOnScreen = sprite['x'] + xIsInSprite
                if not (0 <= xIsOnScreen < 160): continue

                if bgOverTop and priority_buffer[xIsOnScreen]:
                    continue

                columnInSprite = 7 - xIsInSprite if not xFlip else xIsInSprite
                
                colorID = ((byte2 >> columnInSprite) & 1) << 1 | ((byte1 >> columnInSprite) & 1)
                
                if colorID == 0: continue
                
                color = (palette >> (colorID * 2)) & 0b11
                line_buffer[xIsOnScreen] = color

    def busWrite(self, addr, val):
        if addr == 0xFF40: self.ctrl = val
        elif addr == 0xFF41: self.stat = (val & 0b11111000) | (self.stat & 0b00000111)
        elif addr == 0xFF42: self.scy = val
        elif addr == 0xFF43: self.scx = val
        elif addr == 0xFF44: self.ly = 0
        elif addr == 0xFF45: self.lyc = val
        elif addr == 0xFF47: self.bg_palette = val
        elif addr == 0xFF48: self.obj_palette0 = val
        elif addr == 0xFF49: self.obj_palette1 = val
        elif addr == 0xFF4A: self.wy = val
        elif addr == 0xFF4B: self.wx = val

    def busRead(self, addr):
        if addr == 0xFF40: return self.ctrl
        elif addr == 0xFF41: return self.stat | 0x80
        elif addr == 0xFF42: return self.scy
        elif addr == 0xFF43: return self.scx
        elif addr == 0xFF44: return self.ly
        elif addr == 0xFF45: return self.lyc
        elif addr == 0xFF47: return self.bg_palette
        elif addr == 0xFF48: return self.obj_palette0
        elif addr == 0xFF49: return self.obj_palette1
        elif addr == 0xFF4A: return self.wy
        elif addr == 0xFF4B: return self.wx
        return 0
