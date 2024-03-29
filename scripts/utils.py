def chunks(arr: list, n: int):
    '''
        returns arr broken into n-sized chunks
    '''
    chunks = []
    for i in range(0, len(arr), n):
        chunks.append(arr[i: i + n])
    return chunks
