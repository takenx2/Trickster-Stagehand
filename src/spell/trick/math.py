from spell.fragments import AddableFragment,SubtractableFragment,MultiplicableFragment,DivisibleFragment,Pattern
from spell.trick.tricks import Trick
from spell.execution.executor import ExecutionState


add = Trick(Pattern.of(7,4,0,1,2,4),"Annexation Stratagem")
@add(AddableFragment,"...")
def add_function(ctx: ExecutionState,*fragments: AddableFragment) -> AddableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.add(fragment)
    return ret
subtract = Trick(Pattern.of(2,4,6,7,8,4),"Desertion Stratagem")
@subtract(SubtractableFragment,"...")
def sub(ctx: ExecutionState, *fragments: SubtractableFragment) -> SubtractableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.sub(fragment)
    return ret
multiply = Trick(Pattern.of(2,1,0,4,8,7,6),"Domination Stratagem")
@multiply(MultiplicableFragment,"...")
def mult(ctx: ExecutionState, *fragments: MultiplicableFragment) -> MultiplicableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.mul(fragment)
    return ret
divide = Trick(Pattern.of(0,1,2,4,6,7,8),"Submission Stratagem")
@divide(DivisibleFragment,"...")
def div(ctx: ExecutionState, *fragments: DivisibleFragment) -> DivisibleFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.div(fragment)
    return ret
