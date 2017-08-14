import os
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import time

class mygspread():
	def __init__(self,authpath):
		self.authpath=authpath
		self.cell_list=[]
	def setup(self):
		json_key = json.load(open(self.authpath))
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
		try:
			self.gc = gspread.authorize(credentials)
			sheet=self.gc.open(self.sheet_name)
			self.worksheet=sheet.worksheet(self.worksheet_name)
		except IOError:
			raise Exception('error')
	def set_sheet(self,sheet_name):
		self.sheet_name=sheet_name
	def set_worksheet(self,worksheet_name):
		self.worksheet_name=worksheet_name
	def get_current_position(self):
		self.position=self.worksheet.cell(1,1).value
		return self.position	
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
				self.setup()
		print("row %d"%x)
	def set_value(self,x,y,value):
		try:
			self.worksheet.update_cell(x,y,value)
		except:
			try:
				self.setup()
				self.worksheet.update_cell(x,y,value)
			except:
				pass
		print("row %d" % x)
	def update_values(self):
		try:
			self.worksheet.update_cells(self.cell_list)
		except:
			self.setup()
			self.worksheet.update_cells(self.cell_list)

		
