import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

class InputGsheet():
	def __init__(self, SHEET_ID):
		self.SERVICE_SCOPE = ["https://spreadsheets.google.com/feeds"
		,'https://www.googleapis.com/auth/spreadsheets',
		"https://www.googleapis.com/auth/drive.file",
		"https://www.googleapis.com/auth/drive"]
		self.SERVICE_ACCOUNT_KEY = '<key json file>'
		self.SHEET_NAME = 'budget-copilot'
		# CREDENTIAL START
		self.cred = service_account.Credentials.from_service_account_file(
			filename=self.SERVICE_ACCOUNT_KEY, scopes=self.SERVICE_SCOPE)
		# CREDENTIAL END
		self.SHEET_ID = SHEET_ID
		self.service = build('sheets', 'v4', credentials=self.cred)
		self.sheet = self.service.spreadsheets()

	# create new sheet
	def createSheet(self):
		sheet_properties = self.sheet.get(
			spreadsheetId=self.SHEET_ID).get('sheets')
		exist = False
		for item in sheet_properties:
			if item.get("properties").get('title') == self.SHEET_NAME:
				exist = True
		if not exist:
			body = {'requests': [
			    {
			        'addSheet': {
			            'properties': {
			                'title': self.SHEET_NAME
			            }
			        }
			    }]}
			self.sheet.batchUpdate(spreadsheetId=self.SHEET_ID, body=body).execute()

	# add column name to a new blank sheet
	def InitSheet(self):
		def clearsheet():
			allRange = '{}'.format(self.SHEET_NAME)
			self.sheet.values().clear(spreadsheetId=self.SHEET_ID,
				range=allRange).execute()
		def initColumnName():
			fistRow = '{}!A1:D1'.format(self.SHEET_NAME)
			column_name = [['Date', 'Title', 'Cost', 'Category']]
			self.sheet.values().update(
				spreadsheetId=self.SHEET_ID,
				range=fistRow,
				valueInputOption='RAW', body={
						"values" : column_name
					}).execute()
		clearsheet()
		initColumnName()

    # return settlement
	def settlement(self):
		range = "{}!A:D".format(self.SHEET_NAME)
		result = self.sheet.values().get(
			spreadsheetId=self.SHEET_ID,
			range=range).execute()
		cell_value = result.get('values', [])
		df = pd.DataFrame(cell_value)
		df.columns = ['date', 'cost', 'title', 'category']
		df = df.iloc[1:]
		df['cost'] = df['cost'].apply(pd.to_numeric)
		first_date = df.iloc[0, 0]
		last_date = df.iloc[-1, 0]
		total = df.iloc[:,1].sum(axis=0)
		groupped_df = df.groupby('category')['cost'].sum()
		settle_dict = {
			'食': 0,
			'樂': 0,
			'行': 0,
			'其他': 0
		}
		for index in groupped_df.index:
			settle_dict[index] = groupped_df[index]
		return [first_date, last_date, total, settle_dict]

	# count row of data
	def countRow(self):
		lastIndex = len(self.sheet.values().get(
			spreadsheetId=self.SHEET_ID, range=self.SHEET_NAME
			).execute().get('values', []))
		return lastIndex

	def deleteLastRow(self):
		sheet_id = None
		spreadsheet = self.sheet.get(spreadsheetId=self.SHEET_ID).execute()
		for _sheet in spreadsheet['sheets']:
			if _sheet['properties']['title'] == self.SHEET_NAME:
				sheet_id = _sheet['properties']['sheetId']
		# google sheet index => 0 based
		last_row = self.countRow() - 1
		body = {
				"requests": [
				{
					"deleteDimension":
					{
						"range": {
							"sheetId": sheet_id,
							"dimension": "ROWS",
							"startIndex": last_row,
							"endIndex": last_row+1
						}
					}
				}
				]
			}
		self.sheet.batchUpdate(
			spreadsheetId=self.SHEET_ID, body=body).execute()


	def writeInKeeping(self, date, cost, title, category):
		def writeDate():
			inputValues = [[date, cost, title, category]]
			range_ = '{}!A:D'.format(self.SHEET_NAME)
			self.sheet.values().append(
				spreadsheetId=self.SHEET_ID,
				range = range_,
				valueInputOption='RAW',
				insertDataOption='INSERT_ROWS',
				body={'values' : inputValues}).execute()
		writeDate()
