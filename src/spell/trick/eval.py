from spell.trick.tricks import Trick
from spell.blunders import Blunder
from spell.fragments import Fragment,Pattern,SpellPart
from spell.execution.defaultexec import DefaultSpellExecutor,ExecutionState
quiet_eval = Trick(Pattern.of(0, 1, 4, 5, 8, 7, 6, 3, 0),"Quiet Deviation")
@quiet_eval(SpellPart,"...")
def eval_trick(ctx: ExecutionState,part: SpellPart):
    return DefaultSpellExecutor(part)