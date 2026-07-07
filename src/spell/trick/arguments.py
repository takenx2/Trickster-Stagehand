from base import Trick
from fragments import Pattern,Fragment
from metafragments import ListFragment
from blunders import Blunder
def getArg(argument: int):
    def getArgReturn(args: list[Fragment]) -> Fragment:
        arg = args[argument]
        if arg==None:
            raise Blunder()
        else:
            return arg
    return getArgReturn
Trick(Pattern.of(1,4),getArg(0),"Primary Delusion")
Trick(Pattern.of(2,4),getArg(1),"Secondary Delusion")
Trick(Pattern.of(5,4),getArg(2),"Tertiary Delusion")
Trick(Pattern.of(8,4),getArg(3),"Quaternary Delusion")
Trick(Pattern.of(7,4),getArg(4),"Quinary Delusion")
Trick(Pattern.of(6,4),getArg(5),"Senary Delusion")
Trick(Pattern.of(3,4),getArg(6),"Septenary Delusion")
Trick(Pattern.of(0,4),getArg(7),"Octonary Delusion")
def hoard(args: list[Fragment]) -> Fragment:
    return ListFragment(args)
Trick(Pattern.of(3,0,2,5,4,3,6,8,5),hoard,"Hoarder's Delusion")