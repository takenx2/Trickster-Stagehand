from __future__ import annotations
import base64,gzip
from io import BytesIO
from fragments import *
from struct import unpack
from typing import Iterable
from collections import deque

GZIP_HEADER = bytes([0x1f,0x8b,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0xff])
PROTOCOL_VERSION = 6

def decode_spell_instructions(data: BytesIO) -> list[tuple[int,Fragment|None]]:
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
                        x = decode_fragment(data)
                    elif d[0]==2:
                        pass
                    instructions.append((d[0],x))
    return instructions
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
        glyph = decode_fragment(data)
        print(data.getvalue())
        instructions: list[tuple[int,Fragment|None]] = decode_spell_instructions(data)
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
        byte+=(1).to_bytes(4)+b'\x01'+encode_fragment(self.glyph)
        if len(self.subparts)>0:
            byte+=b'\x01\x01'+len(self.subparts*3).to_bytes()
            for part in self.subparts:
                byte+=(3).to_bytes(4)+b'\x00'
                byte+=part.halfencode()
                byte+=(2).to_bytes(4)+b'\x00'
        return byte
    def __repr__(self):
        return f'SpellPart({self.glyph}{f", {self.subparts}" if len(self.subparts)>0 else ""})' 
type Tree = list[Fragment|Tree]

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
            frgs.append(decode_fragment(encoded))
        return ListFragment(frgs)
    def encode(self):
        bite = bytes()
        bite+=len(self.fragments).to_bytes()
        for fragment in self.fragments:
            bite+=encode_fragment(fragment)
        return bite
    def __repr__(self):
        return f"ListFragment({self.fragments})"

def decompress_fragment(encoded: str) -> Fragment:
    unencoded = base64.b64decode(encoded.strip())
    decompressed = gzip.decompress(GZIP_HEADER+unencoded)
    format = decompressed[0]
    if format < 3:
        raise NotImplementedError("format versions under three not implemented")
    return decode_fragment(decompressed[1:])
def compress_fragment(fragment: Fragment) -> str:
    bite = encode_fragment(fragment)
    compressed = gzip.compress(PROTOCOL_VERSION.to_bytes()+bite)[len(GZIP_HEADER):]
    return str(base64.b64encode(compressed),"utf-8")
def decode_fragment(byteData: bytes|BytesIO) -> Fragment:
    if type(byteData) is bytes:
        data = BytesIO(byteData)
    else:
        data = byteData
    length = data.read(1)
    id = str(data.read(length[0]),"utf-8")
    frag = Fragment._fragments.get(id,None)
    if frag:
        ret = frag.decode(data)
        if isinstance(ret,Fragment):
            return ret
        else:
            
            return VoidFragment()
    return StringFragment(f'Unknown Fragment "{id}"')
def encode_fragment(fragment: Fragment) -> bytes:
    id = next((k for k, v in Fragment._fragments.items() if v == type(fragment)), None)
    bite = bytes()
    bite += len(id).to_bytes()
    bite += bytes(id,"utf-8")
    bite += fragment.encode()
    return bite