# Copyright (c) 2020 Aalto University. All rights reserved.

import json
from pathlib import Path

from SolutionInstance import SolutionInstance
from DataInstance import DataInstance
OUTPUT_DIR = "results/"


def save_to_json(data: DataInstance, solution: SolutionInstance):
    layouts = {
        'layouts': [
            solution_to_layout(data, solution)
        ]
    }
    print("About to dump file")
    solution_filename = data.inputFile + "_" + str(solution.solNo) + ".json"

    Path(OUTPUT_DIR).mkdir(exist_ok=True, parents=True)
    with open(OUTPUT_DIR + solution_filename, "w") as write_file:
        json.dump(layouts, write_file)


def solution_to_layout(data: DataInstance, solution: SolutionInstance):
    thislayout = {
        'objectiveValue': solution.objVal,
        'canvasWidth': data.canvasWidth,
        'canvasHeight': data.canvasHeight,
        'id': solution.solNo,
        'elements': []
    }
    for x, y, w, l, el in zip(solution.X, solution.Y, solution.W, solution.L, data.elements):
        thislayout['elements'].append({
            'x': x,
            'y': y,
            'width': w,
            'height': l,

            'id': el.id,
            'type': el.elementType,
            'fillColorRedValue': el.redValue,
            'fillColorGreenValue': el.greenValue,
            'fillColorBlueValue': el.blueValue,
            'isLocked': el.isLocked,
        })
    return thislayout
