from __future__ import annotations
from abc import ABC, abstractmethod
import struct
from io import BytesIO
from sys import maxsize
from typing import Iterable
from spell.blunders import *
from copy import deepcopy
from random import randrange
import spell.execution.executor as executor
import spell.execution.defaultexec as defaultexec
import spell.trick.tricks as tricks
import transfer
class Fragment(ABC):
    _fragments: dict[str,Fragment] = {}
    _typecolors: dict[str,int] = {}
    plain_name: str = "Unknown"
    def __init_subclass__(cls,id: str=None,color=0xffffffff):
        if (id != None) and id in cls._fragments.keys():
            raise KeyError("id already in use.")
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
    def hash_that_can_lie(self) -> int:
        return hash(self)
    def activate(self,ctx:executor.Context,args:tuple[Fragment]) -> Fragment|executor.SpellExecutor:
        """this also returns spell executors, sometimes.
        dw about it. <3"""
        return self.copy()
    def equals(self,other:Fragment) -> bool:
        return False
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
class MappableFragment[T](Fragment):
    value: T
    def __init__(self,value:T):
        self.value = value
        super().__init__()
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value.__repr__()})"
    def __str__(self):
        return self.value.__str__()
    def __hash__(self):
        return hash(self.value)
    def equals(self, other):
        if isinstance(other,MappableFragment):
            return self.value==other.value
        return super().equals(other)
class NumberFragment(AddableFragment,SubtractableFragment,MultiplicableFragment,MappableFragment[float],id="trickster:number"):
    plain_name = "Number"
    def decode(encoded: BytesIO):
        return NumberFragment(struct.unpack(">d",encoded.read(8))[0])
    def encode(self):
        return struct.pack(">d",self.value)
    def add(self,other):
        if isinstance(other,NumberFragment):
            return NumberFragment(self.value+other.value)
        raise ArithmeticBlunder
    def mul(self, other):
        if isinstance(other,NumberFragment):
            return NumberFragment(self.value*other.value)
        raise ArithmeticBlunder
    def sub(self, other):
        if isinstance(other,NumberFragment):
            return NumberFragment(self.value-other.value)
        raise ArithmeticBlunder
    def __str__(self):
        return f"{self.value:.2f}"
class StringFragment(MappableFragment[str],id="trickster:string"):
    plain_name = "String"
    def decode(encoded: BytesIO):
        size = encoded.read(1)[0]
        return StringFragment(str(encoded.read(size),"utf-8"))
    def encode(self):
        Bite = bytes()
        Bite+=len(self.value).to_bytes()
        Bite+=bytes(self.value,"utf-8")
        return Bite
class BooleanFragment(MappableFragment[bool],id="trickster:boolean"):
    plain_name = "Boolean"
    def decode(encoded: BytesIO):
        return BooleanFragment(encoded.read(1)==b'\x01')
    def encode(self):
        return b'\x00' if self.value else b'\x01'
class VoidFragment(Fragment,id="trickster:void"):
    plain_name = "Void"
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
    plain_name = "???"
    def __init__(self):
        pass
    def __repr__(self):
        return "ZalgoFragment()"
    def decode(encoded):
        return ZalgoFragment()
    def encode(self):
        return bytes()
    def __str__(self):
        #I would LOVE to implement garbletext
        #but id rather do anything else.
        return "?????"
    def hash_that_can_lie(self):
        return randrange(-maxsize-1,maxsize)
class TypeFragment(Fragment,id="trickster:type"):
    typeid: str
    plain_name = "Type"
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
class ListFragment(Fragment,id="trickster:list"):
    fragments: list[Fragment]
    def __init__(self,iter: Iterable[Fragment]):
        self.fragments = []
        for frag in iter:
            self.fragments.append(frag)
        super().__init__()
    def decode(encoded: BytesIO):
        frgs = []
        for i in range(encoded.read(1)[0]):
            frgs.append(transfer.unpack_fragment(encoded))
        return ListFragment(frgs)
    def encode(self):
        bite = bytes()
        bite+=len(self.fragments).to_bytes()
        for fragment in self.fragments:
            bite+=transfer.pack_fragment(fragment)
        return bite
    def __repr__(self):
        return f"ListFragment({self.fragments})"
_possibleLines: list[tuple[int,int]] = []
for p1 in range(9):
    for p2 in range(9):
        if (p2 > p1) and (p1 + p2) != 8:
            _possibleLines.append((p1,p2))
def sort_with(tup: tuple[int,int]):
    return _possibleLines.index(tup)
class Pattern(Fragment,id="trickster:pattern_literal"):
    plain_name = "Pattern"
    entries: set[tuple[int,int]]
    def __init__(self,entries: set[tuple[int,int]]=[]):
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
    def __eq__(self, other):
        if isinstance(other,Pattern):
            return self.toInt()==other.toInt()
        return super().equals(other)
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
                    entry.remove(line)
                    last = line[1]
                    found = True
                    break
                elif line[1]==last:
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
        return f"\\{s}\\"
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
    def is_empty(self) -> bool:
        return len(self.entries)==0
    def activate(self):
        return PatternGlyph(self)
class SpellPart(Fragment,id="trickster:spell_part"):
    glyph: Fragment
    subparts: list[SpellPart]
    plain_name= "Spell Part"
    def __init__(self,glyph: Fragment=None,subparts: SpellPart|list[SpellPart]|None = None):
        if subparts==None:
            subparts=[]
        if glyph==None:
            glyph = PatternGlyph()
        self.glyph = glyph
        if isinstance(subparts,SpellPart):
            self.subparts = [subparts]
        else:
           self.subparts = subparts
        super().__init__()
    def decode(data: BytesIO):
        glyph = transfer.unpack_fragment(data)
        instructions: list[executor.SpellInstruction] = []
        l1 = struct.unpack("b",data.read(1))[0]
        for i in range(l1):
                if data.read(1)==b'\x01': 
                    l2 = struct.unpack("b",data.read(1))[0]
                    for z in range(l2):
                        v = data.read(5)
                        d = struct.unpack(">ib",v)
                        x = None
                        if d[0]==1:
                            x = transfer.unpack_fragment(data)
                        instructions.append(executor.SpellInstruction(d[0],x))
        return executor.SpellInstruction.decode(instructions,glyph)
    def encode(self):
        byte = transfer.pack_fragment(self.glyph)
        byte += len(self.subparts).to_bytes(1)
        for part in self.subparts:
            instructions = executor.SpellInstruction.flatten_spell(part)
            byte+=b'\x01'+len(instructions).to_bytes(1)
            for instruct in instructions:
                byte+=instruct.type.to_bytes(4)
                if instruct.type == executor.InstructType.FRAGMENT:
                    byte+=b'\x01'+transfer.pack_fragment(instruct.fragment)
                else:
                    byte+=b'\x00'
        return byte
    def __repr__(self):
        return f'SpellPart({self.glyph.__repr__()}{f", {self.subparts.__repr__()}" if len(self.subparts)>0 else ""})' 
    def __str__(self):
        if len(self.subparts)>0:
            e = ""
            for part in self.subparts:
                e+=str(part)+", "
            return f"({self.glyph}:[{e[:-2]}])"
        else:
            return f'({self.glyph})' 
    def activate(self, ctx, args):
        if len(args)==0:
            return super().activate(ctx, args)
        else:
            return defaultexec.DefaultSpellExecutor(self,ctx.state.recurse(*args))
    def is_empty(self):
        return len(self.subparts)==0 and (isinstance(self.glyph,Pattern) and self.glyph.is_empty())
class PatternGlyph(Fragment,id="trickster:pattern"):

    def __init__(self,pattern:Pattern=Pattern()):
        self.pattern = pattern
    def encode(self):
        return self.pattern.encode()
    def decode(encoded):
        return PatternGlyph(Pattern.decode(encoded))
    def activate(self,ctx,args):
        return tricks.callTrick(self.pattern,ctx,args)
    def __repr__(self):
        return f"PatternGlyph({repr(self.pattern)})"
    def __str__(self):
        return f'"{str(self.pattern)}"'