from __future__ import annotations
import spell.fragments as fragments
from spell.execution import ExecutionState, SpellExecutor,Context
from typing import Literal
from collections.abc import Callable
from spell.blunders import Blunder


class TrickBlunder(Blunder):
    trick: Trick
    inputs: tuple[fragments.Fragment]
    def __init__(self, trace: list[int], trick : Trick):
        super().__init__(trace)
        self.trick = trick
    def __str__(self):
        return f'"{self.trick.name}": '
class InvalidSignature(TrickBlunder):
    given: tuple[fragments.Fragment]
    def __init__(self, trace:list[int], trick:Trick,*inputs:fragments.Fragment):
        super().__init__(trace, trick)
        self.given = inputs
    def __str__(self):
        e = super().__str__()+"Invalid inputs, the following signatures are valid for this trick:"
        for signature in self.trick.signatures:
            
            x = ""
            frags = signature[0]
            for frag in frags:
                if frag == "...":
                    x += "..."
                else:
                    x+=", "+frag.__name__
            e+="\n- "+x[2:]
        z = ""
        for inp in self.given:
            z+=repr(inp)+", "
        e+="\nThe following inputs were given: "+z[:-2]
        return e
class UnknownTrickBlunder(Blunder):
    pattern: fragments.Pattern
    def __init__(self, trace,pattern: fragments.Pattern):
        super().__init__(trace)
        self.pattern = pattern
    def __str__(self):
        return "Unknown Trick!"
type Various = type[fragments.Fragment]|Literal["..."]
type TrickFunction = Callable[[ExecutionState,tuple[fragments.Fragment,...]],fragments.Fragment|SpellExecutor]
class Trick():
    tricks: dict[fragments.Pattern,Trick] = {}
    """Every trick, indexed by pattern"""
    name: str
    """Trick's name"""
    signatures: list[tuple[tuple[Various,...],TrickFunction]] 
    """Every valid signature for the trick"""
    pattern: fragments.Pattern
    def __init__(self,pattern: fragments.Pattern,name:str="Unknown"):
        self.name = name
        self.signatures = []
        self.pattern = pattern
        if Trick.tricks.get(pattern) == None:
            Trick.tricks[pattern] = self
    def __call__(self,*vals: Various):
        def ret(tf: TrickFunction):
            self.signatures.append((vals,tf))
            return tf
        return ret
    def __repr__(self):
        return f"Trick({self.name},{self.signatures})"
    def activate(self,ctx:Context,args:list[fragments.Fragment]) -> fragments.Fragment|SpellExecutor:
        for signature in self.signatures:
            #print(signature)
            x = iter(signature[0])
            v = next(x,None)
            l = None
            for argument in args:
                if v==None:
                    #raise InvalidSignature(ctx.state.trace,self,*args)
                    break
                z: type[fragments.Fragment] = None
                tup = (v=="...")
                if tup:
                    z=l
                else:
                    z=v
                val = isinstance(argument,z)
                if val:
                    if not tup:
                        l=v
                        v=next(x,None)
                else:
                    if tup:
                        v=next(x,None)
                        if v!=None and isinstance(argument,v):
                            continue
                    break
            else:
                if next(x,None)==None:
                    break
        else:
            raise InvalidSignature(ctx.state.trace,self,*args)
        return signature[1](ctx,*args)
def callTrick(pattern: fragments.Pattern,ctx:Context,args:tuple[fragments.Fragment]) -> fragments.Fragment|SpellExecutor:
    trick = Trick.tricks.get(pattern)
    if trick==None:
        raise UnknownTrickBlunder(ctx.state.trace,pattern)
    return trick.activate(ctx,args)
