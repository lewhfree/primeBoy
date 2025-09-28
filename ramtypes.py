class Ram:
    def __init__(self, size:int):
        self.ram = [0]*size
    def read(self, addr: int):
        return self.ram[addr]
    def write(self, addr: int, val: int):
        self.ram[addr] = val
