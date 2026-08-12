from __future__ import annotations
import base64,gzip
from io import BytesIO
import spell.fragments as fragments
GZIP_HEADER = bytes([0x1f,0x8b,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0xff])
PROTOCOL_VERSION = 6

def decompress_fragment(encoded: str) -> fragments.Fragment:
    unencoded = base64.b64decode(encoded.strip())
    decompressed = gzip.decompress(GZIP_HEADER+unencoded)
    format = decompressed[0]
    if format != 6:
        raise NotImplementedError("format versions other than six are not implemented.")
    return unpack_fragment(decompressed[1:])
def compress_fragment(fragment: fragments.Fragment) -> str:
    bite = pack_fragment(fragment)
    compressed = gzip.compress(PROTOCOL_VERSION.to_bytes()+bite)[len(GZIP_HEADER):]
    return str(base64.b64encode(compressed),"utf-8")
def unpack_fragment(byteData: bytes|BytesIO) -> fragments.Fragment:
    if type(byteData) is bytes:
        data = BytesIO(byteData)
    else:
        data = byteData
    length = data.read(1)
    id = str(data.read(length[0]),"utf-8")
    frag = fragments.Fragment._fragments.get(id,None)
    if frag:
        ret = frag.decode(data)
        if isinstance(ret,fragments.Fragment):
            return ret
        else:
            return fragments.ZalgoFragment()
    return fragments.ZalgoFragment()
def pack_fragment(fragment: fragments.Fragment) -> bytes:
    id = next((k for k, v in fragments.Fragment._fragments.items() if v == type(fragment)), None)
    bite = bytes()
    bite += len(id).to_bytes()
    bite += bytes(id,"utf-8")
    bite += fragment.encode()
    return bite
__all__ = ["pack_fragment","unpack_fragment","decompress_fragment","compress_fragment"]