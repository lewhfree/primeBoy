import busfile

class CPU:
    def __init__(self, bus:busfile.Bus):
        self.bus = bus
        self.A = 0
        self.F = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.PC = 0
        self.SP = 0
        
    def interupt(self, val):
        self.push16(self.PC) #Push the pc to stack
        self.PC = val
    def push8(self, val):
        self.SP -= 1
        self.bus.writeByte(self.PC, val)
    def push16(self, val):
        val1 = val >> 8
        val2 = val & 8
        self.push8(val1)
        self.push8(val2)
