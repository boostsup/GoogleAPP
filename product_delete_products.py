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
"""Gets all products on the specified account."""

import sys
import os
import csv
import time

from apiclient.http import BatchHttpRequest
from oauth2client import client
import shopping_common

# The maximum number of results to be returned in a page.
MAX_PAGE_SIZE = 1000
products_path = os.path.expanduser('~/products.txt')

def product_deleted(request_id, unused_response, exception):
  if exception is not None:
    # Do something with the exception.
    print('There was an error: ' + str(exception))
  else:
    print('Requested product %s was deleted.' % request_id)

def main(argv):
  # Authenticate and construct service.
  service, config, _ = shopping_common.init(argv, __doc__)
  merchant_id = config['merchantId']

  with open(products_path, 'r') as products_handle:
    products_buf = []
    products_reader = csv.reader(products_handle, delimiter="\t")
    for product_record in products_reader:
      if len(products_buf) < MAX_PAGE_SIZE:
        products_buf.append(product_record)
        continue

      batch = BatchHttpRequest(callback=product_deleted)
      for product in products_buf:
        batch.add(
          service.products().delete(merchantId=merchant_id, productId=product[0]))

      while True:
        try:
          batch.execute()
          break
        except client.AccessTokenRefreshError:
          print('The credentials have been revoked or expired, please re-run the '
                'application to re-authorize')
        except Exception as e:
          print(e.message)
          time.sleep(180)
          break
      products_buf = []
    if len(products_buf) > 0:
      batch = BatchHttpRequest(callback=product_deleted)
      for product in products_buf:
        batch.add(
          service.products().delete(merchantId=merchant_id, productId=product[0]))
      try:
        batch.execute()
      except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')
      except:
        time.sleep(180)  
if __name__ == '__main__':
  main(sys.argv)
