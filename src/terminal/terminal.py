import subprocess

"""
    Provide an executor
"""


class Terminal:
    def __init__(self):
        pass

    def ExecuteCommand(self, command: str):
        return subprocess.run(command, shell=True, check=True)
