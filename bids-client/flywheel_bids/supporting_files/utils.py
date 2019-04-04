import logging
import os
import re
import six
import sys
import subprocess
import jsonschema
import collections
from builtins import input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('utils')

BIDS_VALIDATOR_PATH = '/usr/bin/bids-validator'

def validate_bids(dirname):
    """ """
    if os.path.isfile(BIDS_VALIDATOR_PATH):
        logger.info('Validating BIDS directory')

        cmd = [BIDS_VALIDATOR_PATH, dirname]
        proc = subprocess.Popen(cmd,
                                #cwd=dirname,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        returncode = proc.returncode

        # TODO: Determine if an error should be raised or just a warning
        logger.info('returncode: %d' % returncode)
        logger.info('stderr: ' + str(stderr))
        logger.info('stdout: ' + str(stdout))
    else:
        logger.warn('Skipping validation, validator is not present')

def validate_project_label(fw, project_label):
    """ """
    # Find project id
    projects = fw.get_all_projects()
    project_found = False
    for p in projects:
        if p['label'] == project_label:
            project_id = p.id
            project_found = True

    if not project_found:
        logger.error('Cannot find project %s.' % project_label)
        sys.exit(1)

    return project_id

def get_project_id_from_session_id(fw, session_id):
    """ """
    # Find project id from session
    session = fw.get_session(session_id)
    if not session:
        logger.error('Could not load session %s.' % session_id)
        sys.exit(1)

    return session['project']


def get_extension(fname):
    """ Get extension

    If search returns a result, get value
    else, ext is None

    """
    ext = re.search('\.[a-zA-Z]*[\.]?[A-Za-z0-9]+$',fname)
    if ext:
        ext = ext.group()
    return ext

def dict_lookup(obj, value, default=None):
    # For now, we don't support escaping of dots
    parts = value.split('.')
    curr = obj
    for part in parts:
        if isinstance(curr, (dict, collections.Mapping)) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and int(part) < len(curr):
            curr = curr[int(part)]
        else:
            curr = default
            break
    return curr

def dict_set(obj, key, value):
    parts = key.split('.')
    curr = obj
    for part in parts[:-1]:
        if isinstance(curr, (dict, collections.Mapping)) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and int(part) < len(curr):
            curr = curr[int(part)]
        else:
            raise ValueError('Could not set value for key: ' + key)
    curr[parts[-1]] = value

def dict_match(matcher, matchee):
    """
    Returns True if each key,val pair is present in the matchee
    """
    for key, val in matcher.items():
        if not matchee.get(key):
            return False
        elif not isinstance(matchee.get(key), list):
            mval = [matchee.get(key)]
        else:
            mval = matchee.get(key)
        if isinstance(val, list):
            for item in val:
                if item not in mval:
                    return False
        else:
            if val not in mval:
                return False

    return True

def normalize_strings(obj):
    if isinstance(obj, six.string_types):
        return str(obj)
    if isinstance(obj, collections.Mapping):
        return dict(map(normalize_strings, obj.items()))
    if isinstance(obj, collections.Iterable):
        return type(obj)(map(normalize_strings, obj))
    return obj

# process_string_template(template, context)
# finds values in the context object and substitutes them into the string template
# Use <path> for cases where you want the result converted to lowerCamelCase
# Use {path} for cases where you want a literal value substitution
# path uses dot notation to navigate the context for desired values
# path examples:  <session.label>  returns session.label withou _ and -
#                 {file.info.BIDS.Filename} returns the value of file.info.BIDS.Filename
#                 {file.info.BIDS.Modality} returns Modality without modification
# example template string:
#       'sub-<subject.code>_ses-<session.label>_acq-<acquisition.label>_{file.info.BIDS.Modality}.nii.gz'

def process_string_template(template, context):
    tokens = re.compile('[^\[][A-Za-z0-9\.><}{-]+|\[[/A-Za-z0-9><}{_\.-]+\]')
    values = re.compile('[{<][A-Za-z0-9\.-]+[>}]')

    for token in tokens.findall(template):
        if values.search(token):
            replace_tokens = values.findall(token)
            for replace_token in replace_tokens:
                # Remove the {} or <> surrounding the replace_token
                path = replace_token[1:-1]
                # Get keys, if replace token has a . in it
                keys = path.split(".")
                result = context
                for key in keys:
                    if key in result:
                        result = result[key]
                    else:
                        result = None
                        break
                # If value found replace it
                if result:
                    # If replace token is <>, need to check if in BIDS
                    if replace_token[0] == '<':
                        # Check if result is already in BIDS format...
                        #   if so, split and grab only the label
                        if re.match('(sub|ses)-[a-zA-Z0-9]+', result):
                            label, result = result.split('-')
                        # If not, take the entire result and remove underscores and dashes
                        else:
                            result = ''.join(x for x in result.replace('_', ' ').replace('-', ' ') if x.isalnum())
                    # Replace the token with the result
                    template = template.replace(replace_token, str(result))
                # If result not found, but the token is option, remove the token from the template
                elif token[0] == '[':
                    template = template.replace(token, '')

                # TODO: Determine approach
                # Else the value hasn't been found AND field is required, and so let's replace with 'UNKNOWN'
                #elif token[0] != '[':
                #    result = 'UNKNOWN'
                #    template = template.replace(replace_token, result)
        else:
            pass

    # Replace any [] from the string
    processed_template = re.sub('\[|\]', '', template)

    return processed_template


def get_pattern(format_params):
    return format_params.get("$pattern")


def format_value(params, value):
    """
    Formats a string value based on list of given parameters i.e. [{"$replace": {"$pattern": "ab", "$replacement": "c"}}]
    will return "dcf" from "dabf"
    """
    for param in params:
        if "$replace" in param:
            value = re.sub(get_pattern(param["$replace"]), param["$replace"].get('$replacement'), value)
        elif "$lower" in param:
            if isinstance(param['$lower'], dict) and get_pattern(param["$lower"]):
                value = re.sub(get_pattern(param["$lower"]), lambda m: m.group(0).lower(), value)
            else:
                value = value.lower()
        elif "$upper" in param:
            if isinstance(param['$upper'], dict) and get_pattern(param["$upper"]):
                value = re.sub(get_pattern(param["$upper"]), lambda m: m.group(0).upper(), value)
            else:
                value = value.upper()
        elif "$camelCase" in param:
            if isinstance(param['$camelCase'], dict) and get_pattern(param["$camelCase"]):
                patterns = get_pattern(param["$camelCase"])
                if not isinstance(patterns, list):
                    patterns = [pattern]
                for pattern in patterns:
                    value = value.replace(patter, ' ')
                value = ''.join(x for x in value.title() if x.isalnum())
                value = value[0].lower() + value[1:]
            else:
                # Best to not process string with <...> with $camelCase : true
                value = ''.join(x for x in value.replace('_', ' ').replace('-', ' ').title() if x.isalnum())
                value = value[0].lower() + value[1:]

    return value


def confirmation_prompt(message):
    """Continue prompting at the terminal for a yes/no repsonse

    Arguments:
        message (str): The prompt message

    Returns:
        bool: True if the user responded yes, otherwise False
    """
    responses = { 'yes': True, 'y': True, 'no': False, 'n': False }
    while True:
        six.print_('{} (yes/no): '.format(message), end='')
        choice = input().lower()
        if choice in responses:
            return responses[choice]
        six.print_('Please respond with "yes" or "no".')


class RunCounter:
    def __init__(self):
        self.current = 0

    def next(self):
        self.current = self.current + 1
        return str(self.current)

    def current(self):
        return str(self.current)

class RunCounterMap:
    def __init__(self):
        self.entries = {}

    def __getitem__(self, key):
        if key not in self.entries:
            self.entries[key] = RunCounter()
        return self.entries[key]

    def __contains__(self, key):
        return True
