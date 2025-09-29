import ramtypes
import cartridge
class Bus: # i am going to ignore cart ram for now, ill do it later
    def __init__(self, bootrom, cart:cartridge.Cartridge, vram:ramtypes.Ram, wram:ramtypes.Ram, oam:ramtypes:Ram, hram:ramtypes:Ram):
        self.bootrom = bootrom
        self.cart = cart
        self.vram = vram
        self.cartram = 0
        self.wram = wram
        self.oam = oam
        self.hram = hram

        #flags
        self.bootromEnabled = 1
        self.canReadVram = 1
        self.canReadOAM = 1
        self.canWriteVram = 1
        self.canWriteOAM = 1
        self.IE = 0
        self.ppu = 0
    def loadPPU(self, ppu):
        self.ppu = ppu
    def readByte(self, addr:int):
        if 0x0000 <= addr <= 0x7FFF:
            if addr <= 0xFF and self.bootromEnabled:
                return self.bootrom[addr]
            return self.cart.read(addr)
        elif 0x8000 <= addr <= 0x9FFF:
            if self.canReadVram:
                return self.vram.read(addr - 0x8000)
            else:
                return 0xFF
        elif 0xA000 <= addr <= 0xBFFF:
            return 0x00
            # I DO NOT WANT TO DO THIS
        elif 0xC000 <= addr <= 0xDFFF:
            return self.wram.read(addr - 0xC000)
        elif 0xE000 <= addr <= 0xFDFF:
            return self.wram.read(addr - 0xE000)
        elif 0xFE00 <= addr <= 0xFE9F:
            if self.canReadOAM:
                return self.oam.read(addr - 0xFE00)
            else:
                return 0xFF
        elif 0xFEA0 <= addr <= 0xFEFF:
            return 0xFF
            #borked
        elif 0xFF00 <= addr <= 0xFF7F:
            #io registers
            if addr == 0xFF40:
                return self.ppu.busRead()
        elif 0xFF80 <= addr <= 0xFFFE:
            return self.hram.read(addr - 0xFF80)
        elif addr == 0xFFFF:
            return self.IE
        else:
            print("UHH bus bus bus")
            exit()
    def writeByte(self, addr:int, val:int):
        if 0x8000 <= addr <= 0x9FFF:
            if self.canWriteVram:
                self.vram.write(addr - 0x8000, val)
        elif 0xA000 <= addr <= 0xBFFF:
            pass
            # I DO NOT WANT TO DO THIS
        elif 0xC000 <= addr <= 0xDFFF:
            self.wram.write(addr - 0xC000, val)
        elif 0xE000 <= addr <= 0xFDFF:
            self.wram.write(addr - 0xE000, val)
        elif 0xFE00 <= addr <= 0xFE9F:
            if self.canWriteOAM:
                self.oam.write(addr - 0xFE00, val)
        elif 0xFEA0 <= addr <= 0xFEFF:
            pass
        elif 0xFF00 <= addr <= 0xFF7F:
            #io registers
            if addr == 0xFF40:
                self.ppu.busWrite(val)
        elif 0xFF80 <= addr <= 0xFFFE:
            self.hram.write(addr - 0xFF80, val)
        elif addr == 0xFFFF:
            self.IE = val
        else:
            print("UHH busasdf bus bus")
            exit()
