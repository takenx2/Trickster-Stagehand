import spell.fragments as fragments
from spell.execution.executor import ExecutionState, SpellExecutor,SpellInstruction,InstructType
from spell.trick.tricks import callTrick


class DefaultSpellExecutor(SpellExecutor):
    def __init__(self,root: fragments.SpellPart):
        self.root = root
        self.instructions: list[SpellInstruction] = SpellInstruction.flatten_spell(root)
        self.inputs: list[fragments.Fragment] = []
        self.scope: list[int] = []
        self.state = ExecutionState([])
        self.child: SpellExecutor|None = None
    def run(self, ctx=None) -> fragments.Fragment|None:
    #   print(len(self.root.subparts))
        if self.child!=None:
            if self.runChild(ctx)==None:
                return None
        while True:
            if self.state.delay>0:
                self.state.delay-=1
                return None
            if self.state.exec_limit_reached():
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
                        return self.inputs.pop()
                    else:
                        pass
                    self.scope.append(self.scope.pop()+1)
                case _:
                    frag = instruct.fragment
                    frag.activate()
    def runChild(self,ctx: None) -> bool:
        result = self.child.run(ctx)
        if result == None:
            return False
        self.child = None
        self.inputs.append(result)
        return True