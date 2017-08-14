from configparser import ConfigParser
import os,glob,codecs
from datetime import datetime, date, timedelta
import calendar,time,requests,json
import contextlib,dropbox,re

def get_path(root_dir,directory_list):
	dir = root_dir.rstrip('/')+'/'+'/'.join(directory_list)+'/'
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir

def get_config_value(root_path,section_name,key):
	config_dir=get_path(root_path,['app','config'])
	config_path=config_dir+'config.ini'
	config=ConfigParser()
	config.read(config_path)
	return config.get(section_name,key)

def set_config_value(root_path,section_name,key,value):
	config_dir=get_path(root_path,['app','config'])
	config_path=config_dir+'config.ini'
	config=ConfigParser()
	config.read(config_path)
	try:
		config.set(section_name,key,value)
	except:
		try:
			config.add_section(section_name)
		except:
			pass
		config.set(section_name,key,value)
	config.write(open(config_path,'w'))

def get_files_from_filedir(filedir):
	files_list = []
	for file in os.listdir(filedir):
		if '.txt' in file:
			files_list.append(file)
	return files_list

def get_source_asins_from_asindir(asindir):
	source_asins = {}
	for f in (open(asindir+i) for i in os.listdir(asindir) if '.txt' in i):
		asins=f.read().splitlines()
		for asin in asins:
			if asin:
				source_asins[asin] = True
	return source_asins

def get_asins_from_asindir(asindir):
	asins_list = []
	for f in (open(asindir+i) for i in os.listdir(asindir) if '.txt' in i):
		asins=f.read().splitlines()
		for asin in asins:
			if asin:
				asins_list.append(asin)
	return asins_list

def write_to_file(file_path,content):
	f_out = open(file_path,'a')
	f_out.write(content+'\n')
	f_out.close()

def get_filter_asins_from_filter_asindir(filter_asindir):
	asinsdic={}
	for f in (codecs.open(filter_asindir+i,encoding='iso-8859-1') for i in os.listdir(filter_asindir) if '.txt' in i):
		asins=f.read().splitlines()
		for asin in asins:
			if asin:
				asinsdic[convert_isbn(asin)]=True
	return asinsdic
def get_filter_asins_from_filter_invendir(filter_invendir):
	asinsdic={}
	for f in (codecs.open(filter_invendir+i,encoding='iso-8859-1') for i in os.listdir(filter_invendir) if '.txt' in i):
		lines=f.read().splitlines()
		for line in lines:
			try:
				asin=line.split('\t')[1]
			except:
				continue
			asinsdic[asin]=True
	return asinsdic
def get_keep_asins_from_keep_asindir(keep_asindir):
	asinsdic={}
	for f in (open(keep_asindir+i) for i in os.listdir(keep_asindir) if '.txt' in i):
		asins=f.read().splitlines()
		for asin in asins:
			asinsdic[asin]=True
	return asinsdic
def get_keep_asins_from_inven_dir(keep_invendir):
	asinsdic={}
	for f in (open(keep_invendir+i) for i in os.listdir(keep_invendir) if '.txt' in i):
		lines=f.read().splitlines()
		for line in lines:
			try:
				asin=line.split('\t')[1]
			except:
				continue
			asinsdic[asin]=True
	return asinsdic
def get_products(inven_file,used_signs,filter_asins):
	products={}
	first_line=inven_file.readline()
	lines=inven_file.read().splitlines()
	for line in lines:
		sku,asin,price,quantity=line.split('\t')[:4]
		if filter_asins.get(asin,False):
			continue
		if products.get(asin,None)==None:
			products[asin]={}
		if is_used(sku,used_signs):
			products[asin]['used_price']=price
		else:
			products[asin]['new_price']=price
	return products

def get_asins(source_asins,filter_asins,type='book'):
	asinsdic = {}
	for asin in source_asins:
		if filter_asins.get(asin,False):
			continue
		if type=='book':
			if asinsdic.get(asin)==None and 'B' not in asin:
				asinsdic[asin]=True
		elif type=='product':
			if asinsdic.get(asin)==None and 'B' in asin:
				asinsdic[asin]=True
	return [k for k in asinsdic.keys()]

def write_to_asinfile(file_name,asin_path,asins,type='book'):
	file_name = file_name+'_'+datetime.strftime(datetime.now(),'%Y%m%d')
	file_number = 1
	count = 0
	file_path = asin_path+str(file_name)+'_'+str(file_number)+'.txt'
	#print(file_path)
	f_out = open(file_path,'w')
	for asin in asins:
		if type=='book':
			if asin and 'B' not in asin:
				print(asin)
				count +=1
				f_out.write(asin+'\n')
		elif type=='product':
			if asin and 'B' in asin:
				#print(asin)
				count +=1
				f_out.write(asin+'\n')
		if count%300000000000==0:
			f_out.close()
			file_number +=1
			file_path = asin_path+str(file_name)+'_'+str(file_number)+'.txt'
			f_out = open(file_path,'w')
	f_out.close()
	print(count)
def get_dir(root_dir,directory_list):
	dir = root_dir.rstrip('/')+'/'+'/'.join(directory_list)+'/'
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir

def sku_need_note(sku,used_signs):
	return any(used_sign in sku for used_sign in used_signs)
# def write_to_file(root_dir,input_file,file_title,row_count):
#     #inven_file.readline()
#     count = 1
#     file_number = 100
#     output_file_path = get_dir(root_dir,['src','shuju'])+'x'+str(file_number)[1:]+'shuju.txt'
#     output_file = open(output_file_path,'w')
#     output_file.write(file_title)
#     for line in input_file:
#         items=line.split('\t')
#         print(items)
#         if count%row_count==0:
#             output_file.close()
#             file_number +=1
#             output_file = open(output_file_path,'w')
#             output_file.write(file_title)
#         output_file.write(line)
#         count +=1
#     output_file.close()
def get_accounts(input_file):
	accounts = set()
	for account in input_file:
		accounts.add(account.strip())
	return list(accounts)
def remove_files_from_dir(file_dir):
	if len(os.listdir(file_dir)):
		for root, dirs, files in os.walk(file_dir, False):
			for name in files:
				os.remove(os.path.join(root, name))

def convert_isbn(productid):
	return '0'*(10-len(productid))+str(productid)
def is_isbn(asin):
	pattern='(\d{9}[\d|x|X]{1})'
	if re.match(pattern,asin):
		return True
	else:
		return False

def find_newest_file(dir, prefix=""):
	newest = max(glob.iglob("%s/%s*"%(dir,prefix)), key=os.path.getmtime)
	return newest
def find_newest_files(dir, prefix=""):
	files = glob.glob("%s/%s*" % (dir, prefix))
	files.sort(key=lambda x: os.path.getmtime(x))
	return files
def get_asins_from_file(file_path):
	asinsdic={}
	f = codecs.open(file_path,encoding='iso-8859-1')
	asins=f.read().splitlines()
	for asin in asins:
		asinsdic[asin]=True
	return asinsdic

def get_asins_from_invenfile(file_path):
	asinsdic={}
	f = codecs.open(file_path,encoding='iso-8859-1')
	lines=f.read().splitlines()
	for line in lines:
		try:
			asinsdic[asin]=line.split('\t')[1]
		except:
			continue
		asinsdic[asin] = True
	return asinsdic

def get_month_range(start_date=None):
	if start_date is None:
		start_date = date.today().replace(day=1)
	_, days_in_month = calendar.monthrange(start_date.year, start_date.month)
	end_date = start_date + timedelta(days=days_in_month)
	return (start_date, end_date)
def get_month_days():
	days_list = []
	a_day = timedelta(days=1)
	first_day, last_day = get_month_range()
	while first_day < last_day:
		#print(first_day)
		days_list.append(first_day.strftime("%Y-%m-%d"))
		first_day += a_day
	return days_list
def get_month_week():
	week_list = []
	a_day = timedelta(days=1)
	first_day, last_day = get_month_range()
	while first_day < last_day:
		#print(first_day)
		week_list.append(first_day.strftime("%a"))
		first_day += a_day
	return week_list

def get_sku_pattern(sku):
	if '-' in sku:
		code,sku_pattern=sku[::-1].split('-',1)
		code=code[::-1]
		sku_pattern='%s-%s' % (sku_pattern[::-1],code[0])
	else:
		sku_pattern='other'
	return sku_pattern

def is_product(sku):
	product_list = ['toy','kit','spor','home','tool','heal','beau','ealth','wire','kichen','shoes',\
	'compo','watch','hardware','grocery','jewel','b aby','be auty','hoktsp','video','tchen','t oy',\
	'pet','elec','out','food','office','art','acce','pro','ban','baby','auto']
	if any(product in sku.lower() for product in product_list):
		return True
	else:
		return False

def encrypt(key, s):
	b = bytearray(str(s).encode("gbk"))
	n = len(b) # Ã¦Â±â€šÃ¥â€¡Âº b Ã§Å¡â€žÃ¥Â­â€”Ã¨Å â€šÃ¦â€¢Â°
	c = bytearray(n*2)
	j = 0
	for i in range(0, n):
		b1 = b[i]
		b2 = b1 ^ key # b1 = b2^ key
		c1 = b2 % 16
		c2 = b2 // 16 # b2 = c2*16 + c1
		c1 = c1 + 65
		c2 = c2 + 65 # c1,c2Ã©Æ’Â½Ã¦ËœÂ¯0~15Ã¤Â¹â€¹Ã©â€”Â´Ã§Å¡â€žÃ¦â€¢Â°,Ã¥Å Â Ã¤Â¸Å 65Ã¥Â°Â±Ã¥ÂËœÃ¦Ë†ÂÃ¤Âºâ€ A-P Ã§Å¡â€žÃ¥Â­â€”Ã§Â¬Â¦Ã§Å¡â€žÃ§Â¼â€“Ã§Â Â
		c[j] = c1
		c[j+1] = c2
		j = j+2
	return c.decode("gbk")
def decrypt(key, s):
	c = bytearray(str(s).encode("gbk"))
	n = len(c) # Ã¨Â®Â¡Ã§Â®â€” b Ã§Å¡â€žÃ¥Â­â€”Ã¨Å â€šÃ¦â€¢Â°
	if n % 2 != 0 :
		return ""
	n = n // 2
	b = bytearray(n)
	j = 0
	for i in range(0, n):
		c1 = c[j]
		c2 = c[j+1]
		j = j+2
		c1 = c1 - 65
		c2 = c2 - 65
		b2 = c2*16 + c1
		b1 = b2^ key
		b[i]= b1
	try:
		return b.decode("gbk")
	except:
		return "failed"
def get_marketplaceid(region='US'):
	marketplaces = {
	"CA" : "A2EUQ1WTGCTBG2",
	"US" : "ATVPDKIKX0DER",
	"DE" : "A1PA6795UKMFR9",
	"ES" : "A1RKKUPIHCS9HS",
	"FR" : "A13V1IB3VIYZZH",
	"IN" : "A21TJRUUN4KGV",
	"IT" : "APJ6JRA9NG5V4",
	"UK" : "A1F83G8C2ARO7P",
	"JP" : "A1VC38T7YXB528",
	"CN" : "AAHKV2X7AFYLW",
	"MX" : "A1AM78C64UM0Y8",
	}
	return marketplaces.get(region.upper())

def get_amazon_base_url(region='US'):
	region = {
	'CA': 'ca',
	'DE': 'de',
	'ES': 'es',
	'FR': 'fr',
	'IN': 'in',
	'IT': 'it',
	'JP': 'co.jp',
	'UK': 'co.uk',
	'US': 'com',
	'CN': 'cn'
	}
	return 'http://www.amazon.'+region.get(region.upper())+'/'

def requests_config(url,data_dic):
	try_times=0
	config_dic={}
	r=None
	while try_times<5:
		try:
			r = requests.post(url,data=data_dic,timeout=600)
			#print(r.text)
			if r.status_code==200:
				data_list = json.loads(r.text)
				#print(data_list)
				for data in data_list:
					config_dic[data.get('c_key')] = data.get('c_value')
				break
		except:
			print('I am trying to requests data to server...')
			time.sleep(1)
			try_times+=1
	return config_dic

def get_mws(conn,account):
	mws_dic = {}
	cursor = conn.cursor()
	data = cursor.execute('SELECT accountid FROM data_account where account="%s"' % account)
	result = cursor.fetchone()
	if result:
		a_id= result[0]
		cursor.execute('select s_id,a_key,s_key from data_sinfo where a_id= '+str(a_id))
		res_mws = cursor.fetchone()
		if res_mws:
			mws_dic['sellerid']=res_mws[0]
			mws_dic['accesskey']=res_mws[1]
			mws_dic['secretkey']=res_mws[2]
		conn.commit()
		cursor.close
	return mws_dic

def get_account_status(code):
	astatus_dic = {1:'Active',2:'Inactive',3:'Under View',4:'Restricted'}
	return astatus_dic.get(code,code)
def get_account_info(conn,account):
	is_pro = False
	source=astatus=currentstatus=cdate=feedback30days=rating30days=''
	account_info = {}
	cursor = conn.cursor()
	data = cursor.execute('select source,astatus,feedback30days,rating30days from data_account where account="%s"' % account)
	result = cursor.fetchone()
	if result:
		source,astatus,feedback30days,rating30days = result
	data2= cursor.execute('select sku from data_block where dstatus !=-1 and account ="%s"' % account)
	result2 = cursor.fetchall()
	if result2:
		for sku in result2:
			if is_product(sku[0]):
				is_pro = True
				break
	data3 = cursor.execute('select currentstatus,cdate from data_accountalter where account="%s" ORDER BY `alterid` ASC LIMIT 1' % account)
	result3 = cursor.fetchone()
	if result3:
		currentstatus,cdate = result3
	conn.commit()
	cursor.close
	account_info['source'],account_info['astatus'],account_info['is_product'],account_info['currentstatus'],account_info['cdate'],account_info['feedback30days'],account_info['rating30days']=\
	source,astatus,is_pro,currentstatus,cdate,feedback30days,rating30days
	return account_info

def get_spreadsheet_name(source,account,last_month=False):
	month=time.localtime().tm_mon
	if last_month and month!=1:
		month = month-1
	elif last_month:
		month = 12
	month=str(100+int(month))[1:]
	year=str(time.localtime().tm_year)
	y_m = year+month
	source_type={1:'US',2:'UK',3:'CA'}
	region = account[-2:].upper()
	if source_type.get(source,'Other') =='US' and region =='US':
		spreadsheet_name = 'US Product To US-'+y_m
	elif source_type.get(source,'Other') =='US':
		spreadsheet_name = 'US Product Export-'+y_m
	elif source_type.get(source,'Other') =='UK':
		spreadsheet_name = 'UK Product To UK And Export-'+y_m
	elif source_type.get(source,'Other') =='Other':
		spreadsheet_name = 'Other Product-'+y_m
	return spreadsheet_name

def get_date(lastdays=0):
	return time.strftime("%Y-%m-%d",time.localtime(time.time()-3600*24*int(lastdays)))

def get_time():
	return time.strftime("%H:%M:%S")

def get_inven_analysis(des_dir,file_name):
	fenxi_data_dic = {}
	readfile = codecs.open(des_dir+file_name+'.txt',encoding='iso-8859-1')
	readfile.readline()
	product_type_dic ={}
	product_count_dic ={}
	count_all = count_pro=0
	for line in readfile:
		try:
			items=line.strip().split('\t')
			sku=items[0]
			quantity = int(items[3])
		except:
			continue
		count_all +=1
		sku_type = get_sku_pattern(sku)
		if not is_product(sku):
			continue
		count_pro +=1
		product_type_dic[sku_type] = {}
		try:
			product_count_dic[sku_type+'_count'] +=1
		except:
			product_count_dic[sku_type+'_count'] = 0
			product_count_dic[sku_type+'_count'] +=1
		product_type_dic[sku_type]['count'] = product_count_dic[sku_type+'_count']
		if not quantity:
			try:
				product_count_dic[sku_type+'_quantity0'] +=1
			except:
				product_count_dic[sku_type+'_quantity0'] = 0
				product_count_dic[sku_type+'_quantity0'] +=1
			product_type_dic[sku_type]['quantity0'] = product_count_dic[sku_type+'_quantity0']
	return product_type_dic,count_all,count_pro

def get_account_status_from_sheet(conn,account,status):
	status_map = {'Active':1,'Inactive':2,'Under Review':3,'Restricted':4}
	status_dic = {'UA':status_map['Under Review'],'UI':status_map['Inactive'],'AA':status_map['Active'],\
				  'Suspended':status_map['Inactive']}
	cursor = conn.cursor()
	data= cursor.execute('select sku from data_block where dstatus !=-1 and account ="%s"' % account)
	result = cursor.fetchall()
	conn.commit()
	cursor.close
	# astatus = get_account_info(conn,account)['astatus']
	# if astatus ==2:
	# 	status_dic['AI'] = status_map['Active']
	# elif astatus ==1:
	if result:
		status_dic['AI'] = status_map['Inactive']
	else:
		status_dic['AI'] = status_map['Active']
	return status_dic.get(status,'')

def update_account_metric(conn,table,fields_dic,account,where=''):
    cursor = conn.cursor()
    sql = 'update ' +table+' set '
    for field in fields_dic:
        if str(fields_dic[field]).strip():
            sql +=field+'="'+str(fields_dic[field])+'",'
    sql = sql[:-1]
    if where:
        where = ' and '+where
    sql +=' where account="'+account+'"'+where
    #print(sql)
    cursor.execute(sql)
    conn.commit()
    cursor.close

def insert_account_metric(conn,table,fields_dic):
	cursor = conn.cursor()
	sql = 'insert into ' +table
	fields_list = []
	values_list = []
	for field in fields_dic:
		fields_list.append(field)
		values_list.append('"'+str(fields_dic[field])+'"')
	str_fields = ','.join(fields_list)
	str_values = ','.join(values_list)
	sql +=' ('+str_fields+') values ('+str_values+')'
	#print(sql)
	cursor.execute(sql)
	conn.commit()
	cursor.close

def get_sales_channel_code(region):
	channel_region = {'Amazon.co.uk':'UK','Amazon.de':'DE','Amazon.fr':'FR','Amazon.es':'ES',\
	'Amazon.it':'IT','Amazon.co.jp':'JP','Amazon.com':'US','Amazon.ca':'CA',\
	'Amazon.com.mx':'MX','Amazon.in':'IN'}
	return channel_region.get(region,region)
def analysis_orders_from_dir(orderdir,region):
	order_analysis = {}
	orderid_unique = {}
	for file_name in os.listdir(orderdir):
		if region.lower()+'.txt' in file_name:
			file = codecs.open(orderdir+file_name,encoding='iso-8859-1')
			orders=file.read().splitlines()
			file_header = {}
			for order in orders:
				content_dic = {}
				rows=order.strip('\n').strip('\r').split('\t')
				#print(rows)
				if 'order-id' in rows:
					for field in rows:
						file_header[field] = rows.index(field)
				if file_header and 'order-id' not in rows:
					for field in file_header:
						content_dic[field] = rows[file_header[field]]
				else:
					continue
				if not content_dic['sales-channel']:
					content_dic['sales-channel']=region
				orderid,purchase_date,sku,channel=content_dic['order-id'],content_dic['purchase-date'],content_dic['sku'],get_sales_channel_code(content_dic['sales-channel'])
				if orderid_unique.get(orderid):
					continue
				purchase_date = purchase_date[0:10]
				sku_pattern = get_sku_pattern(sku)
				if order_analysis.get(channel,False)==False:
					order_analysis[channel] = {}
				if order_analysis[channel].get(purchase_date,False)==False:
					order_analysis[channel][purchase_date] = {}
				if order_analysis[channel][purchase_date].get('total_orders_product',False) ==False:
					order_analysis[channel][purchase_date]['total_orders_product'] = 0
				if is_product(sku):
					order_analysis[channel][purchase_date]['total_orders_product'] +=1
				if order_analysis[channel][purchase_date].get('total_orders',False) ==False:
					order_analysis[channel][purchase_date]['total_orders'] = 0
				order_analysis[channel][purchase_date]['total_orders'] +=1
				if order_analysis[channel][purchase_date].get(sku_pattern,False) ==False:
					order_analysis[channel][purchase_date][sku_pattern] =0
				order_analysis[channel][purchase_date][sku_pattern] +=1
				orderid_unique[orderid] = True
	return order_analysis

def get_value_from_dic(d,l):
	for k in l:
		try:
			d=d[k]
		except:
			return 0
	return d

def get_marketplaces():
	return ['US','CA','UK','DE','FR','ES','IT','MX','IN','JP']

def download(dbx, download_path,file_folder_list, name):
	path = '/'+'/'.join(file_folder_list)+'/'+name
	with stopwatch('download'):
		try:
			res = dbx.files_download_to_file(download_path, path, rev=None)
		except dropbox.exceptions.HttpError as err:
			print('*** HTTP error', err)
			return None
	return res

def upload(dbx, fullname, des_folder_list, name, overwrite=False):
	path = '/'+'/'.join(des_folder_list)+'/'+name
	mode = (dropbox.files.WriteMode.overwrite
			if overwrite
			else dropbox.files.WriteMode.add)
	mtime = os.path.getmtime(fullname)
	with open(fullname, 'rb') as f:
		data = f.read()
	with stopwatch('upload %d kb' % float(len(data)/1024)):
		try:
			res = dbx.files_upload(
				data, path, mode,
				client_modified=datetime(*time.gmtime(mtime)[:6]),
				mute=True)
		except dropbox.exceptions.ApiError as err:
			print('*** API error', err)
			return None
	return res

@contextlib.contextmanager
def stopwatch(message):
	t0 = time.time()
	try:
		yield
	finally:
		t1 = time.time()
		print('Total elapsed time for %s: %.3f' % (message, t1 - t0))

def ftp_upload_inven(server,username,passwd,acc_no,filename,file_dir):
	ftp = ftplib.FTP(server,username,passwd)
	#ftp.set_debuglevel(2)
	remote_path = "/src/inventory/"
	try:
		ftp.cwd(remote_path)
	except:
		try:
			ftp.mkd(remote_path)
		except:
			print('cant make directory')
			exit()

	ftp.cwd(remote_path)
	bufsize = 10240
	fh = open(file_dir+filename+'.txt', 'rb',bufsize)
	ftp.storbinary('STOR '+filename+'.txt', fh)
	fh.close()
	#ftp.set_debuglevel(0)
	ftp.quit()

def ftp_upload_order(server,username,passwd,acc_no,filename,file_dir):
	ftp = ftplib.FTP(server,username,passwd)
	ftp.set_debuglevel(2)
	remote_path = "/src/orders/"
	try:
		ftp.cwd(remote_path)
	except:
		try:
			ftp.mkd(remote_path)
		except:
			print('cant make directory')
	ftp.cwd(remote_path)
	bufsize = 10240
	fh = open(file_dir+filename+'.txt', 'rb',bufsize)
	ftp.storbinary('STOR '+filename+'.txt', fh)
	fh.close()
	#ftp.set_debuglevel(0)
	ftp.quit()

def get_cat(sku):
	product_list = ['toy','kit','spor','home','tool','heal','beau','pet','elec','out','food','office','art','acc','pro','ban','baby','auto']
	count = 0
	for product in product_list:
		if product in sku.lower():
			return product
			break
		count +=1
		if count==len(product_list):
			return 'other'

def found_pack_of(title):
    pat = [
    # from the head of line
    '^pack of \d+[,]*', # pack of 10,
    '^\d+ pack of ', # '10 pack of '
    '^twin pack of ', # 'Twin pack of '
    '^\d+ Pair[s]{0,1} Pack of ', # 12 Pair Pack of 
    '^\d+\-Pair[s]{0,1} Pack of ', # 3-Pair Pack of
    '^\d+ [a-z]{3,5} Pack of ', # 3 Pcs Pack of 
    '^\d+ [a-z]{3,5} [a-z]{3,5} Pack of ', # 5 Piece Value Pack of 
    '^\d+ [a-z]{3,5} [a-z]{3,5} [a-z]{3,5} Pack of ', # 5 Pairs Mix Color Pack of
    '^(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) \(\d+\) pack of ', # Ten (10) Pack of
    '^\d+ \((one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\) pack of ', # 1 (One) Pack of
    '^\[\d+ pack\]', # [2 Pack]
    '^\(\d+\) pack ', # (3) pack
    '^\d+[\- ]+pack ', # 3 pack | 3-pack
    '^pack \d+ ', # pack 2

    # from the end of line
    '[, ]*[\(]*pack of \d+[\)]*$',
    '\(pack of \d+ [a-z]{3,6}\)$', # (Pack of 11 Colors)
    'pack of \([ ]*\d+pcs[ ]*\)$', # Pack of ( 50pcs )
    '\[pack of \d+[ ]*\]$', # [PACK OF 2 ]
    '\d+[\- ]+pack[\!]*$', # 3 pack | 3-pack | 3 pack!!
    '\[[ ]*\d+ pack[ ]*\]$', # [ 2 Pack]
    '\{[ ]*\d+ pack[ ]*\}$', # {2 Pack}
    '\([ ]*\d+[ ]*pack[ ]*\)$', # (2Pack)|(2 Pack)|( 2 Pack)
    ' pack \d+$', # pack 3

    # from the head to the end of line
    '\d+\-pack of ', # '2-Pack of '
    '(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)-pack of ', # 'Two-Pack of '
    ' pack of \- \d+', # ' Pack Of - 3'
    '\d+ pack of', # '2 Pack of '
    '\(pack of \d+\)', # (pack of 2)
    ' Pack of \d+pairs', # Pack of 5pairs
    ' Pack of \d+pcs', # Pack of 12pcs
    '\d+pcs pack of ', # 12pcs Pack of
    '\d+pc pack of ', # 6pc Pack of 
    '[, ]{1}pack of \d+[,]{0,1}',
    '[ -]*Pack of \d+ Dozen' # - Pack of 1 Dozen
    '\(\d+, Assorted \d+ Pack\)', # (5, Assorted 8 Pack)
    'pack of (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) \(\d+\) ', # Pack of TWELVE (12)
    '[\(]*pack of (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)[\)]*', # (Pack of Three) | Pack of Three
    '(one|two|three|four|five|six|seven|eight|nine|ten) pack of ', # three pack of
    'pack of \(\d+\) (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) ', # Pack of (4) Four
    'pack of \(\d+\)', # Pack of (8) 
    'pack of \d+[ ,-]*', # 'Pack of 6 - ' | 'Pack of 6 ' | 'Pack of 6, ' 
    '\d+ [a-z]{3,5} Pack of ', # 100 Bulk Pack of
    '\(\d+[\-\~ ]+Pack[\!]*\)', # (3 Pack)|(3-Pack)|(3 pack!)
    '\(Pack[\- ]+\d+[\!]*\)', # (Pack 2)|(Pack-2)|(Pack 2!)
    '\d+[\-\~ ]+Pack ', # 3-pack | 3 -pack
    '\(\d+ per pack\)', # (2 Per Pack)
    '\(Package of \d+[ ]*\)', # (Package of 3 )
    ]

    pattern = re.compile("|".join(pat), re.I)
    
    title = pattern.sub('',title)
    return title

