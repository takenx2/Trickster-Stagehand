from io import BytesIO

from spell.execution.defaultexec import DefaultSpellExecutor,ExecutionState
from spell.trick.eval import quiet_eval
from spell.trick.basic import showcase
from spell.fragments import NumberFragment,ZalgoFragment,SpellPart
from sys import maxsize
from random import randrange
from transfer import pack_fragment,unpack_fragment,decompress_fragment,compress_fragment
# print(tricks.Trick.tricks)
from spell.trick.math import add,multiply
from spell.trick.basic import show
spell = SpellPart(
    add.pattern,
    [
        SpellPart(NumberFragment(2)),
        SpellPart(
            multiply.pattern,
            [
                SpellPart(NumberFragment(2)),
                SpellPart(NumberFragment(2))
            ]
        )
    ]
)
print(DefaultSpellExecutor(spell).run())
spell = SpellPart(
            add.pattern,
            [SpellPart(NumberFragment(2)),SpellPart(NumberFragment(2)),SpellPart(NumberFragment(3))]
        )