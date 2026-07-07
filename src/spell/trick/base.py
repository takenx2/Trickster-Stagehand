from __future__ import annotations
from fragments import *
from typing import Protocol
import inspect
class Overload(Protocol):
    def __call__(self, *args: Fragment) -> Fragment: ...

class SignatureBlunder(Blunder):
    trick: Trick
    inputs: tuple[Fragment]
    def __init__(self, trick, *inputs):
        self.trick = trick
        self.inputs = inputs
    def __str__(self):
        e = ""
        for inp in self.inputs:
            e+=str(inp)+", "
        return f"Invalid inputs: ({e[:-2]})"
class UnknownTrickBlunder(Blunder):
    pattern: Pattern
    def __init__(self, pattern: Pattern):
        self.pattern = pattern
    def __str__(self):
        return f"Unknown Trick with pattern: {self.pattern}"


def sortacheck(v: any,clas: str) -> bool:
    for c in v.__class__.__mro__:
        if c.__name__ == clas:
            return True
    return False
class Trick():
    _tricks: dict[Pattern,Trick] = {}
    _trick_names: dict[Trick,str] = {}
    overloads: list[Overload]
    def __init__(self,pattern:Pattern,overloads: list[Overload]|Overload,name:str=""):
        if isinstance(overloads,list):
            self.overloads = overloads
        else: 
            self.overloads = [overloads]
        if pattern in Trick._tricks.keys():
            raise KeyError(f"Pattern {pattern} already in use!")
        Trick._trick_names[self] = name
        Trick._tricks[pattern] = self
    def call(self,args: list[Fragment],*frags: Fragment) -> Fragment:        
        for overload in self.overloads:
            sig = inspect.signature(overload)
            i = 0
            try: 
                bound = sig.bind(args,*frags)
                bound.apply_defaults()
            except TypeError:
                continue
            valid = True
            for name,val in bound.arguments.items():
                param = sig.parameters[name]
                if param.annotation == inspect.Parameter.empty:
                    valid = False
                    break
                elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                    if not all(sortacheck(v,param.annotation) for v in val):
                        valid = False
                        break
                else:
                    if not sortacheck(val,param.annotation):
                        valid = False
                        break
            if valid:
                return overload(*args)
            else:
                raise SignatureBlunder(self,*args)
    def __str__(self):
        Trick._trick_names.get(self,"Unknown")
def callTrick(pat: Pattern,args:list[Fragment],*frags: Fragment) -> Fragment:
    trick: Trick = Trick._tricks.get(pat,None)
    if trick==None:
        raise UnknownTrickBlunder(pat)
    return trick.call(args,*frags)

def show(args: list[Fragment],*fragments: Fragment) -> Fragment:
    e = ""
    for frag in fragments:
        e+=str(frag)+", "
    print(f"({e[:-2]})")
    return fragments[0] or VoidFragment()
Trick(Pattern.of(3,4,5,8,7,6,3),show,"Showcase Ploy")
