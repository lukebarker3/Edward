from flask_restful import Resource, abort, reqparse
from flask import send_file
import os
import random
from typing import Dict

from scripts.Sorts import *
from scripts.Chart import CompareChart, TestChart
from config import ROOT_DIR

sorts = {
    "insertion-sort":          InsertionSort,
    "selection-sort":          SelectionSort,
    "optimised-bubble-sort":   OptimisedBubbleSort,
    "traditional-bubble-sort": TraditionalBubbleSort,
    "recursive-quick-sort":    RecursiveQuickSort,
    "iterative-quick-sort":    IterativeQuickSort,
    "top-down-merge-sort":     TopDownMergeSort,
    "bottom-up-merge-sort":    BottomUpMergeSort,
    "heap-sort":               HeapSort,
    "shell-sort":              ShellSort,
    "counting-sort":           CountingSort,
    "bucket-sort":             BucketSort
}

algorithmmap = {**sorts} # type: Dict[str, Algorithm]


class AlgorithmListController(Resource):
    def get(self):
        return {
            "available_algorithms": list(algorithmmap.keys())
        }, 200


class AlgorithmController(Resource):
    valid_actions = [
        "run",
        "test",
        "compare"
    ]

    def check_algorithm_exists(self, algorithmname):
        if algorithmname not in algorithmmap.keys():
            abort(404, message="Algorithm '{}' doesn't exist.".format(algorithmname))

        return True

    def get(self, algorithmname):
        """
        Algorithm metadata - space complexity, time complexity, description etc.
        """

        self.check_algorithm_exists(algorithmname)

        try:
            return algorithmmap[algorithmname].metadata(), 200
        except NotImplementedError:
            abort(501, message="There is no metadata available for the {} algorithm.".format(algorithmname))

    def post(self, algorithmname):
        """
        Runs the algorithm on a set of data.
        """

        self.check_algorithm_exists(algorithmname)

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("action", type=str, required=True)
        parser.add_argument("makegraph", type=bool, default=False, store_missing=True)
        parser.add_argument("options", type=dict, default=dict(), store_missing=True)
        parser.add_argument("collection", type=dict, required=False, store_missing=True)
        parser.add_argument("first_algorithm", type=str, required=False, store_missing=False)
        parser.add_argument("second_algorithm", type=str, required=False, store_missing=False)

        # contains all post data from request
        args = parser.parse_args()

        action = args['action']

        if action == "":
            abort(400, message="No action specified.")
        else:
            if action not in AlgorithmController.valid_actions:
                abort(400, message="Invalid action '{}'".format(action))

            default_options = {
                'min_size': 5,
                'max_size': 20,

                'jump': 1,
                'repeats': 5
            }

            # use pure default options if no options are provided
            options_not_provided = args['options'] is None or args['options'] == {}
            options = default_options if options_not_provided else {**default_options, **args['options']}

            # don't make graph unless specified otherwise
            makegraph = False if args['makegraph'] is None else args['makegraph']

            if action == "run":
                algorithm = algorithmmap[algorithmname](args['collection'])
                algorithm.run()
                return algorithm.__dict__(), 200

            if action == "test":
                # Uncomment during controller debugging
                #abort(503, message="The {} action is not available.".format(action))
                min_size = options['min_size'] # TODO must be at least 5
                max_size = options['max_size'] # TODO must be at least 10
                jump     = options['jump'] # TODO must be at least 1
                #repeats = options['repeats'] # TODO must be at least 3

                algorithm_results = {}
                algorithm_results_json = {}

                for size in range(min_size, max_size + 1, jump):
                    results_for_this_size = []
                    results_for_this_size_json = []

                    repeats = options['repeats'] # TODO must be at least 3

                    while repeats > 0:
                        # get algorithm class from map, instantiate and run
                        algorithm = algorithmmap[algorithmname](size=size)
                        algorithm.run()

                        results_for_this_size.append(algorithm)
                        results_for_this_size_json.append(algorithm.__dict__())
                        repeats -= 1

                    algorithm_results.update({size: results_for_this_size})
                    algorithm_results_json.update({size: results_for_this_size_json})

                if makegraph is True:
                    algorithm_results_json['graph'] = TestChart.new(algorithm_results)
                else:
                    algorithm_results_json['graph'] = None

                return algorithm_results_json, 200

            if action == "compare":
                # check if two algorithm's solve the same problem
                first_algorithm_class = algorithmmap[args['first_algorithm']]
                second_algorithm_class = algorithmmap[args['second_algorithm']]
                try:
                    repeats = args['options']['repeats']
                except:
                    repeats = 10

                if first_algorithm_class.__base__ is not second_algorithm_class.__base__:
                    abort(400, message="The two algorithms do not solve the same computational problem!")
                else:
                    if args['collection'] is None or args['collection'] == []:
                        min_size = options['min_size'] # TODO must be at least 5
                        max_size = options['max_size'] # TODO must be at least 10

                        size_to_use = random.randint(min_size, max_size)

                        first_algorithm = first_algorithm_class(size=size_to_use)

                        # get generated collection from first algorithm
                        # avoids second algorithm generating another one
                        # keeps experiment fair
                        collection_to_use = first_algorithm.oldcollection
                    else:
                        collection_to_use = args["collection"]

                    first_results = []
                    first_results_json = []
                    second_results = []
                    second_results_json = []

                    while repeats > 0:
                        first_algorithm = first_algorithm_class(data=collection_to_use)
                        second_algorithm = second_algorithm_class(data=collection_to_use)

                        first_algorithm.run()
                        second_algorithm.run()

                        first_results.append(first_algorithm)
                        second_results.append(second_algorithm)

                        first_results_json.append(first_algorithm.__dict__())
                        second_results_json.append(second_algorithm.__dict__())

                        repeats -= 1

                    results = {
                        "first_algorithm": {
                            "name": args["first_algorithm"],
                            "result": first_results
                        },
                        "second_algorithm": {
                            "name": args["second_algorithm"],
                            "result": second_results
                        }
                    }

                    results_json = {
                        "first_algorithm": {
                            "name": args["first_algorithm"],
                            "result": first_results_json
                        },
                        "second_algorithm": {
                            "name": args["second_algorithm"],
                            "result": second_results_json
                        }
                    }

                    if makegraph is True:
                        results_json['graph'] = CompareChart.new(results)
                    else:
                        results_json['graph'] = None

                    return results_json, 200


class GraphController(Resource):
    def get(self, graphid):
        return send_file(os.path.join(ROOT_DIR, "images/graphs/", graphid + ".png"), mimetype="image/png")
