from __future__ import annotations
from fragments import *
from spell.trick.base import callTrick
from transfer import unpack_fragment,pack_fragment
from struct import unpack
from typing import Iterable
# fragments that cant go in `fragments.py` for reason xyz...

type Tree = list[Fragment|Tree]
class SpellPart(Fragment,id="trickster:spell_part"):
    glyph: Fragment
    subparts: list[SpellPart]
    def __init__(self,glyph: Fragment,subparts: list[Fragment]|None = None):
        if subparts==None:
            subparts=[]
        self.glyph = glyph
        self.subparts = subparts
        super().__init__()
    def decode(data: BytesIO):
        glyph = unpack_fragment(data)
        instructions = []
        l1 = unpack("b",data.read(1))[0]
        for i in range(l1):
                if data.read(1)==b'\x01': 
                    l2 = unpack("b",data.read(1))[0]
                    for z in range(l2):
                        v = data.read(5)
                        d = unpack(">ib",v)
                        x = None
                        if d[0]==1:
                            x = unpack_fragment(data)
                        elif d[0]==2:
                            pass
                        instructions.append((d[0],x))
        tree: list[SpellPart] = list([SpellPart(glyph)])
        for i in instructions:
            match i[0]:
                case 3:
                    tree.append(SpellPart(VoidFragment()))
                case 1:
                    tree[-1].glyph = i[1]
                case 2:
                    part = tree.pop()
                    tree[-1].subparts.append(part)
        return tree[0]
    def encode(self):
        byte = self.halfencode()
        byte = byte[5:]
        return byte
    def halfencode(self) -> bytes:
        byte = bytes()
        byte+=(1).to_bytes(4)+b'\x01'+pack_fragment(self.glyph)
        if len(self.subparts)>0:
            byte+=b'\x01\x01'+len(self.subparts*3).to_bytes()
            for part in self.subparts:
                byte+=(3).to_bytes(4)+b'\x00'
                byte+=part.halfencode()
                byte+=(2).to_bytes(4)+b'\x00'
        return byte
    def run_glyph(self,args: list[Fragment]=[]) -> Fragment:
        if isinstance(self.glyph, Pattern):
            frags = []
            for part in self.subparts:
                frags.append(part.run_glyph())
            return callTrick(self.glyph,args,*frags)
        else:
            return self.glyph.copy()
    def __repr__(self):
        return f'SpellPart({self.glyph.__repr__()}{f", {self.subparts.__repr__()}" if len(self.subparts)>0 else ""})' 
    def __str__(self):
        if len(self.subparts)>0:
            e = ""
            for part in self.subparts:
                e+=str(part)+", "
            return f"({self.glyph}:({e[:-2]}))"
        else:
            return f'({self.glyph})' 


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
            frgs.append(unpack_fragment(encoded))
        return ListFragment(frgs)
    def encode(self):
        bite = bytes()
        bite+=len(self.fragments).to_bytes()
        for fragment in self.fragments:
            bite+=pack_fragment(fragment)
        return bite
    def __repr__(self):
        return f"ListFragment({self.fragments})"
