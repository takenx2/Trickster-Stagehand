from spell.fragments import AddableFragment,SubtractableFragment,MultiplicableFragment,DivisibleFragment,Pattern
from base import Trick


def add(*fragments: AddableFragment) -> AddableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.add(fragment)
    return ret
Trick(Pattern.of(7,4,0,1,2,4),add,"Annexation Stratagem")
def sub(*fragments: SubtractableFragment) -> SubtractableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.sub(fragment)
    return ret
Trick(Pattern.of(2,4,6,7,8,4),sub,"Desertion Stratagem")
def mul(*fragments: MultiplicableFragment) -> MultiplicableFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.mul(fragment)
    return ret
Trick(Pattern.of(2,1,0,4,8,7,6),mul,"Domination Stratagem")
def div(*fragments: DivisibleFragment) -> DivisibleFragment:
    ret = fragments[0]
    for fragment in fragments[1:]:
        ret = ret.div(fragment)
    return ret
Trick(Pattern.of(0,1,2,4,6,7,8),div,"Submission Stratagem")