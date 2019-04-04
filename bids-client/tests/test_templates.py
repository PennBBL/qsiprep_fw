import os
import json
import re
import shutil
import unittest

from flywheel_bids.supporting_files import utils, templates

class RuleTestCases(unittest.TestCase):

    def test_rule_initialize_switch(self):
        rule = templates.Rule({
            'template': 'test',
            'where': { 'x': True },
            'initialize': {
                'Property': {
                    '$switch': {
                        '$on': 'value',
                        '$cases': [
                            { '$eq': 'foo', '$value': 'found_foo' },
                            { '$eq': 'bar', '$value': 'found_bar' },
                            { '$default': True, '$value': 'found_nothing' }
                        ]
                    }
                }
            }
        })

        context = { 'value': 'foo' }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'found_foo' } )

        context = { 'value': 'bar' }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'found_bar' } )

        context = { 'value': 'something_else' }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'found_nothing' } )

    def test_rule_initialize_switch_lists(self):
        rule = templates.Rule({
            'template': 'test',
            'where': { 'x': True },
            'initialize': {
                'Property': {
                    '$switch': {
                        '$on': 'value',
                        '$cases': [
                            { '$eq': ['a', 'b', 'c'], '$value': 'match1' },
                            { '$eq': ['a', 'd'], '$value': 'match2' },
                            { '$default': True, '$value': 'no_match' }
                        ]
                    }
                }
            }
        })

        context = { 'value': ['c', 'b', 'a'] }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'match1' } )

        context = { 'value': ['a', 'd'] }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'match2' } )

        context = { 'value': ['a', 'b'] }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'no_match' } )

        context = { 'value': ['a', 'b', 'c', 'd'] }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'no_match' } )

    def test_rule_initialize_format(self):
        rule = templates.Rule({
            'template': 'test',
            'where': { 'x': True },
            'initialize': {
                'Property': {
                    'value': {
                        '$take': True,
                        '$format': [
                            # Use regex to find patterns
                            {'$replace': {'$pattern': '[A-Z]+', '$replacement': 'NEW'}},
                            # Chain formatting operations
                            {'$lower': {'$pattern': 'EW'}}
                        ]
                    }
                }
            }
        })
        rule2 = templates.Rule({
            'template': 'test',
            'where': { 'x': True },
            'initialize': {
                'Property': {
                    'value': {
                        '$take': True,
                        '$format': [
                            # Use regex to find patterns
                            {'$replace': {'$pattern': '[A-Z]+', '$replacement': 'UPPER_12_key'}},
                            # Chain formatting operations
                            {'$lower': True}
                        ]
                    }
                }
            }
        })
        context = { 'value': 'the_OLD_string' }
        info = { }
        rule.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'the_New_string'})
        info = { }
        rule2.initializeProperties(info, context)
        self.assertEqual( info, { 'Property': 'the_upper_12_key_string'})

    def test_rule_where_regex_match(self):
        rule = templates.Rule({
            'template': 'test',
            'where': {
                'x': {
                    "$regex": "topup"
                }
            }
        })
        context = { 'x': 'string_with topup in it' }
        self.assertTrue(rule.test(context))

    def test_rule_in_string(self):
        """ """
        rule = templates.Rule({
            'template': 'test',
            'where': {
                'x.l': {
                    "$in": ["topup", "something_else"]
                }
            }
        })
        # Define context

        context = { 'x': {'l':'string_with topup in it' }}
        # Call function
        self.assertTrue(rule.test(context))

        rule = templates.Rule({
            'template': 'test',
            'where': {
                'x': {
                    "$in": ["not_topup", "something_else"]
                }
            }
        })
        # Call function
        self.assertFalse(rule.test(context))

    def test_rule_where_not(self):
        """ """
        rule = templates.Rule({
            'template': 'test',
            'where': {
                'x': {
                    '$not': {
                        '$in': ["Value"]
                    }
                }
            }
        })
        context = {'x': 'Value'}
        self.assertFalse(rule.test(context))
        context = {'x': 'Something'}
        self.assertTrue(rule.test(context))

