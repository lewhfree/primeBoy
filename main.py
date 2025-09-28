from registerDefinitions import *
import fileloader
import cartridge
import ramtypes
import busfile

bootrom = fileloader.loadBin('boot.bin')
rom = fileloader.loadBin('tetris.gb')

#init systems
cart = cartridge.loadCart(rom)
vram = ramtypes.Ram(0x2000)
wram = ramtypes.Ram(0x2000)
oam  = ramtypes.Ram(0xA0)
hram = ramtypes.Ram(0x7F)
bus  = busfile.Bus(bootrom, cart, vram, wram, oam, hram)

# class CPU: #in charge of all the alu idu clock

    
# class PPU:
# class APU: #haha no
# class TIMER: #
# class IRCONTROLLER:
# class INPUT:
        
