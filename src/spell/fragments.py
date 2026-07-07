from __future__ import annotations
from abc import ABC, abstractmethod
import struct
from io import BytesIO
from spell.blunders import *
from copy import deepcopy
class Fragment(ABC):
    _fragments: dict[str,Fragment] = {}
    _typecolors: dict[str,int] = {}
    def __init_subclass__(cls,id: str=None,color=0xffffffff):
        #print(id)
        if (id != None) and id in cls._fragments.keys():
            raise KeyError("id already in use, pick another looser")
        else:
            cls._fragments[id] = cls
            cls._typecolors[id] = color
        return super().__init_subclass__()
    def copy[T](self: T) -> T:
        return deepcopy(self)
    @abstractmethod 
    def decode(encoded: BytesIO) -> Fragment: ...
    @abstractmethod
    def encode(self) -> bytes: ...
class AddableFragment(Fragment):
    @abstractmethod
    def add(self,other: AddableFragment) -> AddableFragment: ...
class SubtractableFragment(Fragment):
    @abstractmethod
    def sub(self,other: SubtractableFragment) -> SubtractableFragment: ...
class DivisibleFragment(Fragment):
    @abstractmethod
    def div(self,other: DivisibleFragment) -> DivisibleFragment: ...
class MultiplicableFragment(Fragment):
    @abstractmethod
    def mul(self,other: MultiplicableFragment) -> MultiplicableFragment: ...

class GenericFragment[T](Fragment):
    value: T
    def __init__(self,value:T):
        self.value = value
        super().__init__()
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value.__repr__()})"
    def __str__(self):
        return self.value.__str__()
class NumberFragment(AddableFragment,SubtractableFragment,GenericFragment[float],id="trickster:number"):
    def decode(encoded: BytesIO):
        return NumberFragment(struct.unpack(">d",encoded.read(8))[0])
    def encode(self):
        return struct.pack(">d",self.value)
    def add(self,other):
        if isinstance(other,NumberFragment):
            return NumberFragment(self.value+other.value)
        raise ArithmeticBlunder
    def sub(self, other):
        if isinstance(other,NumberFragment):
            return NumberFragment(self.value-other.value)
        raise ArithmeticBlunder
class StringFragment(GenericFragment[str],id="trickster:string"):
    def decode(encoded: BytesIO):
        size = encoded.read(1)[0]
        return StringFragment(str(encoded.read(size),"utf-8"))
    def encode(self):
        Bite = bytes()
        Bite+=len(self.value).to_bytes()
        Bite+=bytes(self.value,"utf-8")
        return Bite
class BooleanFragment(GenericFragment[bool],id="trickster:boolean"):
    def decode(encoded: BytesIO):
        return BooleanFragment(encoded.read(1)==b'\x01')
    def encode(self):
        return b'\x00' if self.value else b'\x01'
class VoidFragment(Fragment,id="trickster:void"):
    def __init__(self):
        pass
    def __repr__(self):
        return "VoidFragment()"
    def decode(encoded: BytesIO):
        return VoidFragment()
    def encode(self):
        return bytes()
    def __str__(self):
        return "Void"
class ZalgoFragment(Fragment,id="trickster:zalgo"):
    def __init__(self):
        pass
    def __repr__(self):
        return "ZalgoFragment()"
    def decode(encoded):
        return ZalgoFragment()
    def encode(self):
        return bytes()
    def __str__(self):
        return "?????"
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
    entries: set[tuple[int,int]]
    def __init__(self,entries: set[tuple[int,int]]):
        self.entries = set(entries)
    def fromBytes(bites: bytes) -> Pattern:
        lyst: set[tuple[int,int]] = set()
        last = None
        for byte in bites:
            if last!=None:
                if last<byte:
                    lyst.add((last,byte))
                else:
                    lyst.add((byte,last))
            last = byte
        return Pattern(lyst)
    def __hash__(self):
        return hash(self.toInt())
    def __eq__(self, value):
        return isinstance(value,Pattern) and self.toInt()==value.toInt()
    def fromInt(pattern: int) -> Pattern:
        lines = []
        for i in range(32):
            if ((pattern >> i) & 0x1) == 1:
                lines.append(_possibleLines[i])
        return Pattern(lines)
    def toInt(self) -> int:
        result = 0 
        for i in range(32):
            if _possibleLines[i] in self.entries:
                result |= 1 << i
        return result
    def of(*args: int) -> Pattern:
        lines = [(min(args[x],args[x+1]),max(args[x],args[x+1])) for x in range(len(args)-1)]
        valid = True
        for line in lines:
            if not (line in _possibleLines):
                valid = False
        if not valid:
            raise ValueError("Invalid Pattern!")
        return Pattern(lines)
    def decode(encoded: BytesIO):
        dat = encoded.read(4)
        try:
            i = struct.unpack(">i",dat)[0]
            return Pattern.fromInt(i)
        except ValueError:
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
    def __str__(self):
        term = self.get_terminal()
        s = ""
        entry = self.entries.copy()
        last = None
        while len(entry)>0:
            if last == None:
                if len(term)>0:
                    last = term.pop()
                else:
                    last = list(entry)[0][0]
        
            s+=str(last)
            found = False
            for line in entry.copy():
                if line[0]==last:
                    print(line)
                    entry.remove(line)
                    last = line[1]
                    found = True
                    break
                elif line[1]==last:
                    print(line)
                    entry.remove(line)
                    last = line[0]
                    found = True
                    break
            
            if not found:
                s+="|"
                try:
                    term.remove(last)
                except:
                    pass
                last = None
        s+=str(last)
        return s

            
        return s
    def get_terminal(self) -> list[int]:
        dots = [False]*9
        for entry in self.entries:
            dots[entry[0]] = not dots[entry[0]]
            dots[entry[1]] = not dots[entry[1]]
        ret = list()
        for x in range(9):
            if dots[x]:
                ret.append(x)
        return ret

class TypeFragment(Fragment,id="trickster:type"):
    typeid: str
    def __init__(self,id: str):
        if not (id in Fragment._fragments.keys()):
            raise KeyError(f"Unknown Fragment Type: {id}")
        self.typeid = id
        super().__init__()
    def decode(encoded: BytesIO):
        len = encoded.read(1)[0]
        return TypeFragment(str(encoded.read(len),"utf-8"))
    def encode(self):
        byte = bytes(len(self.typeid))
        byte += bytes(self.typeid,"utf-8")
        return byte
    def __repr__(self):
        return f"TypeFragment({self.typeid.__repr__()})"
    
