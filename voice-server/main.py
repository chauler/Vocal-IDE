import os
import copilot
from copilot import copilot_listen
from basic_listen import basic_listen
from compile_listen import compile_listen

mode = os.environ.get("MODE", "OTHER")

if __name__ == "__main__":
    if mode == "COPILOT":
        copilot.watch_authentication(copilot_listen)
        copilot.authenticate()
    elif mode == "COMPILER":
        compile_listen(r"x assign 5 if x equals 3 var assign y greater equals x divide 5 plus sampleVariable x assign 10 equals 5 return z end return x")
    elif mode == "OTHER":
        basic_listen()
