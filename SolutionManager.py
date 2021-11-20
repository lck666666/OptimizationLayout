# Copyright (c) 2020 Aalto University. All rights reserved.

from SolutionInstance import SolutionInstance
from JSONExportUtility import save_to_json
from DataInstance import DataInstance
from PlotUtils import draw_solution

class SolutionManager:
    def __init__(self):
        self.solution_hashes = set()
        self.solution_callbacks = []

    def build_new_solution(self, data: DataInstance, solNo, objValue, Xval, Yval, Lval, Wval):
        sol_hash = hash((str(Xval), str(Yval), str(Lval), str(Wval)))  # hash a tuple
        if sol_hash in self.solution_hashes:
            print("** Neglecting a repeat solution **")
            return
        else:
            self.solution_hashes.add(sol_hash)

            solution = SolutionInstance(objValue, Xval, Yval, Lval, Wval, solNo)
            for cb in self.solution_callbacks:
                cb(data, solution)

    def add_solution_handler(self, cb):
        assert callable(cb)
        self.solution_callbacks.append(cb)

    def sol_count(self) -> int:
        return len(self.solution_hashes)


def json_handler(data: DataInstance, solution: SolutionInstance):
    save_to_json(data, solution)


def plot_handler(data: DataInstance, solution: SolutionInstance):
    draw_solution(data, solution)
