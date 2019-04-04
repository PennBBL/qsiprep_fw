import os, os.path, json, re
import jsonschema
import six

from . import utils
from . import resolver

DEFAULT_TEMPLATE_NAME = 'bids-v1'
BIDS_TEMPLATE_NAME = 'bids-v1'
DEFAULT_TEMPLATES = {}

class Template:
    """
    Represents a project-level template for organizing data.

    Args:
        data (dict): The json configuration for the template
        templates (list): The optional existing map of templates by name.

    Attributes:
        namespace (str): The namespace where resolved template data is displayed.
        description (str): The optional description of the template.
        definitions (dict): The map of template definitions.
        rules (list): The list of if rules for applying templates.
        extends (string): The optional name of the template to extend.
        exclude_rules (list): The optional list of rules to exclude from a parent template.
    """
    def __init__(self, data, templates=None):
        if data:
            self.namespace = data.get('namespace')
            self.description = data.get('description', '')
            self.definitions = data.get('definitions', {})
            self.rules = data.get('rules', [])
            self.upload_rules = data.get('upload_rules', [])
            self.resolvers = data.get('resolvers', [])
            self.custom_initializers = data.get('initializers', [])

            self.extends = data.get('extends')
            self.exclude_rules = data.get('exclude_rules', [])
        else:
            raise Exception("data is required")

        if templates:
            self.do_extend(templates)

        resolver = jsonschema.RefResolver.from_schema({'definitions': self.definitions})
        self.resolve_refs(resolver, self.definitions)
        self.compile_resolvers()
        self.compile_rules()
        self.compile_custom_initializers()

    def do_extend(self, templates):
        """
        Implements the extends logic for this template.

        Args:
            templates (list): The existing list of templates.
        """
        if not self.extends:
            return

        if self.extends not in templates:
            raise Exception('Could not find parent template: {0}'.format(self.extends))

        parent = templates[self.extends]

        if not self.namespace:
            self.namespace = parent.namespace

        my_rules = self.rules
        my_defs = self.definitions
        my_resolvers = self.resolvers

        # Extend definitions
        self.definitions = parent.definitions.copy()
        for key, value in my_defs.items():
            self.definitions[key] = value

        # Extend rules, after filtering excluded rules
        filtered_rules = filter(lambda x: x.id not in self.exclude_rules, parent.rules)
        self.rules = my_rules + list(filtered_rules)

        # Extend resolvers
        self.resolvers = my_resolvers + parent.resolvers

    def compile_rules(self):
        """
        Converts the rule dictionaries on this object to Rule class objects.
        """
        for i in range(0, len(self.rules)):
            rule = self.rules[i]
            if not isinstance(rule, Rule):
                self.rules[i] = Rule(rule)

        for i in range(0, len(self.upload_rules)):
            upload_rule = self.upload_rules[i]
            if not isinstance(upload_rule, Rule):
                self.upload_rules[i] = Rule(upload_rule)

    def compile_resolvers(self):
        """
        Walk through the definitions
        """
        self.resolver_map = {}
        for i in range(0, len(self.resolvers)):
            res = self.resolvers[i]
            if not isinstance(res, resolver.Resolver):
                res = resolver.Resolver(self.namespace, res)

            # Create a mapping of template id to resolver
            for tmpl in res.templates:
                if tmpl not in self.resolver_map:
                    self.resolver_map[tmpl] = []
                self.resolver_map[tmpl].append(res)

    def compile_custom_initializers(self):
        """
        Map custom initializers by rule id
        """
        self.initializer_map = {}
        for init in self.custom_initializers:
            rule = init.get('rule')
            if not rule:
                continue
            del init['rule']
            if rule not in self.initializer_map:
                self.initializer_map[rule] = []
            self.initializer_map[rule].append(init)

    def apply_custom_initialization(self, rule_id, info, context):
        """
        Apply custom initialization templates for the given rule

        Args:
            rule_id (str): The id of the matched rule
            info (dict): The info object to update
            context (dict): The current context
        """
        if rule_id in self.initializer_map:
            for init in self.initializer_map[rule_id]:
                if 'where' in init:
                    if not test_where_clause(init['where'], context):
                        continue

                apply_initializers(init['initialize'], info, context)

    def validate(self, templateDef, info):
        """
        Validate info against a template definition schema.

        Args:
            templateDef (dict): The template definition (schema)
            info (dict): The info object to validate

        Returns:
            list(string): A list of validation errors if invalid, otherwise an empty list.
        """
        if '_validator' not in templateDef:
            templateDef['_validator'] = jsonschema.Draft4Validator(templateDef)

        return list(sorted(templateDef['_validator'].iter_errors(info), key=str))

    def resolve_refs(self, resolver, obj, parent=None, key=None):
        """
        Resolve all references found in the definitions tree.

        Args:
            resolver (jsonschema.RefResolver): The resolver instance
            obj (object): The object to resolve
            parent (object): The parent object
            key: The key to the parent object
        """
        if isinstance(obj, dict):
            if parent and '$ref' in obj:
                ref, result = resolver.resolve(obj['$ref'])
                parent[key] = result
            else:
                for k in obj.keys():
                    self.resolve_refs(resolver, obj[k], obj, k)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                self.resolve_refs(resolver, obj[i], obj, i)

class Rule:
    """
    Represents a matching rule for applying template definitions to resources or files within a project.

    Args:
        data (dict): The rule definition as a dictionary.

    Attributes:
        id (string): The optional rule id.
        template (str): The name of the template id to apply when this rule matches.
        initialize (dict): The optional set of initialization rules when this rule matches.
        conditions (dict): The set of conditions that must be true for this rule to match.
    """
    def __init__(self, data):
        self.id = data.get('id', '')
        self.template = data.get('template')
        self.initialize = data.get('initialize', {})
        if self.template is None:
            raise Exception('"template" field is required!')
        self.conditions = data.get('where')
        if not self.conditions:
            raise Exception('"where" field is required!')

    def test(self, context):
        """
        Test if the given context matches this rule.

        Args:
            context (dict): The context, which includes the hierarchy and current container

        Returns:
            bool: True if the rule matches the given context.
        """
        return test_where_clause(self.conditions, context)

    def initializeProperties(self, info, context):
        """
        Attempts to resolve initial values of BIDS fields from context.

        Template properties can now include an "initialize" field that gives instructions on how to attempt to
        initialize a field based on context. Within the initialize object, there are a list of keys to extract
        from the context, and currently regular expressions to match against the extracted fields. If the regex
        matches, then the "value" group will be extracted and assigned. Otherwise if 'take' is True for an initialization
        spec, we will copy that value into the field.

        Args:
            context (dict): The full context object
            info (dict): The BIDS data to update, if matched
        """
        apply_initializers(self.initialize, info, context)
        handle_run_counter_initializer(self.initialize, info, context)

def apply_initializers(initializers, info, context):
    """
    Attempts to resolve initial values of BIDS fields from context.

    Args:
        initializers (dict): The list of initializer specifications
        context (dict): The full context object
        info (dict): The BIDS data to update, if matched
    """
    for propName, propDef in initializers.items():
        resolvedValue = None

        if isinstance(propDef, dict):
            if '$switch' in propDef:
                resolvedValue = handle_switch_initializer(propDef['$switch'], context)
            else:
                for key, valueSpec in propDef.items():
                    # Lookup the value of the key
                    value = utils.dict_lookup(context, key)
                    if value is not None:
                        # Regex matching must provide a 'value' group
                        if '$regex' in valueSpec:
                            regex_list = valueSpec['$regex']
                            if not isinstance(regex_list, list):
                                regex_list = [regex_list]

                            for regex in regex_list:
                                m = re.search(regex, value)
                                if m is not None:
                                    resolvedValue = m.group('value')
                                    break
                        # 'take' will just copy the value
                        elif '$take' in valueSpec and valueSpec['$take']:
                            resolvedValue = value

                        if '$format' in valueSpec and resolvedValue:
                            resolvedValue = utils.format_value(valueSpec['$format'], resolvedValue)

                        if resolvedValue:
                            break
        else:
            resolvedValue = propDef

        if resolvedValue:
            info[propName] = resolvedValue


def handle_switch_initializer(switchDef, context):
    value = utils.dict_lookup(context, switchDef['$on'])
    if isinstance(value, list):
        value = set(value)

    for caseDef in switchDef['$cases']:
        compValue = caseDef.get('$eq')
        if isinstance(compValue, list):
            compValue = set(compValue)

        if '$default' in caseDef or value == compValue:
            return caseDef.get('$value')

    return None

def handle_run_counter_initializer(initializers, info, context):
    counter = context.get('run_counters')
    if not counter:
        return

    for propName, propDef in initializers.items():
        if isinstance(propDef, dict) and '$run_counter' in propDef:
            current = info.get(propName)
            if current == '+' or current == '=':
                key = propDef['$run_counter']['key']
                key = utils.process_string_template(key, context)

                counter = counter[key]
                if current == '+':
                    info[propName] = counter.next()
                else:
                    info[propName] = counter.current()

def test_where_clause(conditions, context):
    """
    Test if the given context matches this rule.

    Args:
        context (dict): The context, which includes the hierarchy and current container

    Returns:
        bool: True if the rule matches the given context.
    """

    for field, match in conditions.items():
        value = utils.dict_lookup(context, field)
        if not processValueMatch(value, match, field):
            return False

    return True

def processValueMatch(value, match, condition=None):
    """
    Helper function that recursively performs value matching.
    Args:
        value: The value to match
        match: The matching rule
    Returns:
        bool: The result of matching the value against the match spec.
    """
    if condition:
        # Handle $or clauses at top-level
        if condition == "$or":
            for field, deeper_match in match:
                value = utils.dict_lookup(context, field)
                if processValueMatch(value, deeper_match):
                    return True
            return False

        # Otherwise AND clauses
        if condition == "$and":
            for field, deeper_match in match:
                value = utils.dict_lookup(context, field)
                if not processValueMatch(value, deeper_match):
                    return False
            return True

    if isinstance(match, dict):
        # Deeper processing
        if '$in' in match:
            # Check if value is in list
            if isinstance(value, list):
                for item in value:
                    if item in match['$in']:
                        return True
                return False
            elif isinstance(value, six.string_types):
                for item in match['$in']:
                    if item in value:
                        return True
                return False

            return value in match['$in']

        elif '$not' in match:
            # Negate result of nested match
            return not processValueMatch(value, match['$not'])

        elif '$regex' in match:
            regex = re.compile(match['$regex'])

            if isinstance(value, list):
                for item in value:
                    if regex.search(item) is not None:
                        return True

                return False
            if value is None:
                return False
            return regex.search(value) is not None

    else:
        # Direct match
        if isinstance(value, list):
            for item in value:
                if item == match:
                    return True
            return False

        return value == match


def loadTemplates(templates_dir=None):
    """
    Load all templates in the given (or default) directory

    Args:
        templates_dir (string): The optional directory to load templates from.
    """
    results = {}

    if templates_dir is None:
        script_dir = os.path.dirname( os.path.realpath(__file__) )
        templates_dir = os.path.join(script_dir, '../templates')

    # Load all templates from the templates directory
    for fname in os.listdir(templates_dir):
        path = os.path.join(templates_dir, fname)
        name, ext = os.path.splitext(fname)
        if ext == '.json' and os.path.isfile(path):
            results[name] = loadTemplate(path)

    return results

def loadTemplate(path, templates=None):
    """
    Load the template at path

    Args:
        path (str): The path to the template to load
        templates (dict): The mapping of template names to template defintions.
    Returns:
        Template: The template that was loaded (otherwise throws)
    """
    with open(path, 'r') as f:
        data = json.load(f)

    data = utils.normalize_strings(data)

    if templates is None:
        templates = DEFAULT_TEMPLATES

    return Template(data, templates)

DEFAULT_TEMPLATES = loadTemplates()
DEFAULT_TEMPLATE = DEFAULT_TEMPLATES.get(DEFAULT_TEMPLATE_NAME)
BIDS_TEMPLATE = DEFAULT_TEMPLATES.get(BIDS_TEMPLATE_NAME)

