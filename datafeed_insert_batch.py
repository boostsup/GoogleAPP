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
"""Adds several datafeeds to the specified account, in a single batch."""

import sys

from apiclient.http import BatchHttpRequest
import datafeed_sample
from oauth2client import client
import shopping_common

# Number of datafeeds to insert.
BATCH_SIZE = 5


def datafeed_inserted(unused_request_id, response, exception):
  if exception is not None:
    # Do something with the exception.
    print 'There was an error: ' + str(exception)
  else:
    print('Datafeed with name "%s" and ID "%s" was created.' %
          (response['name'], response['id']))


def main(argv):
  # Authenticate and construct service.
  service, config, _ = shopping_common.init(argv, __doc__)
  merchant_id = config['merchantId']

  batch = BatchHttpRequest(callback=datafeed_inserted)

  for _ in range(BATCH_SIZE):
    name = 'feed%s' % shopping_common.get_unique_id()
    datafeed = datafeed_sample.create_datafeed_sample(config, name)

    # Add datafeed to the batch.
    batch.add(service.datafeeds().insert(merchantId=merchant_id, body=datafeed))
  try:
    batch.execute()
  except client.AccessTokenRefreshError:
    print('The credentials have been revoked or expired, please re-run the '
          'application to re-authorize')


if __name__ == '__main__':
  main(sys.argv)
