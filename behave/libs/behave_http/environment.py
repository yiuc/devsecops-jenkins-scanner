from behave.model import Scenario


def before_all(context):
    userdata = context.config.userdata
    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", False)
    Scenario.continue_after_failed_step = continue_after_failed


def before_scenario(context, scenario):
    # Seed empty HTTP headers so steps do not need to check and create.
    context.headers = {}

    # Seed empty Jinja2 template data so steps do not need to check and create.
    context.template_data = {}

    # Default repeat attempt counts and delay for polling GET.
    context.n_attempts = 10
    context.pause_between_attempts = 0.05

    # Do not authenticate by default.
    context.auth = None

    # Verify server certificate by default.
    context.verify_ssl = False
