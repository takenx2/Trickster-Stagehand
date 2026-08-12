import spell.fragments as fragments
from spell.execution.executor import ExecutionState, SpellExecutor,SpellInstruction,InstructType,Context,TickData


class DefaultSpellExecutor(SpellExecutor):
    def __init__(self,root: fragments.SpellPart,state: ExecutionState=ExecutionState([])):
        self.root = root
        self.instructions: list[SpellInstruction] = SpellInstruction.flatten_spell(root)
        self.inputs: list[fragments.Fragment] = []
        self.scope: list[int] = []
        self.state = state
        self.child: SpellExecutor|None = None
        self.overrideReturn: fragments.Fragment = None
    def run_without_context(self,path:str,tickdata:TickData):
        return self.run(Context(self.state,path,tickdata))
    def run(self, ctx:Context) -> fragments.Fragment|None:
    #   print(len(self.root.subparts))
        if self.child!=None:
            if not self.runChild(ctx):
                return None
        while True:
            if self.state.delay>0:
                self.state.delay-=1
                return None
            if ctx.data.exec_limit_reached():
                return None
            instruct = self.instructions.pop()
            match instruct.type:
                case InstructType.ENTER_SCOPE:
                    if len(self.scope)>0:
                        self.state.trace.append(self.scope[-1])
                    self.scope.append(0)
                case InstructType.EXIT_SCOPE:
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
                                if instruction.type == InstructType.EXIT_SCOPE:
                                    continue
                                if (instruction.type == InstructType.FRAGMENT 
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
                            self.state.recursions -= 1
                            ctx = Context(self.state,ctx.path,ctx.data)
                        else:
                            self.child = result
                            if not self.runChild(ctx):
                                return None
                    else:
                        self.inputs.append(result)
            ctx.data.executions+=1
    def runChild(self,ctx: Context) -> bool:
        result = self.child.run_without_context(ctx.path,ctx.data)
        if result == None:
            return False
        self.child = None
        self.inputs.append(result)
        return True