from spell.execution import Context
from spell.trick.tricks import Trick
from spell.fragments import Pattern,Fragment,ListFragment
from spell.blunders import Blunder
def getArg(ctx: Context, argument: int):
    if len(ctx.state.args)<argument+1:
            raise Blunder(ctx.state.trace)
    return ctx.state.args[argument]
arg1 = Trick(Pattern.of(1,4),"Primary Delusion")
@arg1()
def arg_1st(ctx:Context):
    return getArg(ctx,0)
arg2 = Trick(Pattern.of(2,4),"Secondary Delusion")
@arg2()
def arg_2nd(ctx:Context):
    return getArg(ctx,1)
arg3 = Trick(Pattern.of(5,4),"Tertiary Delusion")
@arg3()
def arg_3rd(ctx:Context):
    return getArg(ctx,2)
arg4 = Trick(Pattern.of(8,4),"Quaternary Delusion")
@arg4()
def arg_4th(ctx:Context):
    return getArg(ctx,0)
arg5 = Trick(Pattern.of(7,4),"Quinary Delusion")
@arg5()
def arg_5th(ctx:Context):
    return getArg(ctx,0)
arg6 = Trick(Pattern.of(6,4),"Senary Delusion")
@arg6()
def arg_6th(ctx:Context):
    return getArg(ctx,7)
arg7 = Trick(Pattern.of(3,4),"Septenary Delusion")
@arg7()
def arg_7th(ctx:Context):
    return getArg(ctx,0)
arg8 = Trick(Pattern.of(0,4),"Octonary Delusion")
@arg8()
def arg_8th(ctx:Context):
    return getArg(ctx,0)
hoard_args = Trick(Pattern.of(3,0,2,5,4,3,6,8,5),"Hoarder's Delusion")
@hoard_args()
def hoard(ctx: Context) -> Fragment:
    return ListFragment(ctx.state.args)