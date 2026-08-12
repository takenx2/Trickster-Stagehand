class Blunder(Exception):
    trace: list[int]
    def __init__(self, trace: list[int]):
        self.trace = trace
    def __str__(self):
        return "Blundered:"
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
