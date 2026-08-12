from spell.trick.tricks import Trick
from spell.blunders import Blunder
from spell.fragments import Pattern,SpellPart,Fragment
from spell.execution.defaultexec import DefaultSpellExecutor,Context
quiet_eval = Trick(Pattern.of(0, 1, 4, 5, 8, 7, 6, 3, 0),"Quiet Deviation")
@quiet_eval(SpellPart)
def quiet_func(ctx: Context,part: SpellPart):
    return DefaultSpellExecutor(part,ctx.state.recurse(*ctx.state.args))
grand_eval = Trick(Pattern.of(3, 4, 5, 8, 7, 6, 3, 0, 1, 4, 7),"Grand Deviation")
@grand_eval(SpellPart,Fragment,"...")
def grand_func(ctx: Context,part: SpellPart,*args: Fragment):
    return DefaultSpellExecutor(part,ctx.state.recurse(*args))