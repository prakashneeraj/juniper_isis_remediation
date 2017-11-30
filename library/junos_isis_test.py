#path= /usr/local/lib/python2.7/dist-packages/ansible/modules/network/junos/junos_isis_test.py
#!usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}



import time
import re
#import shlex

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.junos import junos_argument_spec, check_args, get_configuration
#from ansible.module_utils.netcli import Conditional, FailedConditionalError
from ansible.module_utils.netconf import send_request
from ansible.module_utils.six import string_types, iteritems
from ansible.modules.network.junos.junos_isis_remediate import *
#from ansible.module_utils.connection import Connection,exec_command

try:
	from lxml.etree import Element, SubElement, tostring
except ImportError:
	from xml.etree.ElementTree import Element, SubElement, tostring

try:
	import jxmlease
	HAS_JXMLEASE = True
except ImportError:
	HAS_JXMLEASE = False

USE_PERSISTENT_CONNECTION = True


def to_lines(stdout):
	lines = list()
	for item in stdout:
		if isinstance(item, string_types):
			item = str(item).split('\n')
		lines.append(item)
	return lines

def rpc(module, items):

    responses = list()

    for item in items:
        name = item['name']
        xattrs = item['xattrs']
        fetch_config = False

        #args = item.get('args')
        text = item.get('text')

        #name = str(name).replace('_', '-')
        name = str(name)

        #if all((module.check_mode, not name.startswith('get'))):
            #module.fail_json(msg='invalid rpc for running in check_mode')

        if name == 'command' and text.startswith('show configuration') or name == 'get-configuration':
            fetch_config = True

        element = Element(name, xattrs)

        if text:
            element.text = text
        
        if fetch_config:
            reply = get_configuration(module, format=xattrs['format'])
        else:
            reply = send_request(module, element, ignore_warning=False)
        
        responses.append(tostring(reply))

    return responses


def split(value):
    lex = shlex.shlex(value)
    lex.quotes = '"'
    lex.whitespace_split = True
    lex.commenters = ''
    return list(lex)


def parse_commands(module, warnings):
    items = list()

    for command in (module.params['commands'] or list()):
        parts = command.split('|')
        text = parts[0]

        display = module.params['display'] or 'text'

        if '| display json' in command:
            display = 'json'

        elif '| display xml' in command:
            display = 'xml'

        if display == 'set' or '| display set' in command:
            if command.startswith('show configuration'):
                display = 'set'
            else:
                module.fail_json(msg="Invalid display option '%s' given for command '%s'" % ('set', command))

        xattrs = {'format': display}
        items.append({'name': 'command', 'xattrs': xattrs, 'text': text})

    return items




def main():

    argument_spec = dict(
        commands=dict(type='list', required=True),
        display=dict(choices=['text', 'json', 'xml', 'set'], aliases=['format', 'output']),
    )

    argument_spec.update(junos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)
    result={'changed': False}
  
    items = list()
    items.extend(parse_commands(module, warnings))
    command = module.params['commands']
    if(command[0]=='show isis interface'):
        responses = rpc(module, items)
    else:
    	module.fail_json(msg='invalid show command(please give show isis interface)')
    regex = "([a-z0-9./-]+)\s+([0-9]+)\s+([\w]+)\s+(\w+)\s+(Down)\s+(\w+)"
    res=responses[0].split('\n')        
    for response in res:
        m = re.match(regex,response)
        if m:
            interface = m.group(1)
            remediate = action_remediate(module, warnings, interface)
    result.update({
        'changed': False,
        'warnings': warnings,
        'stdout': responses,
        'stdout_lines': to_lines(responses)
    })
	

    module.exit_json(**result)
	
if __name__ == '__main__':
    main()
