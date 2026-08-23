from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from spell.blunders import Blunder
import spell.fragments as fragments
from pathlib import Path
MAX_DEPTH = 255
EXEC_LIMIT = 255 #maybe?


class ExecutionLimitReachedBlunder(Blunder):
    pass
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
                 stacktrace:list[int]=[]):
        self.args = arguments
        self.delay = delay
        self.recursions = recursions
        self.trace = []
        self.init_trace_size = len(stacktrace)
        self.trace.extend(stacktrace)
    def recurse(self,*args: fragments.Fragment) -> ExecutionState:
        if self.recursions+1>=MAX_DEPTH:
            raise ExecutionLimitReachedBlunder(self.trace)
        state = ExecutionState(args,0,self.recursions+1,self.trace.copy())
        state.trace.append(-2)
        return state
    def unrecurse(self):
        self.recursions -= 1
        while len(self.trace)>=max(self.init_trace_size,-1):
            self.trace.pop()
class ExecFrameData:
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
    data: ExecFrameData
    def __init__(self,state: ExecutionState,cwd=Path(),data=ExecFrameData()):
        self.state = state
        self.path = Path()
        self._cwd = cwd
        self.data = data
    def get_path(self) -> Path:
        return self.path.relative_to(self._cwd)
class SpellInstruction:
    class Type(IntEnum):
        FRAGMENT = 1
        ENTER_SCOPE = 2
        EXIT_SCOPE = 3   
        @classmethod
        def from_id(cls,id: int) -> SpellInstruction.Type:
            match id:
                case 1:
                    return cls.FRAGMENT
                case 2:
                    return cls.ENTER_SCOPE
                case 3:
                    return cls.EXIT_SCOPE
                case _:
                    raise IndexError("that aint an instruction")
        def __str__(self):
            return self.name
    type: Type
    fragment: fragments.Fragment|None
    def __init__(self,type: Type|int, fragment: fragments.Fragment = None):
        if isinstance(type,SpellInstruction.Type):
            self.type = type
        else:
            self.type = SpellInstruction.Type.from_id(type)
        self.fragment = fragment
    @classmethod
    def flatten_spell(cls,head: fragments.SpellPart) -> list[SpellInstruction]:
        instructions: list[SpellInstruction] = []
        headStack: list[fragments.SpellPart] = []
        i=0
        indexStack: list[int] = []
        headStack.append(head)
        indexStack.append(-1)
        while len(headStack)>0:
            current = headStack[-1]
            currentI = indexStack.pop()
            if (currentI == -1):
                instructions.append(SpellInstruction(SpellInstruction.Type.EXIT_SCOPE))
                instructions.append(SpellInstruction(SpellInstruction.Type.FRAGMENT,current.glyph))
            currentI+=1
            if (currentI < len(current.subparts)):
                headStack.append(current.subparts[-currentI])
                indexStack.append(currentI)
                indexStack.append(-1)
            else:
                headStack.pop()
                instructions.append(SpellInstruction(SpellInstruction.Type.ENTER_SCOPE))
        return instructions
    @classmethod
    def decode(cls,instructs: list[SpellInstruction],rootGlyph: fragments.Fragment=None) -> fragments.SpellPart:
        pile: list[fragments.SpellPart] = []
        scope: list[int] = []
        
        while len(instructs)>0:
            inst = instructs.pop()
            match inst.type:
                case SpellInstruction.Type.ENTER_SCOPE:
                    scope.append(0)
                case SpellInstruction.Type.EXIT_SCOPE:
                    scope.pop()
                    if len(scope)>0:
                        scope[-1]+=1
                case SpellInstruction.Type.FRAGMENT:
                    args: list[fragments.SpellPart] = []
                    for i in range(scope[-1]):
                        args.append(pile.pop())
                    args.reverse()
                    pile.append(fragments.SpellPart(inst.fragment,args))
        if rootGlyph==None:
            return pile.pop()
        else:
            return fragments.SpellPart(rootGlyph,*pile)
    def __repr__(self):
        return f"SI({self.type}{f", {self.fragment}" if self.fragment!=None else ""})"

class SpellExecutor(ABC):
    def single_frame_run(self,ctx: Context) -> fragments.Fragment:
        result = self.run(ctx)
        if result==None:
            raise ExecutionLimitReachedBlunder()
        return result
    @abstractmethod
    def run(self,path:str,execFDat:ExecFrameData) -> fragments.Fragment|None: ...
    @abstractmethod
    def get_last_executions(self) -> int: ...
    @abstractmethod
    def get_deepest_state(self) -> int: ...
class DefaultSpellExecutor(SpellExecutor):
    def __init__(self,root: fragments.SpellPart,state: ExecutionState=ExecutionState([])):
        self.root = root
        self.instructions: list[SpellInstruction] = SpellInstruction.flatten_spell(root)
        self.inputs: list[fragments.Fragment] = []
        self.scope: list[int] = []
        self.state = state
        self.child: SpellExecutor|None = None
        self.last_executions = 0
        self.overrideReturn: fragments.Fragment = None
    def run(self,path:Path,execFDat:ExecFrameData=ExecFrameData()):
        ctx = Context(self.state,path,execFDat)
        if self.child!=None:
            if not self.run_child(ctx):
                return None
        while True:
            if self.state.delay>0:
                self.state.delay-=1
                return None
            if ctx.data.exec_limit_reached():
                return None
            instruct = self.instructions.pop()
            match instruct.type:
                case SpellInstruction.Type.ENTER_SCOPE:
                    if len(self.scope)>0:
                        self.state.trace.append(self.scope[-1])
                    self.scope.append(0)
                case SpellInstruction.Type.EXIT_SCOPE:
                    self.scope.pop()
                    if len(self.scope)==0:
                        if self.overrideReturn!=None:
                            return self.overrideReturn
                        elif len(self.inputs)>0:
                            return self.inputs.pop()
                        else:
                            return None
                    self.scope.append(self.scope.pop()+1)
                case _:
                    frag = instruct.fragment
                    x = self.scope[-1]
                    args = []
                    for i in range(x):
                        args.append(self.inputs.pop())
                    args = args[::-1]
                    result = frag.activate(ctx,args)
                    if isinstance(result,SpellExecutor):
                        is_tail = True
                        ret_value: fragments.Fragment = None
                        if len(self.instructions)>1:
                            for instruction in self.instructions:
                                if instruction.type == SpellInstruction.Type.EXIT_SCOPE:
                                    continue
                                if (instruction.type == SpellInstruction.Type.FRAGMENT 
                                and isinstance(instruction.fragment,fragments.PatternGlyph) 
                                and instruction.fragment.pattern.is_empty()):
                                    ret_value = fragments.VoidFragment()
                                    continue
                                is_tail = False
                                break
                        if is_tail and isinstance(result,DefaultSpellExecutor):
                            
                            self.instructions = result.instructions
                            self.inputs = []
                            self.scope = []
                            if self.overrideReturn==None:
                                self.overrideReturn = ret_value
                            self.state = result.state
                            self.state.unrecurse()
                            ctx = Context(self.state,ctx.path,ctx.data)
                        else:
                            self.child = result
                            if not self.run_child(ctx):
                                return None
                    else:
                        self.inputs.append(result)
            ctx.data.executions+=1
            self.last_executions = ctx.data.executions
    def run_child(self,ctx: Context) -> bool:
        result = self.child.run(ctx.path,ctx.data)
        if result == None:
            return False
        self.child = None
        self.inputs.append(result)
        return True
    def get_last_executions(self):
        if self.child:
            return self.child.get_last_executions()
        return self.last_executions
    def get_deepest_state(self):
        if self.child:
            return self.child.get_deepest_state()
        return self.state
class FoldingExecutor(SpellExecutor):
    def __init__(self,context:Context,spell:fragments.SpellPart,result:fragments.Fragment,values:list[fragments.Fragment],keys:list[fragments.Fragment],folding:fragments.Fragment):
        super().__init__()
        self.state:ExecutionState = context.state.recurse(())
        self.spell: fragments.SpellPart = spell
        self.last: fragments.Fragment = result
        self.values: list[fragments.Fragment] = values
        self.keys: list[fragments.Fragment] = keys
        self.folding: fragments.Fragment = folding
        self.child: SpellExecutor|None = None
        self.last_executions = 0
        assert len(values)==len(keys),"Values and Keys must be equal length!"
    def run(self, path, execFDat=ExecFrameData()):
        ctx = Context(self.state,path,exec)

        self.last_executions = 0
        if self.child!=None:
            result = self.run_child(ctx)
            if result==None:
                return None
        size = len(self.values)
        for i in range(size):
            if ctx.data.exec_limit_reached():
                return None
            self.child = DefaultSpellExecutor(self.spell,self.state.recurse(
                self.last,
                self.values.pop(),
                self.keys.pop(),
                self.folding
            ))
            result = self.run_child(ctx)
            if result==None:
                return None
            ctx.data.executions += 1
            self.last_executions = ctx.data.executions
    def run_child(self,ctx:Context) -> fragments.Fragment:
        result = self.child.run(ctx.path,ctx.data)
        if result!=None:
            self.last = result
            self.child = None
        return result
    def get_last_executions(self):
            if self.child:
                return self.child.get_last_executions()
            return self.last_executions
    def get_deepest_state(self):
        if self.child:
            return self.child.get_deepest_state()
        return self.state
from io import StringIO
from select import select
class ReadBufferExecutor(SpellExecutor):
    def __init__(self,state:ExecFrameData,buffer: StringIO,timeout:int=0,fallback=None):
        self.state = state
        self.buffer = buffer
        self.timeleft = timeout+1 if timeout>0 else timeout
        self.fallback = fallback if fallback!=None else fragments.VoidFragment()
    def run(self, path, execFDat):
        if self.timeleft == 0:
            return self.fallback
        result = None
        if select([self.buffer],[],[],0)[0]:
            result = self.buffer.readline().strip()
        if result!=None:
            return fragments.StringFragment(result)
        if self.timeleft>0:
            self.timeleft-=1
        return None
    def get_deepest_state(self):
        return self.state
    def get_last_executions(self):
        return 0