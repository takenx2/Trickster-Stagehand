from __future__ import annotations
import base64,gzip
from io import BytesIO
from fragments import *
import struct
from enum import Enum

b64 = "YxMpKcpMzi4uSS2yKi5IzcmJL0gsKuFDCJblZ6YwAAA8irKGJgAAAA==" #SpellPart(Void)
b64 = "YxMpKcpMzi4uSS2yKi5IzcmJL0gsKuFDCJblZ6YwMjIzMDCAMAMjI5ocUIyJAQBm1nz5RgAAAA==" #SpellPart(Void,[Void])
b64 = "YxMpKcpMzi4uSS2yKi5IzcmJL0gsKuFDCJblZ6YwMTIzMDCAMAMjI5ocUIyJgZA8AIAmv2lmAAAA" #SpellPart(Void,[Void,Void])
b64 = "YxMpKcpMzi4uSS2yKi5IzcmJL0gsKuFDCJblZ6YwMzIzMDCAMAMjI5ocUIyJgVJ5AKRjhVSGAAAA" #SpellPart(Void,[Void,Void,Void])
b64 = "YxMpKcpMzi4uSS2yKi5IzcmJL0gsKuFDCJblZ6YwMzIzMDCAMAMjI5ocUIyJgZENnzwejRDdBEwHAHCd0+WkAAAA" #SpellPart(Void,[Void,SpellPart(Void,[Void]),Void])

GZIP_HEADER = bytes([0x1f,0x8b,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0xff])
PROTOCOL_VERSION = 6


class SpellPart(Fragment,id="trickster:spell_part"):
    #ENDEC
    #fragment - 'glyph'
    #
    glyph: Fragment
    subparts: list[SpellPart]
    def __init__(self,glyph: Fragment,subparts: list[Fragment]=[]):
        self.glyph = glyph
        self.subparts = subparts
        super().__init__()
    def decode(data: BytesIO):
        glyph = decode_fragment(data)
        #print(data.read())
        #TODO subparts
        print(data.read(1))
        subparts = []
        tell = data.tell()
        prev = b'\x00'
        while len(data.read())>0:
            data.seek(tell)
            red = data.read(2)
            print(red)
            if red==b'\x01\x01':
                subparts.append(decode_fragment(data))
                print(data.read(1))
            prev = red
            tell = data.tell()

        return SpellPart(glyph,subparts)
    def encode(self):
        return bytes()
    def __repr__(self):
        return f'SpellPart({self.glyph}{f", {self.subparts}" if len(self.subparts)>0 else ""})'
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
            pass
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
    print(id)
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
print(decompress_fragment(b64))
# compd = compress_fragment(Pattern.of(1,4,7))
# print(compd)