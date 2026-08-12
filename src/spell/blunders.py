class Blunder(Exception):
    trace: list[int]
    def __init__(self, trace: list[int]):
        self.trace = trace
    def __str__(self):
        return f"Spell Blundered! at {self.format_trace()}"
    def format_trace(self):
        result = None
        for t in self.trace:
            if result == None:
                result = ""
            else:
                result += ":"
            match t:
                case -1:
                    result += ">"
                case -2:
                    result += "#"
                case -3:
                    result += "&"
                case _:
                    result += str(t)
        return result
class ArithmeticBlunder(Blunder):
    def __init__(self, trace):
        super().__init__(trace)
    def __str__(self):
        return f"Incompatible Types @{self.format_trace()}"
