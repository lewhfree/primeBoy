# from registerDefinitions import *
import fileloader
import cartridge
import ramtypes
import busfile
import ppufile
import cpu
import intcallerfile
import pygame
import framebufferfile
HEIGHT, WIDTH = 144, 160
SCALE = 2
bootrom = fileloader.loadBin('boot.bin')
rom = fileloader.loadBin('tetris.gb')
#init systems
cart = cartridge.loadCart(rom)
vram = ramtypes.Ram(0x2000)
wram = ramtypes.Ram(0x2000)
oam  = ramtypes.Ram(0xA0)
hram = ramtypes.Ram(0x7F)
bus  = busfile.Bus(bootrom, cart, vram, wram, oam, hram)
cpuo = cpu.CPU(bus)
intcaller = intcallerfile.IntCaller(cpuo)

screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
pygame.display.set_caption("PrimeBoy Display")

framebuffer = framebufferfile.FB()
ppu = ppufile.PPU(bus, framebuffer, intcaller)

bus.loadPPU(ppu) # I need to do this because the bus calls ppu functions to pass on r/w to it
                 # I will probably have to do the same thing for the rest of the peripherals.

for x in range(256):
    for y in range(256):
        ppu.fb.writePixel(x, y, ((x*y) % 4))


framebuffer.drawFB(screen)
# class CPU: #in charge of all the alu idu clock
while 1:
    ppu.step(1)

    
# class APU: #haha no
# class TIMER: #
# class IRCONTROLLER:
# class INPUT:
        
