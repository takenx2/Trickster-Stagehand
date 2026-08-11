from __future__ import annotations
from abc import ABC, abstractmethod
from enum import IntEnum

from spell.blunders import Blunder
import spell.fragments as fragments

class ExecutionLimitReacheBlunder(Blunder):
    pass
EXEC_LIMIT = 255

class ExecutionState:
    args: list[Fragment]
    directory: str
    delay: int
    executions: int
    trace: list[int]
    init_trace_size: int
    def __init__(self,
                 arguments: list[Fragment],
                 delay:int=0,
                 executions:int=0,
                 recursions:int=0,
                 stacktrace:list[int]=[],
                 init_stacktrace_size:int=0,
                 directory:str=None,):
        self.args = arguments
        self.directory = directory
        self.delay = delay
        self.executions = executions
        self.trace = []
        self.init_trace_size = init_stacktrace_size
        self.trace.extend(stacktrace)
    def exec_limit_reached(self) -> bool:
        return self.executions > EXEC_LIMIT
class SpellExecutor(ABC):
    def single_frame_run(self,ctx: ExecutionState) -> Fragment:
        result = self.run(ctx)
        if result==None:
            raise ExecutionLimitReacheBlunder()
        return result
    @abstractmethod
    def run(self,ctx:ExecutionState) -> Fragment|None: ...

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
