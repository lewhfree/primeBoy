def loadBin(path: str) -> bytes:
    file = open(path, 'rb')
    binary_data = file.read()
    file.close()
    return binary_data
