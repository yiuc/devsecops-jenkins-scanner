"""Reasonably complete set of BDD steps for testing a simple HTTP service.

Some state is set-up and shared between steps using the context variable. It is
reset at the start of every scenario by environment.before_scenario.

"""
from __future__ import unicode_literals
import behave
import json
from ensure import ensure
import requests
import time
import os
import pickle
import jinja2
from itertools import product
from six.moves import urllib

from behave_http.utils import (
    dereference_step_parameters_and_data,
    append_path,
    filename_generator,
)

FEATURE_DIR = f"{os.getcwd()}/features"
DATA_DIR = f"{FEATURE_DIR}/data"


def get_requests(context):
    try:
        return context.session
    except AttributeError:
        context.session = requests.Session()
    return context.session


@behave.given('I am using the endpoint "{endpoint}"')
@dereference_step_parameters_and_data
def using_server(context, endpoint):
    context.endpoint = endpoint


@behave.given('I set base URL to "{base_url}"')
@dereference_step_parameters_and_data
def set_base_url(context, base_url):
    parse_res = urllib.parse.urlparse(context.endpoint)
    if not parse_res.scheme:
        raise AttributeError("$APP_URL should contain protocol! Such as https://")
    context.endpoint = urllib.parse.urljoin(context.endpoint, base_url)


@behave.given('I set "{key}" header to "{value}"')
@dereference_step_parameters_and_data
def set_header(context, key, value):
    # We must keep the headers as implicit ascii to avoid encoding failure when
    # the entire HTTP body is constructed by concatenating strings.
    context.headers[key.encode("ascii")] = value.encode("ascii")


@behave.given('I set BasicAuth username to "{username}" and password to "{password}"')
@dereference_step_parameters_and_data
def set_basic_auth_headers(context, username, password):
    context.auth = (username, password)


@behave.given('I set variable "{variable}" to {value}')
@dereference_step_parameters_and_data
def set_var(context, variable, value):
    # setattr(context, variable, json.loads(value))
    context.template_data[variable] = json.loads(value)


@behave.given("I do not want to verify server certificate")
@dereference_step_parameters_and_data
def do_not_verify_ssl(context):
    context.verify_ssl = False


@behave.given("a request payload template")
@dereference_step_parameters_and_data
def receive_request_payload(context):
    data = context.text
    # return type string
    context.data = jinja2.Template(data).render(context.template_data)


@behave.given('a request payload from a file "{pfile}"')
@dereference_step_parameters_and_data
def receive_payload_file(context, pfile):
    payload_file = f"{DATA_DIR}/{pfile}"
    with open(payload_file, "r") as pf:
        res = jinja2.Template(pf.read()).render(context.template_data)
        # return type dict
        context.data = json.loads(res)


@behave.given("a set of specific headers")
@dereference_step_parameters_and_data
def receive_header_definition(context):
    # data structure is { key -> [value_a, value_b...]}
    context.db_header = dict()
    for row in context.table:
        if row["key"] not in context.db_header:
            context.db_header.update({row["key"]: [row["value"].encode("ascii")]})
        else:
            context.db_header[row["key"]].append(row["value"].encode("ascii"))


@behave.given('the bad username file is "{ufile}" and password file is "{pfile}"')
@dereference_step_parameters_and_data
def load_weak_credentials(context, ufile, pfile):
    context.creds_file = filename_generator() + ".pkl"
    username_file = f"{DATA_DIR}/{ufile}"
    password_file = f"{DATA_DIR}/{pfile}"
    with open(username_file, "r") as du, open(password_file, "r") as pf:
        creds_tuple = [(username, password) for username, password in product(du, pf)]
        with open(context.creds_file, "wb") as pkl:
            pickle.dump(creds_tuple, pkl)


@behave.when('I make a HEAD request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def head_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).head(
        url, headers=context.headers, auth=context.auth, verify=context.verify_ssl
    )


@behave.when('I make an OPTIONS request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def options_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).options(
        url, headers=context.headers, auth=context.auth, verify=context.verify_ssl
    )


@behave.when('I make a TRACE request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def trace_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).request(
        "TRACE",
        url,
        headers=context.headers,
        auth=context.auth,
        verify=context.verify_ssl,
    )


@behave.when('I make a PATCH request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def patch_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).patch(
        url,
        data=context.data,
        headers=context.headers,
        auth=context.auth,
        verify=context.verify_ssl,
    )


@behave.when('I make a PUT request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def put_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).put(
        url,
        data=context.data,
        headers=context.headers,
        auth=context.auth,
        verify=context.verify_ssl,
    )


@behave.when('I make a POST request to "{url_path_segment}"')
def post_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    if isinstance(context.data, bytes):
        context.data = context.data.decode("utf-8")
    # if isinstance(context.data, str):
    #     context.data = json.loads(context.data)
    # Form-encode mode
    # "form": {
    #   "key2": "value2",
    #   "key1": "value1"
    # },
    context.response = get_requests(context).post(
        url,
        json=context.data,
        headers=context.headers,
        verify=context.verify_ssl,
        auth=context.auth,
    )


@behave.when(
    'I make a login request to "{url_path_segment}" with bad username and password and interval "{seconds}" seconds'
)
@dereference_step_parameters_and_data
def login_request(context, url_path_segment, seconds):
    url = append_path(context.endpoint, url_path_segment)
    with open(context.creds_file, "rb") as cf:
        creds_tuple = pickle.load(cf)
        for pair in creds_tuple:
            context.auth = pair
            context.response = get_requests(context).post(
                url,
                data=context.data,
                headers=context.headers,
                auth=context.auth,
                verify=context.verify_ssl,
            )
            # Sleep to avoid rate-limit
            time.sleep(int(seconds))


@behave.when('I make a GET request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def get_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).get(
        url, headers=context.headers, auth=context.auth, verify=context.verify_ssl
    )


@behave.when('I make a DELETE request to "{url_path_segment}"')
@dereference_step_parameters_and_data
def delete_request(context, url_path_segment):
    url = append_path(context.endpoint, url_path_segment)
    context.response = get_requests(context).delete(
        url, headers=context.headers, auth=context.auth, verify=context.verify_ssl
    )


@behave.then('the variable "{variable}" should be "{value}"')
@dereference_step_parameters_and_data
def get_var(context, variable, value):
    ensure(context.template_data[variable]).equals(value)


@behave.then('the response status should be one of "{statuses}"')
@dereference_step_parameters_and_data
def response_status_in(context, statuses):
    ensure(context.response.status_code).is_in([int(s) for s in statuses.split(",")])


@behave.then("the response status should be {status}")
@dereference_step_parameters_and_data
def response_status(context, status):
    ensure(context.response.status_code).equals(int(status))


@behave.then('the response body should contain "{content}"')
@dereference_step_parameters_and_data
def response_body_contains(context, content):
    ensure(content).is_in(context.response.content.decode("utf-8"))


@behave.then('the "{key}" header should be "{value}"')
@dereference_step_parameters_and_data
def check_header_inline(context, key, value):
    value_array = [item.encode("ascii") for item in value.split(" or ")]
    if len(value_array) > 1:
        ensure(value_array).contains(context.response.headers[key].encode("ascii"))
    else:
        ensure(context.response.headers[key].encode("ascii")).equals(value_array[0])


@behave.then('the value of header "{value}" should be in the given set')
@dereference_step_parameters_and_data
def check_header_value(context, value):
    ensure(value).is_in(context.response.headers.keys())
    ensure(context.db_header[value]).contains(
        context.response.headers[value].encode("ascii")
    )


@behave.then(
    'the value of header "{value}" should contain the defined value in the given set'
)
@dereference_step_parameters_and_data
def check_header_value_contains(context, value):
    ensure(value).is_in(context.response.headers.keys())
    for item in context.db_header[value]:
        ensure(item.decode("ascii")).is_in(context.response.headers[value])


@behave.then("the protocol of login URL should be https")
@dereference_step_parameters_and_data
def check_protocol(context):
    url_scheme = urllib.parse.urlparse(context.response.url).scheme
    ensure(url_scheme).equals("https")


@behave.then("the response body should be json format")
@dereference_step_parameters_and_data
def check_response_format(context):
    try:
        context.response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise e


@behave.then('the value of field "{key}" should be "{value}"')
@dereference_step_parameters_and_data
def check_response_field(context, key, value):
    res_json = context.response.json()
    ensure(key).is_in(res_json.keys())
    ensure(value).equals(res_json.get(key))
