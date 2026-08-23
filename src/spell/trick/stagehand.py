from spell.trick.tricks import Trick
from spell.fragments import StringFragment,Pattern,NumberFragment,VoidFragment
from spell.execution import Context,ReadBufferExecutor
from sys import stdin

input = Trick(Pattern.of(3,4,5,2,1,0,3),"Listener's Delusion")
@input(NumberFragment)
def input_no_fallback(ctx: Context,timeout: NumberFragment) -> StringFragment:
    return ReadBufferExecutor(ctx.state,stdin,int(timeout.value))
@input(NumberFragment,StringFragment)
def input_fallback(ctx: Context,timeout: NumberFragment,fallback: StringFragment) -> StringFragment:
    return ReadBufferExecutor(ctx.state,stdin,int(timeout.value),fallback.copy())
