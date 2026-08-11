from spell.fragments import Fragment,Pattern
from spell.execution.executor import ExecutionState
from spell.trick.tricks import Trick

showcase = Trick(Pattern.of(3,4,5,8,7,6,3),"Showcase Ploy")
@showcase(Fragment,"...")
def show(ctx: ExecutionState,*fragments: Fragment) -> Fragment:
    e = ""
    for frag in fragments:
        e+=str(frag)+", "
    print(f"{e[:-2]}")
    return fragments[0]
