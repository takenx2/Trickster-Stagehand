from spell.trick.tricks import Trick
from spell.execution import Context
from spell.fragments import Pattern,NumberFragment,Fragment,TypeFragment
suspend = Trick(Pattern.of(0, 2, 4, 6, 8, 4, 0),"Ploy of Suspension")
@suspend(NumberFragment)
def pause(ctx: Context,num: NumberFragment):
    ctx.state.delay += int(num.value)
    return num
showcase = Trick(Pattern.of(3,4,5,8,7,6,3),"Showcase Ploy")
@showcase(Fragment,"...")
def show(ctx: Context,*fragments: Fragment) -> Fragment:
    e = ""
    for frag in fragments:
        e+=str(frag)+", "
    print(f"{e[:-2]}")
    return fragments[0]
get_type = Trick(Pattern.of(3,4,1,0,4,5),"Argumentative Distortion")
@get_type(Fragment)
def gt_func(ctx:Context,frag:Fragment) -> TypeFragment:
    id = Fragment.lookup(frag)
    return TypeFragment(id)