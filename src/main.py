
from spell.execution.defaultexec import DefaultSpellExecutor
from spell.fragments import NumberFragment,SpellPart,PatternGlyph,StringFragment
# print(tricks.Trick.tricks)
from spell.trick.eval import quiet_eval
from spell.trick.arguments import *
from spell.trick.basic import showcase
from spell.trick.misc import suspend
from spell.trick.math import add,multiply
from transfer import *
spell = SpellPart(
    PatternGlyph(suspend.pattern),
    [
        SpellPart(NumberFragment(20))
    ]
    
)
exec = DefaultSpellExecutor(spell)
# result = None
# while result==None:
#     try:
#         result = exec.run_path_data("")
#         sleep(1/20)
#     except Blunder as b:
#         print(str(b))
#         break
# else:
#     print(result)

dat = "YxMoKcpMzi4uSS2yKktNLskvYnZgwA4Ae57NsysAAAA="
print(decompress_fragment(dat))