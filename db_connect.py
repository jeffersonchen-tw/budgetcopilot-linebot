import pymysql

class mysqlConnection():
	def __init__(self, host, user, password, db):
		self.host = host
		self.user = user
		self.password = password
		self.db = db

	def execution(self, cmd, arg, selection=False):
		connection = pymysql.connect(
		host=self.host,
		user=self.user,
		passwd = self.password,
		db=self.db
		)
		db_cursor = connection.cursor()

		def exit():
			db_cursor.close()
			connection.commit()
			connection.close()
		db_cursor.execute(cmd, arg)

		if selection:
			result = db_cursor.fetchone()
			result = str(result[0])
			exit()
			return result
		exit()


	def create_Table(self):
		def create_LastDate_Table():
			self.execution("""
			CREATE TABLE linebot_user_lastdate (
				USER_ID varchar(50),
				LAST_ACTIVE_DATE DATE
			);
			""", [])

		def create_UserInfo_Table():
			self.execution("""
			CREATE TABLE linebot_user_info (
				USER_ID varchar(50),
				SHEET_LINK varchar(90)
			);
			""", [])
		create_UserInfo_Table()
		create_LastDate_Table()

	def insert_UserSheet(self, id, link):
		check_userdata = self.check_UserSheet(id)
		if check_userdata:
			sql_cmd = """
			UPDATE linebot_user_info
			SET SHEET_LINK = %s
			WHERE USER_ID = %s
			"""
			self.execution(sql_cmd, [link, id])
		else:
			sql_cmd = """
			INSERT INTO linebot_user_info
			VALUES (%s, %s)
			"""
			self.execution(sql_cmd, [id, link])

	def update_LastDate(self, id, date):
		check_lastdate = self.check_LastDate(id)
		if check_lastdate:
			sql_cmd = """
			UPDATE linebot_user_lastdate
			SET LAST_ACTIVE_DATE = %s
			WHERE USER_ID = %s
			"""
			self.execution(sql_cmd, [date, id])
		else:
			sql_cmd = """
			INSERT INTO linebot_user_lastdate
			VALUES (%s, %s)
			"""
			self.execution(sql_cmd, [id, date])

	def check_UserSheet(self, user_id):
		sql_cmd = """
		SELECT SHEET_LINK from linebot_user_info
		WHERE USER_ID = %s
		"""
		result = self.execution(sql_cmd, [user_id], selection=True)
		if result:
			return result
		return None

	def check_LastDate(self, user_id):
		sql_cmd = """
		SELECT LAST_ACTIVE_DATE from linebot_user_lastdate
		WHERE USER_ID = %s
		"""
		result = self.execution(sql_cmd, [user_id], selection=True)
		if result:
			return result
		return None
