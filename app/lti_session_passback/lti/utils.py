TITLE = 'context_title'
RETURN_URL = 'launch_presentation_return_url'
USERNAME = 'ext_user_username'
PERSON_NAME = 'lis_person_name_full'
ROLES = 'roles'
ADMIN_ROLE = 'Instructor'
CUSTOM_PARAM_PREFIX = 'custom_'
PASSBACK_PARAMS = ('lis_outcome_service_url', 'lis_result_sourcedid', 'oauth_consumer_key')

from app.bd_helper.bd_helper import ConsumersDBManager

def get_param(data, key):
    if key in data:
        return data[key]
    else:
        raise KeyError("{} doesn't include {}.".format(data, key))


def get_title(data): return get_param(data, TITLE)


def get_return_url(data): return get_param(data, RETURN_URL)


def get_username(data): return get_param(data, USERNAME)


def get_person_name(data): return get_param(data, PERSON_NAME)


def create_consumers(consumer_dict):
    for key, secret in consumer_dict.items():
        ConsumersDBManager.add_consumer(key, secret)

def parse_consumer_info(key_str, secret_str):
    keys = key_str.split(',')
    secrets = secret_str.split(',')

    if len(keys) != len(secrets):
        raise Exception(f"len(consumer_keys) != len(consumer_secrets): '{key_str}' vs '{secret_str}'")

    return { key: secret for key, secret in zip(keys, secrets) }
    
def get_role(data, default_role=False):
    try:
        return get_param(data, ROLES).split(',')[0] == ADMIN_ROLE
    except:
        return default_role


def get_custom_params(data):
    return { key[len(CUSTOM_PARAM_PREFIX):]: data[key] for key in data if key.startswith(CUSTOM_PARAM_PREFIX) }


def extract_passback_params(data):
    params = {}
    for param_key in PASSBACK_PARAMS:
        if param_key in data:
            params[param_key] = data[param_key]
        else:
            raise KeyError("{} doesn't include {}. Must inslude: {}".format(data, param_key, PASSBACK_PARAMS))
    return params
