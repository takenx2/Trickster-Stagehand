from __future__ import annotations
import base64,gzip
from io import BytesIO
from spell.fragments import Fragment,ZalgoFragment

GZIP_HEADER = bytes([0x1f,0x8b,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0xff])
PROTOCOL_VERSION = 6

def decompress_fragment(encoded: str) -> Fragment:
    unencoded = base64.b64decode(encoded.strip())
    decompressed = gzip.decompress(GZIP_HEADER+unencoded)
    format = decompressed[0]
    if format != 6:
        raise NotImplementedError("format versions other than six are not implemented.")
    return unpack_fragment(decompressed[1:])
def compress_fragment(fragment: Fragment) -> str:
    bite = pack_fragment(fragment)
    compressed = gzip.compress(PROTOCOL_VERSION.to_bytes()+bite)[len(GZIP_HEADER):]
    return str(base64.b64encode(compressed),"utf-8")
def unpack_fragment(byteData: bytes|BytesIO) -> Fragment:
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
            
            return ZalgoFragment()
    return ZalgoFragment()
def pack_fragment(fragment: Fragment) -> bytes:
    id = next((k for k, v in Fragment._fragments.items() if v == type(fragment)), None)
    bite = bytes()
    bite += len(id).to_bytes()
    bite += bytes(id,"utf-8")
    bite += fragment.encode()
    return bite