from spell.trick.tricks import Trick
from spell.blunders import Blunder
from spell.fragments import Pattern,SpellPart,Fragment,FoldableFragment
import spell.execution as exec
quiet = Trick(Pattern.of(0, 1, 4, 5, 8, 7, 6, 3, 0),"Quiet Deviation")
@quiet(SpellPart)
def quiet_func(ctx: exec.Context,part: SpellPart):
    return exec.DefaultSpellExecutor(part,ctx.state.recurse(*ctx.state.args))
grand = Trick(Pattern.of(3, 4, 5, 8, 7, 6, 3, 0, 1, 4, 7),"Grand Deviation")
@grand(SpellPart,Fragment,"...")
def grand_func(ctx: exec.Context,part: SpellPart,*args: Fragment):
    return exec.DefaultSpellExecutor(part,ctx.state.recurse(*args))
folding = Trick(Pattern.of(3, 6, 4, 0, 1, 2, 5, 8, 7, 4, 3),"Folding Deviation")
@folding(SpellPart,FoldableFragment,Fragment)
def fold_func(ctx:exec.Context,part:SpellPart,folding:FoldableFragment,identity:Fragment):
    return folding.fold(ctx,part,identity)