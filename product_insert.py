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
"""This example adds a product to a specified account."""

import sys

from oauth2client import client
import product_sample
import shopping_common


def main(argv):
  # Authenticate and construct service.
  service, config, _ = shopping_common.init(argv, __doc__)
  merchant_id = config['merchantId']

  try:
    offer_id = 'book#%s' % shopping_common.get_unique_id()
    print(offer_id)
    exit()
    product = product_sample.create_product_sample(config, offer_id)

    # Add product.
    request = service.products().insert(merchantId=merchant_id, body=product)

    result = request.execute()
    print('Product with offerId "%s" and title "%s" was created.' %
          (result['offerId'], result['title']))

  except client.AccessTokenRefreshError:
    print('The credentials have been revoked or expired, please re-run the '
          'application to re-authorize')


if __name__ == '__main__':
  main(sys.argv)
