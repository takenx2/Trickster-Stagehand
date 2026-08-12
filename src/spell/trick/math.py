from spell.blunders import Blunder
from spell.fragments import AddableFragment,SubtractableFragment,MultiplicableFragment,DivisibleFragment,Pattern,Fragment
from spell.trick.tricks import Trick
from spell.execution.executor import Context

class ArithmeticBlunder(Blunder):
    types: tuple[Fragment,Fragment]
    def __init__(self, trace,types: tuple[Fragment,Fragment]):
        super().__init__(trace)
        self.types = types
    def __str__(self):
        return f'Incompatible Types: "{self.types[0].plain_name}" and "{self.types[1].plain_name}"'


add = Trick(Pattern.of(7,4,0,1,2,4),"Annexation Stratagem")
@add(AddableFragment,"...")
def add_function(ctx: Context,*fragments: AddableFragment) -> AddableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        x = ret.add(fragment)
        if x==None:
            raise ArithmeticBlunder(ctx.state.trace,(type(ret),type(fragment)))
        ret = x
    return ret
subtract = Trick(Pattern.of(2,4,6,7,8,4),"Desertion Stratagem")
@subtract(SubtractableFragment,"...")
def sub(ctx: Context, *fragments: SubtractableFragment) -> SubtractableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        x = ret.sub(fragment)
        if x==None:
            raise ArithmeticBlunder(ctx.state.trace,(type(ret),type(fragment)))
        ret = x
    return ret
multiply = Trick(Pattern.of(2,1,0,4,8,7,6),"Domination Stratagem")
@multiply(MultiplicableFragment,"...")
def mult(ctx: Context, *fragments: MultiplicableFragment) -> MultiplicableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        x = ret.mul(fragment)
        if x==None:
            raise ArithmeticBlunder(ctx.state.trace,(type(ret),type(fragment)))
        ret = x
    return ret
divide = Trick(Pattern.of(0,1,2,4,6,7,8),"Submission Stratagem")
@divide(DivisibleFragment,"...")
def div(ctx: Context, *fragments: DivisibleFragment) -> DivisibleFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        x = ret.div(fragment)
        if x==None:
            raise ArithmeticBlunder(ctx.state.trace,(type(ret),type(fragment)))
        ret = x
    return ret
