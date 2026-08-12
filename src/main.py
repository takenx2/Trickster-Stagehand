
from spell.execution.defaultexec import DefaultSpellExecutor
from spell.execution.executor import TickData
from spell.fragments import NumberFragment,SpellPart,PatternGlyph
# print(tricks.Trick.tricks)
from spell.trick.eval import quiet_eval
from spell.trick.arguments import *
from spell.trick.basic import showcase
from spell.trick.math import add,multiply
spell = SpellPart(
    SpellPart(
        PatternGlyph(quiet_eval.pattern),
        SpellPart(PatternGlyph(arg1.pattern))
    ),
    SpellPart(
        SpellPart(
            None,
            [
                SpellPart(PatternGlyph(quiet_eval.pattern),
                    SpellPart(PatternGlyph(arg1.pattern))
                ),
                SpellPart(PatternGlyph(showcase.pattern),
                    SpellPart(NumberFragment(2))
                )
            ]
        )
    )
)
try:
    print("result:",DefaultSpellExecutor(spell).run_without_context("",TickData()))
except Blunder as b:
    print(str(b))
# spell = SpellPart(
#             PatternGlyph(add.pattern),
#             [SpellPart(NumberFragment(2)),SpellPart(NumberFragment(2)),SpellPart(NumberFragment(3))]
#         )