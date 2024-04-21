from __future__ import unicode_literals
from functools import wraps
import jinja2
import os
import string
import random
from six.moves import urllib


def dereference_step_parameters_and_data(f):
    """Decorator to dereference step parameters and data.

    This involves three steps:

        1) Rendering feature file step parameters as a Jinja2 template
        against context.template_data.

        2) Replacing step parameters with environment variable values
        if they look like an environment variable (start with a
        "$"). Fall back to original value if environment variable does
        not exist.

        3) Treating context.text as a Jinja2 template rendered against
        context.template_data, and putting the result in context.data.

    """

    @wraps(f)
    def wrapper(context, **kwargs):
        decoded_kwargs = {}
        for key, value in kwargs.items():
            value = jinja2.Template(value).render(context.template_data)
            if value.startswith("$"):
                value = os.environ.get(value[1:], value)
            decoded_kwargs[key] = value
        return f(context, **decoded_kwargs)

    return wrapper


def append_path(url, url_path):
    return urllib.parse.urljoin(url, url_path)


def filename_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))
