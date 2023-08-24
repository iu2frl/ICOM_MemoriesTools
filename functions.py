def HexToAscii(inputData: str, startIndex: int, stopIndex: int) -> str:
    return str(bytes.fromhex(inputData[startIndex:stopIndex])).replace("b\'","").replace("\'","")