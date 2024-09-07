#!/usr/bin/python

# Copyright: (c) 2024, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: weblogic_deployment

short_description: Manages WebLogic deployments (deploy, undeploy, update)

version_added: "1.0.0"

description: This module allows deploying, undeploying, and updating applications on WebLogic servers using the WebLogic REST API.

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
    application_name:
        description: The name of the application to be managed.
        required: true
        type: str
    state:
        description: The desired state of the application.
        required: true
        type: str
        choices: ['deployed', 'undeployed', 'updated']
    deployment_path:
        description: Path to the application file to deploy.
        required: false
        type: str

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Deploy an application
- name: Deploy an application to WebLogic
  weblogic_deployment:
    admin_url: "http://admin-server:7001"
    username: "weblogic"
    password: "password"
    application_name: "myApp"
    state: "deployed"
    deployment_path: "/path/to/myApp.war"

# Undeploy an application
- name: Undeploy an application from WebLogic
  weblogic_deployment:
    admin_url: "http://admin-server:7001"
    username: "weblogic"
    password: "password"
    application_name: "myApp"
    state: "undeployed"

# Update an application
- name: Update an application in WebLogic
  weblogic_deployment:
    admin_url: "http://admin-server:7001"
    username: "weblogic"
    password: "password"
    application_name: "myApp"
    state: "updated"
    deployment_path: "/path/to/updatedMyApp.war"
'''

RETURN = r'''
application_name:
    description: The name of the application being managed.
    type: str
    returned: always
    sample: "myApp"
state:
    description: The state of the application.
    type: str
    returned: always
    sample: "deployed"
changed:
    description: Whether the deployment state of the application was changed.
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from requests import post
from requests.auth import HTTPBasicAuth
import os

def run_module():
    module_args = dict(
        admin_url=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        application_name=dict(type='str', required=True),
        state=dict(type='str', choices=['deployed', 'undeployed', 'updated'], required=True),
        deployment_path=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        application_name='',
        state=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    admin_url = module.params['admin_url']
    username = module.params['username']
    password = module.params['password']
    application_name = module.params['application_name']
    state = module.params['state']
    deployment_path = module.params['deployment_path']

    result['application_name'] = application_name
    result['state'] = state

    try:
        if state == 'deployed':
            if not deployment_path or not os.path.exists(deployment_path):
                module.fail_json(msg=f"Deployment path {deployment_path} is required and must exist for deploying the application")
            deploy_application(admin_url, username, password, application_name, deployment_path)
            result['changed'] = True

        elif state == 'undeployed':
            undeploy_application(admin_url, username, password, application_name)
            result['changed'] = True

        elif state == 'updated':
            if not deployment_path or not os.path.exists(deployment_path):
                module.fail_json(msg=f"Deployment path {deployment_path} is required and must exist for updating the application")
            update_application(admin_url, username, password, application_name, deployment_path)
            result['changed'] = True

    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(**result)

def deploy_application(admin_url, username, password, application_name, deployment_path):
    deploy_url = f"{admin_url}/management/weblogic/latest/domainRuntime/deploymentManager/appDeployments/{application_name}/deploy"
    with open(deployment_path, 'rb') as file_data:
        files = {'deployment': (os.path.basename(deployment_path), file_data)}
        response = post(deploy_url, files=files, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()

def undeploy_application(admin_url, username, password, application_name):
    undeploy_url = f"{admin_url}/management/weblogic/latest/domainRuntime/deploymentManager/appDeployments/{application_name}/undeploy"
    response = post(undeploy_url, auth=HTTPBasicAuth(username, password))
    response.raise_for_status()

def update_application(admin_url, username, password, application_name, deployment_path):
    update_url = f"{admin_url}/management/weblogic/latest/domainRuntime/deploymentManager/appDeployments/{application_name}/redeploy"
    with open(deployment_path, 'rb') as file_data:
        files = {'deployment': (os.path.basename(deployment_path), file_data)}
        response = post(update_url, files=files, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()

def main():
    run_module()

if __name__ == '__main__':
    main()
