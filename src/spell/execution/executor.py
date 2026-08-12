from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum

from spell.blunders import Blunder
import spell.fragments as fragments

class ExecutionLimitReachedBlunder(Blunder):
    pass
MAX_DEPTH = 255

class ExecutionState:
    args: tuple[fragments.Fragment]
    delay: int
    recursions: int
    trace: list[int]
    init_trace_size: int
    def __init__(self,
                 arguments: tuple[fragments.Fragment],
                 delay:int=0,
                 recursions:int=0,
                 stacktrace:list[int]=[],
                 init_stacktrace_size:int=0):
        self.args = arguments
        self.delay = delay
        self.recursions = recursions
        self.trace = []
        self.init_trace_size = init_stacktrace_size
        self.trace.extend(stacktrace)
    def recurse(self,*args: fragments.Fragment):
        if self.recursions+1>=MAX_DEPTH:
            raise ExecutionLimitReachedBlunder(self.trace)
        state = ExecutionState(args,0,self.recursions+1,self.trace.copy())
        state.trace.append(-2)
        return state
EXEC_LIMIT = 255 #maybe?
class TickData:
    executions: int
    exec_limit: int
    killed: bool
    def __init__(self,limit: int=EXEC_LIMIT):
        self.executions = 0
        self.killed = False
        self.exec_limit = limit
    def exec_limit_reached(self):
        return self.killed or self.executions >= self.exec_limit
class Context:
    state: ExecutionState
    path: str
    data: TickData = TickData()
    def __init__(self,state: ExecutionState,path="",data=TickData()):
        self.state = state
        self.path = path
        self.data = data
class SpellExecutor(ABC):
    def single_frame_run(self,ctx: Context) -> fragments.Fragment:
        result = self.run(ctx)
        if result==None:
            raise ExecutionLimitReachedBlunder()
        return result
    @abstractmethod
    def run(self,ctx:Context) -> fragments.Fragment|None: ...
    @abstractmethod
    def run_without_context(self,path:str,tickdata:TickData): ...

class InstructType(IntEnum):
    FRAGMENT = 1
    ENTER_SCOPE = 2
    EXIT_SCOPE = 3   
    def from_id(id: int) -> InstructType:
        match id:
            case 1:
                return InstructType.FRAGMENT
            case 2:
                return InstructType.ENTER_SCOPE
            case 3:
                return InstructType.EXIT_SCOPE
            case _:
                raise IndexError("that aint an instruction")
    def __str__(self):
        return self.name
class SpellInstruction:
    type: InstructType
    fragment: fragments.Fragment|None
    def __init__(self,type: InstructType|int, fragment: fragments.Fragment = None):
        if isinstance(type,InstructType):
            self.type = type
        else:
            self.type = InstructType.from_id(type)
        self.fragment = fragment
    @classmethod
    def flatten_spell(cls,head: fragments.SpellPart) -> list[SpellInstruction]:
        instructions: list[SpellInstruction] = []
        headStack: list[fragments.SpellPart] = []
        indexStack: list[int] = []
        headStack.append(head)
        indexStack.append(-1)
        while len(headStack)>0:
            current = headStack[-1]
            currentI = indexStack.pop()
            if (currentI == -1):
                instructions.append(SpellInstruction(InstructType.EXIT_SCOPE))
                instructions.append(SpellInstruction(InstructType.FRAGMENT,current.glyph))
            currentI+=1
            if (currentI < len(current.subparts)):
                headStack.append(current.subparts[-currentI])
                indexStack.append(currentI)
                indexStack.append(-1)
            else:
                headStack.pop()
                instructions.append(SpellInstruction(InstructType.ENTER_SCOPE))
        return instructions
    @classmethod
    def decode(cls,instructs: list[SpellInstruction],rootGlyph: fragments.Fragment=None) -> fragments.SpellPart:
        pile: list[fragments.SpellPart] = []
        scope: list[int] = []
        
        while len(instructs)>0:
            inst = instructs.pop()
            match inst.type:
                case InstructType.ENTER_SCOPE:
                    scope.append(0)
                case InstructType.EXIT_SCOPE:
                    scope.pop()
                    if len(scope)>0:
                        scope[-1]+=1
                case InstructType.FRAGMENT:
                    args: list[fragments.SpellPart] = []
                    for i in range(scope[-1]):
                        args.append(pile.pop())
                    args.reverse()
                    pile.append(fragments.SpellPart(inst.fragment,args))
        if rootGlyph==None:
            return pile.pop()
        else:
            return fragments.SpellPart(rootGlyph,pile[::-1])
    def __repr__(self):
        return f"SI({self.type}{f", {self.fragment}" if self.fragment!=None else ""})"
