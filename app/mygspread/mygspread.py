import json
import gspread
#from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.service_account import ServiceAccountCredentials
import time

class mygspread():
	def __init__(self,authpath):
		self.cell_list=[]
		scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
		credentials = ServiceAccountCredentials.from_json_keyfile_name(authpath, scope)
		while True:
			try:
				self.gc = gspread.authorize(credentials)
				#print(dir(self.gc))
				break
			except IOError:
				raise Exception('error')
				time.sleep(1)
	def create_spreadsheet(self,name):
		self.sheet = self.gc.create(name)
		self.sheet.share('bujuninchrist@gmail.com', perm_type='user', role='writer')

	def del_spreadsheet(self,file_id):
		self.gc.del_spreadsheet(file_id)

	def open_spreadsheet(self,name,gtype=''):
		if gtype.lower()=='url':
			self.sheet=self.gc.open_by_url(name)
		elif gtype.lower()=='key':
			self.sheet=self.gc.open_by_key(name)
		else:
			self.sheet=self.gc.open(name)

	def setup(self):
		self.worksheet=self.sheet.worksheet(self.worksheet_name)

	def get_worksheets_from_sheet_name(self):
		worksheet_list = []
		worksheets = self.sheet.worksheets()
		for worksheet in worksheets:
			worksheet_list.append(worksheet.title)
		return worksheet_list
	def worksheets(self):
		return self.sheet.worksheets()

	def set_worksheet(self,worksheet_name):
		self.worksheet=self.sheet.worksheet(worksheet_name)

	def get_current_value(self,x,y):
		return self.worksheet.cell(x,y).value

	def set_start_row(self):
		self.start_row=4

	def set_time_row(self):
		self.time_row=2

	def add_cell_list(self,x,y,value):
		while True:
			try:
				cell=self.worksheet.cell(x,y)
				cell.value=value
				self.cell_list.append(cell)
				break
			except:
				time.sleep(1)
		print("row %d"%x)

	def update_cell(self,x,y,value):
		self.worksheet.update_cell(x,y,value)
		#print("row %d" % x)

	def update_cells(self,range_list,value_list):
		row1,col1,row2,col2=range_list
		while True:
			n = 0
			try:
				cell_list = self.worksheet.range(row1,col1,row2,col2)
				for c, v in zip(cell_list, value_list):
					c.value = v
				self.worksheet.update_cells(cell_list)
				break
			except:
				n +=1
				time.sleep(n*0.5)

	def get_col_values(self,col_index):
		return self.worksheet.col_values(col_index)

	def get_row_values(self,row_index):
		return self.worksheet.row_values(row_index)

	def get_all_values(self):
		list_of_lists = self.worksheet.get_all_values()
		return list_of_lists

	def find_cell(self,string):
		cell = self.worksheet.find(string)
		return cell

	def create_worksheet(self,title,rows="100",cols="20"):
		self.sheet.add_worksheet(title=title, rows=rows, cols=cols)

	def del_worksheet(self,worksheet_name):
		self.set_worksheet(worksheet_name)
		self.sheet.del_worksheet(self.worksheet)

	def add_values_to_worksheet(self,watch_file,position_index):
		input_watch_file = open(watch_file)
		position_index = position_index
		if not self.get_current_position():
			self.set_value(1,1,1)
		self.set_value(3,1,'SKU')
		self.set_value(3,2,'ASIN')
		for line in input_watch_file:
			item = line.rstrip('\n').split('\t')
			try:
				sku,asin = item
			except:
				continue
			if sku and asin:
				position_index +=1
				self.set_value(position_index,1,sku)
				self.set_value(position_index,2,asin)
		input_watch_file.close()

	def del_row(self,row_pos):
		self.worksheet.delete_row(row_pos)

	def add_row(self,num):
		self.worksheet.add_rows(num)

	def row_count(self):
		return self.worksheet.row_count

	def add_col(self,num):
		self.worksheet.add_cols(num)

	def col_count(self):
		return self.worksheet.col_count

	def insert_row(self,values,index=1):
		self.worksheet.insert_row(values,index)
		
	def insert_col(self,values,index=1):
		self.worksheet.insert_col(values,index)

	def download(self, spreadsheet, gid=0, format="csv"):
		url_format = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=%s&gid=%i"
		headers = {
			"Authorization": "GoogleLogin auth=" + self.get_auth_token(),
			"GData-Version": "3.0"
		}
		req = urllib2.Request(url_format % (spreadsheet.key, format, gid), headers=headers)
		return urllib2.urlopen(req)

	def export(self,format='csv'):
		self.worksheet.export(format)



