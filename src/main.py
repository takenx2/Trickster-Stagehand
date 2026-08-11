# from spell.trick.base import show
# import transfer
# from spell import metafragments

# read = input("ENTER FRAGMENT > ")

# fragment = transfer.decompress_fragment(read)
# if isinstance(fragment,metafragments.SpellPart):
#     show(fragment)
#     fragment=fragment.run_glyph()
# show(fragment)
import os,math
from spell.metafragments import SpellPart
from spell.fragments import VoidFragment