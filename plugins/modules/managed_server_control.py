#!/usr/bin/python

# Copyright: (c) 2024, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: weblogic_managed_server

short_description: Manages WebLogic managed servers (start, stop, restart)

version_added: "1.0.0"

description: This module allows starting, stopping, and restarting WebLogic managed servers using the WebLogic REST API.

options:
    admin_url:
        description: The URL of the WebLogic Administration Server.
        required: true
        type: str
    username:
        description: The username for the WebLogic server.
        required: true
        type: str
    password:
        description: The password for the WebLogic server.
        required: true
        type: str
        no_log: true
    server_name:
        description: The name of the managed server.
        required: true
        type: str
    state:
        description: The desired state of the managed server.
        required: true
        type: str
        choices: ['started', 'stopped', 'restarted']

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Start a WebLogic managed server
- name: Start WebLogic managed server
  weblogic_managed_server:
    admin_url: "http://admin-server:7001"
    username: "weblogic"
    password: "password"
    server_name: "ManagedServer1"
    state: "started"

# Stop a WebLogic managed server
- name: Stop WebLogic managed server
  weblogic_managed_server:
    admin_url: "http://admin-server:7001"
    username: "weblogic"
    password: "password"
    server_name: "ManagedServer1"
    state: "stopped"

# Restart a WebLogic managed server
- name: Restart WebLogic managed server
  weblogic_managed_server:
    admin_url: "http://admin-server:7001"
    username: "weblogic"
    password: "password"
    server_name: "ManagedServer1"
    state: "restarted"
'''

RETURN = r'''
server_name:
    description: The name of the managed server.
    type: str
    returned: always
    sample: "ManagedServer1"
state:
    description: The state of the managed server.
    type: str
    returned: always
    sample: "started"
changed:
    description: Whether the state of the server was changed.
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from requests import post
from requests.auth import HTTPBasicAuth
import time

def run_module():
    module_args = dict(
        admin_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        server_name=dict(type='str', required=True),
        state=dict(type='str', choices=['started', 'stopped', 'restarted'], required=True)
    )

    result = dict(
        changed=False,
        server_name='',
        state=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    admin_url = module.params['admin_url']
    username = module.params['username']
    password = module.params['password']
    server_name = module.params['server_name']
    state = module.params['state']

    result['server_name'] = server_name
    result['state'] = state

    try:
        if state == 'started':
            start_server(admin_url, username, password, server_name)
            result['changed'] = True

        elif state == 'stopped':
            stop_server(admin_url, username, password, server_name)
            result['changed'] = True

        elif state == 'restarted':
            stop_server(admin_url, username, password, server_name)
            wait_for_server_shutdown(admin_url, username, password, server_name)
            start_server(admin_url, username, password, server_name)
            result['changed'] = True

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)


def start_server(admin_url, username, password, server_name):
    start_url = f"{admin_url}/management/weblogic/latest/domainRuntime/serverLifeCycleRuntimes/{server_name}/start"
    response = post(start_url, auth=HTTPBasicAuth(username, password))
    response.raise_for_status()

def stop_server(admin_url, username, password, server_name):
    stop_url = f"{admin_url}/management/weblogic/latest/domainRuntime/serverLifeCycleRuntimes/{server_name}/shutdown"
    response = post(stop_url, auth=HTTPBasicAuth(username, password))
    response.raise_for_status()

def wait_for_server_shutdown(admin_url, username, password, server_name, timeout=60):
    status_url = f"{admin_url}/management/weblogic/latest/domainRuntime/serverLifeCycleRuntimes/{server_name}"
    for _ in range(timeout):
        response = post(status_url, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200 and response.json().get('state') == 'SHUTDOWN':
            break
        time.sleep(1)
    else:
        raise Exception(f"Server {server_name} did not shutdown within the timeout period")


def main():
    run_module()


if __name__ == '__main__':
    main()
