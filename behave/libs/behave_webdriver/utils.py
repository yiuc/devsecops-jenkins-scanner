from os import getenv, environ
from functools import wraps
import jinja2
import six
from behave_webdriver.driver import (Chrome,
                                     Firefox,
                                     Ie,
                                     Edge,
                                     Opera,
                                     Safari,
                                     BlackBerry,
                                     PhantomJS,
                                     Android,
                                     Remote)


def _from_string(webdriver_string):
    def get_driver_name(driver):
        return driver.__name__.upper()
    drivers = [Chrome, Firefox, Ie, Edge, Opera, Safari, BlackBerry, PhantomJS, Android, Remote]
    driver_map = {get_driver_name(d): d for d in drivers}
    driver_map['CHROME.HEADLESS'] = Chrome.headless
    Driver = driver_map.get(webdriver_string.upper(), None)
    if Driver is None:
        raise ValueError('No such driver "{}". Valid options are: {}'.format(webdriver_string,
                                                                             ', '.join(driver_map.keys())))
    return Driver


def from_string(webdriver_string, *args, **kwargs):
    Driver = _from_string(webdriver_string)
    return Driver(*args, **kwargs)


def _from_env(default_driver=None):
    browser_env = getenv('BEHAVE_WEBDRIVER', default_driver)
    if browser_env is None:
        raise ValueError('No driver found in environment variables and no default driver selection')
    if isinstance(browser_env, six.string_types):
        Driver = _from_string(browser_env)
    else:
        # if not a string, assume we have a webdriver instance
        Driver = browser_env
    return Driver


def from_env(*args, **kwargs):
    default_driver = kwargs.pop('default_driver', None)
    if default_driver is None:
        default_driver = 'Chrome.headless'
    Driver = _from_env(default_driver=default_driver)

    return Driver(*args, **kwargs)

def _get_data_from_context(context):
    """Use context.text as a template and render against any stored state."""
    data = context.text if context.text else ""
    # Always clear the text to avoid accidental re-use.
    context.text = ""
    # NB rendering the template always returns unicode.
    result = jinja2.Template(data).render(context.template_data)
    return result.encode("utf8")

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
                value = environ.get(value[1:], value)
            decoded_kwargs[key] = value
        context.data = _get_data_from_context(context)
        return f(context, **decoded_kwargs)

    return wrapper
