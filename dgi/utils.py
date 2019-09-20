from struct import pack, unpack

def u16(n):
    if type(n) == int:
        return [x for x in pack('>H', n)]
    return unpack('>H', bytes(n))[0]

def u32(n):
    if type(n) == int:
        return [x for x in pack('>I', n)]
    return unpack('>I', bytes(n))[0]

def f32(n):
    if type(n) == float:
        return [x for x in pack('>f', n)]
    return unpack('>f', bytes(n))[0]
