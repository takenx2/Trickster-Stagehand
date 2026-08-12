from __future__ import annotations
import spell.fragments as fragments
from spell.execution.executor import ExecutionState, SpellExecutor,Context
from typing import Literal
from collections.abc import Callable
from spell.blunders import Blunder


class SignatureBlunder(Blunder):
    trick: Trick
    inputs: tuple[fragments.Fragment]
    def __init__(self, trick,*inputs):
        self.trick = trick
        self.inputs = inputs
    def __str__(self):
        e = ""
        for inp in self.inputs:
            e+=inp.plain_name+", "
        return f'Invalid inputs for spell "{self.trick.name}": ({e[:-2]})'
class UnknownTrickBlunder(Blunder):
    pattern: Pattern
    def __init__(self, pattern: Pattern):
        self.pattern = pattern
    def __str__(self):
        return f"Unknown Trick with pattern: {self.pattern}"
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
                    raise SignatureBlunder(self)
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
            raise SignatureBlunder(self,*args)
        return signature[1](ctx,*args)
def callTrick(pattern: fragments.Pattern,ctx:Context,args:tuple[fragments.Fragment]) -> fragments.Fragment|SpellExecutor:
    trick = Trick.tricks.get(pattern)
    if trick==None:
        for p in Trick.tricks.keys():
            print(p.toInt()==pattern.toInt())
        raise UnknownTrickBlunder(pattern)
    return trick.activate(ctx,args)
