from base import Trick
from blunders import Blunder
from fragments import Fragment,Pattern
from metafragments import SpellPart
def grand_eval(args: list[Fragment],spell: SpellPart,*frags: Fragment) -> Fragment:
    return spell.run_glyph(frags)
Trick(Pattern.of(3,4,5,8,7,4,1,0,3,6,7),grand_eval,"Grand Deviation")