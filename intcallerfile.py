class IntCaller:
    def __init__(self, cpu):
        self.cpu = cpu
    def callInt(self, val):
        self.cpu.interupt(val)
