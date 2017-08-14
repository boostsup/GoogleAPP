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
MAX_PAGE_SIZE = 250
products_path = os.path.expanduser('~/products.txt')
print(products_path)
if os.path.isfile(products_path):
  os.remove(products_path)

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
  products_handle = open(products_path, 'a')
  products_writer = csv.writer(products_handle, delimiter="\t")

  try:
    request = service.products().list(
        merchantId=merchant_id, maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      if shopping_common.json_absent_or_false(result, 'resources'):
        print('No products were found.')
        break
      else:
        products = result['resources']
        for product in products:
          print('Product "%s" was found.' % (product['id']))
          products_writer.writerow([product['id']])

        request = service.products().list_next(request, result)
      time.sleep(1)

  except client.AccessTokenRefreshError:
    print('The credentials have been revoked or expired, please re-run the '
          'application to re-authorize')

  products_handle.close()
  with open(products_path, 'rb') as products_handle:
    products_buf = []
    products_reader = csv.reader(products_handle, delimiter="\t")
    for product_record in products_reader:
      if len(products_buf) < 1000:
        products_buf.append(product_record)
        continue

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
