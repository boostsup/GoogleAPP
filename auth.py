#!/usr/bin/python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Authentication-related info for the Content API for Shopping samples."""
from __future__ import print_function
import os
import sys

import _constants
from oauth2client import client
from oauth2client import tools
from oauth2client.service_account import ServiceAccountCredentials
import token_storage


def authorize(config, flags):
  """Authorization for the Content API Samples.

  This function uses common idioms found across all the included
  samples, i.e., that service account credentials are located in a
  file called 'client-service.json' and that OAuth2 client credentials
  are located in a file called 'client-oauth2.json', both in the same
  directory as the sample configuration file.  Only one of these files
  needs to exist for authentication, and the service account will be
  chosen first if both exist.

  Args:
      config: dictionary, Python representation of config JSON.
      flags: the parsed commandline flags.

  Returns:
      An oauth2lib.Credential object suitable for using to authenticate
      to the Content API.
  """
  try:
    credentials = client.GoogleCredentials.get_application_default()
    print('Using application default credentials.')
    return credentials.create_scoped(_constants.API_SCOPE)
  except client.ApplicationDefaultCredentialsError:
    pass  # Can safely ignore this error, since it just means none were found.
  except Exception:
    pass
  if 'path' not in config:
    print('Must use Application Default Credentials with no configuration.')
    sys.exit(1)
  service_account_path = os.path.join(config['path'],
                                      _constants.SERVICE_ACCOUNT_FILE)
  client_secrets_path = os.path.join(config['path'],
                                     _constants.CLIENT_SECRETS_FILE)
  if os.path.isfile(service_account_path):
    print('Using service account credentials from %s.' % service_account_path)
    return ServiceAccountCredentials.from_json_keyfile_name(
        service_account_path, scopes=_constants.API_SCOPE)
  elif os.path.isfile(client_secrets_path):
    print('Using OAuth2 client secrets from %s.' % client_secrets_path)
    storage = token_storage.Storage(config)
    credentials = storage.get()
    if credentials is not None and not credentials.invalid:
      return credentials
    message = tools.message_if_missing(client_secrets_path)
    flow = client.flow_from_clientsecrets(
        client_secrets_path,
        scope=_constants.API_SCOPE,
        message=message,
        login_hint=config['emailAddress'])
    return tools.run_flow(flow, storage, flags)
  print('No OAuth2 authentication files found. Checked:', file=sys.stderr)
  print('- Google Application Default Credentials', file=sys.stderr)
  print('- %s' % service_account_path, file=sys.stderr)
  print('- %s' % client_secrets_path, file=sys.stderr)
  print('Please read the accompanying documentation.', file=sys.stderr)
  sys.exit(1)
  return None
