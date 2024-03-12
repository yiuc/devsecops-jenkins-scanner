import string
import behave
import os
from subprocess import Popen, PIPE
from behave_webdriver.transformers import matcher_mapping
from behave_webdriver.utils import dereference_step_parameters_and_data


FEATURE_DIR=f"{os.getcwd()}/features"


if 'transform-parse' not in matcher_mapping:
    behave.use_step_matcher('parse')
else:
    behave.use_step_matcher('transform-parse')


@behave.when('I pause for {milliseconds:d}ms')
def sleep_ms(context, milliseconds):
    context.behave_driver.pause(milliseconds)


@behave.given('I click on the element "{element}"')
@behave.when('I click on the element "{element}"')
def click_element(context, element):
    context.behave_driver.click_element(element)


@behave.when('I doubleclick on the element "{element}"')
def doubleclick_element(context, element):
    context.behave_driver.doubleclick_element(element)


@behave.when('I click on the link "{link_text}"')
def click_link(context, link_text):
    context.behave_driver.click_link_text(link_text)


@behave.when('I click on the button "{element}"')
def click_button(context, element):
    context.behave_driver.click_element(element)


@behave.when('I set "{value}" to the inputfield "{element}"')
@behave.given('I set "{value}" to the inputfield "{element}"')
@dereference_step_parameters_and_data
def set_input(context, value, element):
    elem = context.behave_driver.get_element(element)
    elem.clear()
    elem.send_keys(value)

@behave.given('I set TOTP to the inputfield "{element}"')
def set_totp(context, element):
    elem = context.behave_driver.get_element(element)
    elem.clear()
    # Need to Prepare the TOTP first
    totp_dir = f"{FEATURE_DIR}/totp"
    command = "bash OTP.sh"
    with Popen(command, stdout=PIPE, stderr=None, shell=True, cwd=totp_dir) as p:
        otp_code = p.communicate()[0].decode("utf-8").strip()
    elem.send_keys(otp_code)


@behave.when('I add "{value}" to the inputfield "{element}"')
@behave.given('I add "{value}" to the inputfield "{element}"')
def add_input(context, value, element):
    elem = context.behave_driver.get_element(element)
    elem.send_keys(value)


@behave.when('I clear the inputfield "{element}"')
def clear_input(context, element):
    elem = context.behave_driver.get_element(element)
    elem.clear()


@behave.when('I drag element "{from_element}" to element "{to_element}"')
def drag_element(context, from_element, to_element):
    context.behave_driver.drag_element(from_element, to_element)


@behave.when('I submit the form "{element}"')
def submit_form(context, element):
    context.behave_driver.submit(element)


@behave.when('I set a cookie "{cookie_key}" with the content "{value}"')
def set_cookie(context, cookie_key, value):
    context.behave_driver.add_cookie({'name': cookie_key, 'value': value})


@behave.when('I delete the cookie "{cookie_key}"')
def delete_cookie(context, cookie_key):
    context.behave_driver.delete_cookie(cookie_key)


@behave.when('I press "{key}"')
def press_button(context, key):
    context.behave_driver.press_button(key)


@behave.when('I scroll to element "{element}"')
def scroll_to(context, element):
    context.behave_driver.scroll_to_element(element)


@behave.when('I select the {nth} option for element "{element}"')
def select_nth_option(context, nth, element):
    index = int(''.join(char for char in nth if char in string.digits))
    context.behave_driver.select_option(element,
                                        by='index',
                                        by_arg=index)


@behave.when('I move to element "{element}" with an offset of {x_offset:d},{y_offset:d}')
def move_to_element_offset(context, element, x_offset, y_offset):
    context.behave_driver.move_to_element(element, (x_offset, y_offset))


@behave.when('I move to element "{element}"')
def move_to_element(context, element):
    context.behave_driver.move_to_element(element)


behave.use_step_matcher('parse')
