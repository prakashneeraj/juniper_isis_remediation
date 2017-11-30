
#path= /usr/local/lib/python2.7/dist-packages/ansible/modules/network/junos/junos_isis_remediate.py
#!usr/bin/python
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}


import re
import json

from ansible.module_utils.junos import load_config, get_configuration
from ansible.module_utils.junos import commit_configuration



def configure_device(module, warnings, candidate):
    kwargs = dict()
    kwargs['format'] = 'text'
    kwargs['action'] = 'set'
    return load_config(module, candidate, warnings, **kwargs)

def action_remediate(module, warnings, interface):
    module = module
    warnings = warnings
    lines = ['delete interfaces {} disable'.format(interface)]
    configure_device(module, warnings, lines)
    commit_configuration(module)
    msg = "remediation done"
    return msg
