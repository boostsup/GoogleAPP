#!/usr/bin/python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Updates the specified product on the specified account.

This should only be used for properties unsupported by the inventory
collection. If you're updating any of the supported properties in a product,
be sure to use the inventory.set method, for performance reasons.
"""

import argparse
import sys,os,datetime,getpass,time,codecs
import _constants
from app.myutil import myutil
from oauth2client import client
import shopping_common

# Declare command-line flags.
start = datetime.datetime.now()
root_path=os.path.split(os.path.abspath(__file__))[0]+'/'
root_path=root_path.replace('\\','/')
store_name = 'olivesmall'
inven_path = myutil.get_path(root_path,['src','inven',store_name])+'status_'+time.strftime("%Y-%m-%d",time.localtime())+'.txt'


def product_update(argv,products_list):
	# Authenticate and construct service.
	service, config,_ = shopping_common.init(argv, __doc__)
	merchant_id = config['merchantId']
	for product_dic in products_list:
		try:

			# First we need to retrieve the full object, since there are no partial
			# updates for the products collection in Content API v2.
			product_id = _constants.CHANNEL+':'+_constants.CONTENT_LANGUAGE+':'+_constants.TARGET_COUNTRY+':shopify_US_'+product_dic['productid']+'_'+product_dic['variantid']
			#product_id = 'online:en:US:shopify_US_11150141316_42564264964'
			#print(product_id)
			try:
				product = service.products().get(
						merchantId=merchant_id, productId=product_id).execute()
			except:
				continue
			# Let's fix the warning about product_type and update the product.
			product['expirationDate'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(time.time()+3600*24*int(30))),
			product['availability'] = 'in stock' if int(product_dic['quantity'])>0 else 'out of stock'
			product['price']['value'] = product_dic['price']
			product['price']['currency'] = 'USD'
			# Notice that we use insert. The products service does not have an update
			# method. Inserting a product with an ID that already exists means the same
			# as doing an update.
			request = service.products().insert(merchantId=merchant_id, body=product)
			#print(product)
			result = request.execute()
			print('Product with offerId "%s" was updated.' % (result['offerId']))

		except client.AccessTokenRefreshError:
			print('The credentials have been revoked or expired, please re-run the '
						'application to re-authorize')

def get_products(file_path):
	products_list = []
	readfile = codecs.open(file_path,encoding='utf-8')
	in_title = readfile.readline()
	in_fields_list = in_title.strip('\n').strip('\r').split('\t')
	in_title_dic = {}
	for field in in_fields_list:
		in_title_dic[field] = in_fields_list.index(field)
	for line in readfile:
		in_content_dic = {}
		items=line.strip('\n').strip('\r').split('\t')
		try:
			for key in in_title_dic:
				in_content_dic[key]=items[in_title_dic[key]]
		except:
			continue
		products_list.append(in_content_dic)
	return products_list

products_list = get_products(inven_path)
product_update(sys.argv,products_list)
