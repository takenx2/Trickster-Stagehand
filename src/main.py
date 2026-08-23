import util
from spell.fragments import SpellPart,NumberFragment,StringFragment,PatternGlyph,PathFragment
from spell.execution import DefaultSpellExecutor
from spell.trick.arguments import *
from spell.trick.exec import grand
from spell.trick.math import multiply
from spell.trick.misc import suspend,showcase
from spell.trick.stagehand import input
import math,time,io,transfer
from pathlib import Path
spell = SpellPart(
    PatternGlyph(showcase.pattern),
    SpellPart(PatternGlyph(input.pattern),SpellPart(NumberFragment(-1)))
)
exec = DefaultSpellExecutor(spell)
path = Path("~","Pictures")
print(transfer.compress_fragment(spell))
# while True:1
#     time.sleep(1/20)
#     ret = exec.run(Path())
#     if ret!=None:
#         #print(ret)
#         break
print(pyside.Qt)