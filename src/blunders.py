class Blunder(Exception):
    def __str__(self):
        return f"Spell Blundered!"
class ArithmeticBlunder(Blunder):
    def __str__(self):
        return "Incompatible Types"
