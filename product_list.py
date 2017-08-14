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

import sys,os,datetime,getpass,time
from app.myutil import myutil
from oauth2client import client
import shopping_common

start = datetime.datetime.now()
root_path=os.path.split(os.path.abspath(__file__))[0]+'/'
root_path=root_path.replace('\\','/')
# The maximum number of results to be returned in a page.
MAX_PAGE_SIZE = 50
store_name = 'olivesmall'
inven_path = myutil.get_path(root_path,['src','inven',store_name])+'inven_'+time.strftime("%Y-%m-%d",time.localtime())+'.txt'
inven_file = open(inven_path,'w',encoding='utf-8') 
def get_product_list(argv,inven_file):
  # Authenticate and construct service.
  service, config, _ = shopping_common.init(argv, __doc__)
  merchant_id = config['merchantId']
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
          print(product)
          exit()
          inven_file.write('\t'.join([product['id'],product.get('gtin',''),product['price'].get('value',''),product['condition'],product['availability']])+'\n')
          print('Product "%s" was found.' % (product['id']))
        request = service.products().list_next(request, result)

  except client.AccessTokenRefreshError:
    print('The credentials have been revoked or expired, please re-run the '
          'application to re-authorize')


get_product_list(sys.argv,inven_file)

end = datetime.datetime.now()
print((end-start).seconds)