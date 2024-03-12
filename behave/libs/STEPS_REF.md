# Step Implementation Examples
The repo is for step implementation of some common BDD test cases and it
leverages the [requests](https://requests.readthedocs.io/en/latest/) python
library to make http request under the hood.

## Folder Structure

```Shell
├── README.md
└── behave_http
    ├── __init__.py
    ├── environment.py
    ├── steps
    │   └── __init__.py
    └── utils.py
```

## List of Predefined Steps

Given Steps 👷
--------------

- ``I am using the endpoint "{endpoint}"``
- ``I set base URL to "{base_url}"``
- ``I set "{key}" header to "{value}"``
- ``I set BasicAuth username to "{username}" and password to "{password}"``
- ``I set "{variable}" to "{value}"``
- ``I do not want to verify server certificate``
- ``a set of specific headers``
- ``a request payload template``
- ``a request payload from a file "{payload_file}"``
- ``the bad username file is "{ufile}" and password file is "{pfile}"``



When Steps ▶️
-------------

- ``I make a HEAD request to "{url_path_segment}"``
- ``I make an OPTIONS request to "{url_path_segment}"``
- ``I make a TRACE request to "{url_path_segment}"``
- ``I make a PATCH request to "{url_path_segment}"``
- ``I make a PUT request to "{url_path_segment}"``
- ``I make a POST request to "{url_path_segment}"``
- ``I make a login request to "{url_path_segment}" with bad username and password``
- ``I make a GET request to "{url_path_segment}"``
- ``I make a DELETE request to "{url_path_segment}"``



Then Steps ✔️
-------------

- ``the variable "{variable}" should be "{valur}"``
- ``the response status should be one of "{statuses}"``
- ``the response status should be "{status}"``
- ``the response body should contain "{content}"``
- ``the "{key}" header should be "{value}"``
- ``the value of header "{value}" should be in the given set``
- ``the protocol of login URL should be https``
- ``the value of header "{value}" should contain the defined value in the given set``
- ``the response body should be json format``
- ``the value of field "{key}" should be "{value}"``
