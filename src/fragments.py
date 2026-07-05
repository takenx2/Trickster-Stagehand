from __future__ import annotations
from abc import ABC, abstractmethod
import struct
from io import BytesIO
class Fragment(ABC):
    _fragments: dict[str,Fragment] = {}
    def __init_subclass__(cls,id: str=None):
        #print(id)
        if (id != None) and id in cls._fragments.keys():
            raise KeyError("id already in use, pick another looser")
        else:
            cls._fragments[id] = cls
        return super().__init_subclass__()
    @abstractmethod 
    def decode(encoded: BytesIO) -> Fragment:
        pass
    @abstractmethod
    def encode(self) -> bytes:
        pass

class GenericFragment[T](Fragment):
    value: T
    def __init__(self,value:T):
        self.value = value
        super().__init__()
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value.__repr__()})"
class NumberFragment(GenericFragment[float],id="trickster:number"):
    def decode(encoded: BytesIO):
        return NumberFragment(struct.unpack(">d",encoded.read(8))[0])
    def encode(self):
        return struct.pack(">d",self.value)
class StringFragment(GenericFragment[str],id="trickster:string"):
    def decode(encoded: BytesIO):
        size = encoded.read(1)[0]
        return StringFragment(str(encoded.read(size),"utf-8"))
    def encode(self):
        Bite = bytes()
        Bite+=len(self.value).to_bytes()
        Bite+=bytes(self.value,"utf-8")
        return Bite

class VoidFragment(Fragment,id="trickster:void"):
    def __init__(self):
        pass
    def __repr__(self):
        return "VoidFragment()"
    def decode(encoded: BytesIO):
        return VoidFragment()
    def encode(self):
        return bytes()
_possibleLines: list[tuple[int,int]] = []
for p1 in range(9):
    for p2 in range(9):
        if (p2 > p1) and (p1 + p2) != 8:
            _possibleLines.append((p1,p2))
# print(_possibleLines)
def sort_with(tup: tuple[int,int]):
    return _possibleLines.index(tup)
#print(__possibleLines)
class Pattern(Fragment,id="trickster:pattern"):
    entries: list[tuple[int,int]]
    def __init__(self,entries: list[tuple[int,int]]):
        self.entries = entries
    def fromBytes(bites: bytes) -> Pattern:
        lyst: list[tuple[int,int]] = []
        last = None
        for byte in bites:
            if last!=None:
                if last<byte:
                    lyst.append((last,byte))
                else:
                    lyst.append((byte,last))
            last = byte
        lyst.sort(key=sort_with)
        return Pattern(lyst)
    def fromInt(pattern: int) -> Pattern:
        lines = []
        print(pattern & 0x1)
        for i in range(32):
            if ((pattern >> i) & 0x1) == 1:
                lines.append(_possibleLines[i])
        return Pattern(lines)
    def toInt(self) -> int:
        result = 0 
        for i in range(32):
            if _possibleLines[i] in self.entries:
                print(result)
                result |= 1 << i
        return result
    def of(*args: int) -> Pattern:
        lines = [(args[x],args[x+1]) for x in range(len(args)-1)]
        print(lines)
        valid = True
        for line in lines:
            if not (line in _possibleLines):
                valid = False
        if not valid:
            raise ValueError("Invalid Pattern!")
        return Pattern(lines)
    def decode(encoded: BytesIO):
        print(encoded.getvalue())
        dat = encoded.read(4)
        try:
            i = struct.unpack(">i",dat)[0]
            print(i)
            return Pattern.fromInt(i)
        except ValueError:
            print("err")
            return Pattern.of()
        # print(encoded.getvalue())
        # length = encoded.read(1)[0]
        # lyst = []
        # for i in range(length):
        #     b = encoded.read(2)
        #     lyst.append((b[0],b[1]))
        # return Pattern(lyst)
    def encode(self):
        bites = bytes()
        bites+=struct.pack(">i",self.toInt())
        return bites
    def __repr__(self):
        return f"Pattern({self.entries})"