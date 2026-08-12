from spell.trick.tricks import Trick
from spell.execution.executor import Context
from spell.fragments import Pattern,NumberFragment
suspend = Trick(Pattern.of(0, 2, 4, 6, 8, 4, 0),"Ploy of Suspension")
@suspend(NumberFragment)
def pause(ctx: Context,num: NumberFragment):
    ctx.state.delay += int(num.value)
    return num