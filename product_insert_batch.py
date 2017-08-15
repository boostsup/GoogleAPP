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
"""Adds several products to the specified account, in a single batch."""

import sys,os,datetime,getpass,time
import _constants
from oauth2client import client
import product_sample
import shopping_common,codecs,traceback
from app.myutil import myutil

# Number of products to insert.
start = datetime.datetime.now()
root_path=os.path.split(os.path.abspath(__file__))[0]+'/'
root_path=root_path.replace('\\','/')
store_name = 'olivesmall'
inven_path = myutil.get_path(root_path,['src','inven',store_name])+'status_'+time.strftime("%Y-%m-%d",time.localtime())+'.txt'

BATCH_SIZE = 5

def create_product(config, product_dic, mode='insert'):
	"""Creates a sample product object for the product samples.

	Args:
			config: dictionary, Python version of config JSON
			offer_id: string, offer id for new product
			**overwrites: dictionary, a set of product attributes to overwrite

	Returns:
			A new product in dictionary form.
	"""
	if mode.lower() == 'insert':
		product = {
				'offerId':
						product_dic['offerId'],
				'title':
						product_dic['title'],
				'description':
						product_dic['description'],
				'link':
						product_dic['link'],
				'imageLink':
						product_dic['imageLink'],
				'contentLanguage':
						_constants.CONTENT_LANGUAGE,
				'targetCountry':
						_constants.TARGET_COUNTRY,
				'channel':
						_constants.CHANNEL,
				'availability':
						'in stock' if product_dic['quantity']>0 else 'out of stock',
				'condition':
						product_dic['condition'],
				'googleProductCategory':
						product_dic['googleProductCategory'],
				'gtin':
						product_dic['gtin'],
				'price': {
						'value': product_dic['price'],
						'currency': 'USD'
				},
				'shipping': [{
						'country': 'US',
						'service': 'Free shipping',
						'price': {
								'value': '0',
								'currency': 'USD'
						}
				}],
				'shippingWeight': {
						'value': product_dic['weight'],
						'unit': 'lb'
				}
		}
	elif mode.lower() == 'update_inven':
		product = {
				'offerId':
						product_dic['offerId'],
				'price': {
						'value': product_dic['price'],
						'currency': 'USD'
				},
				'availability':
						'in stock' if product_dic['quantity']>0 else 'out of stock'
		}
	elif mode.lower() == 'update_expired':
		product = {
				'offerId':
						_constants.CHANNEL+':'+_constants.CONTENT_LANGUAGE+':'+_constants.TARGET_COUNTRY+':shopify_US_'+product_dic['productid']+'_'+product_dic['variantid'],
				'contentLanguage':
						_constants.CONTENT_LANGUAGE,
				'targetCountry':
						_constants.TARGET_COUNTRY,
				'channel':
						_constants.CHANNEL,
				'expirationDate':
						time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(time.time()+3600*24*int(30))),
				'availability':
						'in stock' if int(product_dic['quantity'])>0 else 'out of stock',
				'price': {
						'value': product_dic['price'],
						'currency': 'USD'
				},
				'link':
						product_dic['link'],
				'title':
						product_dic['title'][:130].encode('utf-8').decode(encoding='UTF-8',errors='strict'),
				'condition':
						product_dic['condition'],
				'brand':
						product_dic['brand'],
		}
		if product_dic['gtin']:
			product['gtin'] = product_dic['gtin']
		if not product_dic['gtin']:
			product['mpn'] = product_dic['sku'].split('-')[-1]
		
	return product

def product_insert(argv,products_list,mode):
	# Authenticate and construct service.
	service, config, _ = shopping_common.init(argv, __doc__)
	merchant_id = config['merchantId']

	batch = {'entries': []}
	position = 0
	while position<len(products_list):
		product_list = products_list[position:position+5]
		position +=5
		for i in range(BATCH_SIZE):
			if len(product_list)>i:
				product = create_product(config,product_list[i],mode)
				# Add product to the batch.
				batch['entries'].append({
						'batchId': i,
						'merchantId': merchant_id,
						'method': 'insert',
						'product': product
				})
		try:
			request = service.products().custombatch(body=batch)
			try:
				result = request.execute()
			except:
				traceback.print_exc()

			if result['kind'] == 'content#productsCustomBatchResponse':
				entries = result['entries']
				for entry in entries:
					if not shopping_common.json_absent_or_false(entry, 'product'):
						product = entry['product']
						print('Product with offerId "%s" was update.' %
									(product['offerId']))
					elif not shopping_common.json_absent_or_false(entry, 'errors'):
						print (entry['errors'])
			else:
				print ('There was an error. Response: %s' % (result))
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
product_insert(sys.argv,products_list,'update_expired')
