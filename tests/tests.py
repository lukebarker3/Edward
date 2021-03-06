import requests, unittest
from http import HTTPStatus

BASE_URL = "http://localhost:5000"

# when writing tests, assert the structure of the responses, rather than actual data


class AlgorithmListControllerTests(unittest.TestCase):
    def test_get(self):
        # given no parameters
        # when performing a GET to /api/algorithms
        response_with_http = requests.get(f"{BASE_URL}/api/algorithms")
        response = response_with_http.json()

        # then expect HTTP 200 OK - list of available algorithm keys
        self.assertTrue(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.OK)
        correct_key = "available_algorithms"
        self.assertTrue(correct_key in response.keys())
        self.assertTrue(type(response[correct_key]) is list)
        self.assertTrue(len(response[correct_key]) > 0)
        self.assertTrue(all([type(entry).__name__ == "str" for entry in response[correct_key]]))


class AlgorithmTypesControllerTests(unittest.TestCase):
    def test_get_valid_arg(self):
        # given valid algorithm type key
        algorithm_type_to_use = "sorting"

        # when performing a GET to /api/algorithmType/<algorithm_type>
        response_with_http = requests.get(f"{BASE_URL}/api/algorithmType/{algorithm_type_to_use}")
        response = response_with_http.json()

        # then expect list of available algorithm keys of that type
        self.assertTrue(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.OK)
        self.assertTrue(type(response) is dict)
        self.assertTrue(len(response.keys()) > 0)
        self.assertTrue(all([type(key).__name__ == "str" for key in response.keys()]))
        self.assertTrue(all([type(val).__name__ == "str" for val in response.values()]))

    def test_get_no_args(self):
        # given no args
        # when performing a GET to /api/algorithmType
        response_with_http = requests.get(f"{BASE_URL}/api/algorithmType")

        # then expect HTTP 404 response
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.NOT_FOUND)

    def test_get_invalid_arg(self):
        # given invalid algorithm type key
        invalid_key = "abcdefg"

        # when performing a GET to /api/algorithmType/<algorithm_type>
        response_with_http = requests.get(f"{BASE_URL}/api/algorithmType")
        response = response_with_http.json()

        # then expect HTTP 400 response
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)
        self.assertEqual(response["message"], f"Algorithm type '{invalid_key}' does not exist within the API.")


class AlgorithmControllerTests(unittest.TestCase):
    def test_get_valid_arg_available(self):
        # given valid algorithm key
        available_key = "insertion-sort"

        # when performing a GET to /api/algorithms/<algorithm_key>
        response_with_http = requests.get(f"{BASE_URL}/api/algorithms/{available_key}")
        response = response_with_http.json()

        # if algorithm is available
        # then expect HTTP 200 OK - algorithm JSON metadata
        self.assertTrue(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.OK)

    def test_get_valid_arg_unavailable(self):
        # given valid algorithm key
        unavailable_key = "dummy-unavailable-alg"
        
        # when performing a GET to /api/algorithms/<algorithm_key>
        response_with_http = requests.get(f"{BASE_URL}/api/algorithms/{unavailable_key}")
        response = response_with_http.json()
        
        # if algorithm is unavailable
        # then expect HTTP 501 NOT IMPLEMENTED
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.NOT_IMPLEMENTED)

    def test_get_invalid_arg(self):
        # given invalid algorithm key
        invalid_key = "some-weird-key-asdf"
        
        # when performing a GET to /api/algorithms/<algorithm_key>
        response_with_http = requests.get(f"{BASE_URL}/api/algorithms/{invalid_key}")
        response = response_with_http.json()
        
        # then expect HTTP 404 response
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.NOT_FOUND)

    def test_post_not_implemented(self):
        # given valid POST request
        not_implemented_key = "dummy-unavailable-arg"
        req = {}
        
        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{not_implemented_key}", json=req)
        response = response_with_http.json()
        
        # then expect HTTP 501
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.NOT_IMPLEMENTED)

    def test_post_no_action(self):
        # given POST request with no 'action' entry in JSON
        algorithm_key = "insertion-sort"
        req = { collection: [] }

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        response = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_pot_invalid_action(self):
        # given POST request with invalid 'action' entry in JSON
        algorithm_key = "insertion-sort"
        req = { collection: [], action: "fake" }

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        repsonse = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_post_invalid_min_size(self):
        # given POST request with invalid 'min_size' entry in 'options' JSON
        algorithm_key = "insertion-sort"
        req = { collection: [], action: "test", options: { min_size: -2 } }

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        repsonse = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_post_min_greater_than_max(self):
        # given POST request where 'min_size' is bigger than 'max_size'
        algorithm_key = "insertion-sort"
        req = { collection: [], action: "test", options: { min_size: 10, max_size: 8 } }

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        repsonse = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_post_invalid_jump(self):
        # given POST request with invalid 'jump' entry in 'options' JSON
        algorithm_key = "insertion-sort"
        req = { collection: [], action: "test", options: { jump: 0 } }

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        repsonse = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_post_invalid_repeats(self):
        # given POST request with invalid 'repeats' entry in 'options' JSON
        algorithm_key = "insertion-sort"
        req = { collection: [], action: "test", options: { repeats: 0 } }

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        repsonse = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_post_algorithm_type(self):
        # given POST request comparing two algorithms which solve different problems
        first = "insertion-sort"
        second = "binary-search"

        # when performing a POST to /api/algorithms/<algorithm_key>
        response_with_http = requests.post(f"{BASE_URL}/api/algorithms/{algorithm_key}", json=req)
        repsonse = response_with_http.json()

        # then expect HTTP 400
        self.assertFalse(response_with_http.ok())
        self.assertTrue(response_with_http.status_code == HTTPStatus.BAD_REQUEST)

    def test_post_valid_request_run(self):
        # given valid post body with 'run' action
        # when performing a POST to /api/algorithms/<algorithm_key>
        # then expect HTTP 200 OK - experiment result
        pass

    def test_post_valid_request_test(self):
        # given valid post body with 'test' action
        # when performing a POST to /api/algorithms/<algorithm_key>
        # then expect HTTP 200 OK - experiment result
        pass

    def test_post_valid_request_compare(self):
        # given valid post body with 'compare' action
        # when performing a POST to /api/algorithms/<algorithm_key>
        # then expect HTTP 200 OK - experiment result
        pass

if __name__ == "__main__":
    unittest.main()
