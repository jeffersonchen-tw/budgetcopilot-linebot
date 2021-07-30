import os
import re
from datetime import datetime, timezone, timedelta
import json

from flask import Flask, request, abort

from ResultMessage import settleResult

from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	FollowEvent,
	MessageEvent, TextMessage, TextSendMessage,
	TemplateSendMessage, ButtonsTemplate,
	PostbackEvent, PostbackTemplateAction,
	ConfirmTemplate, PostbackAction,
	FlexSendMessage
)

from db_connect import mysqlConnection
from googlesheet import InputGsheet

app = Flask(__name__)

line_bot_api = LineBotApi('<CHANNEL_ACCESS_TOKEN>')
handler = WebhookHandler('<CHANNEL_SECRET>')

service_acc = 'budget-copilot@budget-copilot.iam.gserviceaccount.com'

linebotDB = mysqlConnection(
	host='<host_name>',
	user='<user_name>',
	password='<db_password>',
	db='<db_name>')

@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']
	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)
	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return 'OK'

# greeting message
@handler.add(FollowEvent)
def handle_follow(event):
	line_bot_api.reply_message(
		event.reply_token,
		[
		TextSendMessage(text='使用前請詳閱選單中使用指引，並建立試算表與服務帳號共用。'),
		TextSendMessage(text='回傳共用試算表範例： 「試算表 https://docs.google.com/spreadsheets/d/EjfrivBfrf08....../edit#gid=0」')
		])

# MESSAGE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	active = True
	def inputUserSheetId(message, id):
		try:
			full_link = message[4:]
			result = re.search(r'spreadsheets/[a-zA-Z]/(\S+)/', full_link)
			if result:
				spreadsheet_id = result.group(1)
				linebotDB.insert_UserSheet(id, spreadsheet_id)
		except:
			global active
			active = False
			valid = re.match(
			r'https?://docs.google.com/spreadsheets/[a-zA-Z]/w', message[5:])
			if not valid:
				line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text='請輸入有效試算表網址'))
			else:
				line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text='無法加入試算表'))

	user_message = event.message.text

	userId = event.source.user_id

	sheetId = linebotDB.check_UserSheet(userId)

	if user_message == '確認試算表':
		if sheetId == None:
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text='尚未加入試算表'))
		else:
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text='已加入試算表'))

	if sheetId != None:
		userGsheet = InputGsheet(sheetId)
		keep = re.match(r'^\$[0-9]+\s\S+\s*$', user_message)
		# 記帳
		if keep:
			line_bot_api.reply_message(
			event.reply_token,
			TemplateSendMessage(
				alt_text='bookkeeping menu',
				template=ButtonsTemplate(
					title='種類',
					text='選擇一個分類',
					actions=list(
						map(
						lambda item: PostbackTemplateAction(
						label=item, data='A&'+user_message+' &'+item),
						['食', '樂', '行', '其他'])
					)
				))
			)
		elif user_message == '結算':
			line_bot_api.reply_message(
				event.reply_token,
				[TextSendMessage(text='開始結算，請等候結算結果。'),
				TemplateSendMessage(
					alt_text='是否在結算後重置帳目',
					template=ConfirmTemplate(
						text='是否在結算後重置帳目',
						actions=[
						PostbackAction(label='是', data='S&yes'),
						PostbackAction(label='否', data='S&no')
						])
					)])
		elif user_message == '清除前一項':
			try:
				userGsheet.deleteLastRow()
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage(text='已成功清除前一帳目'))
			except:
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage(text=
					'無法清除前一帳目，請確認試算表已與服務帳號共用且不為空或回報問題。'))
		elif user_message[:3] == '試算表':
			inputUserSheetId(message=user_message, id=userId)
		else:
			active = False
			guide_message = json.load(
				open('./guideFlexMessage.json', 'r', encoding='utf-8'))
			line_bot_api.reply_message(
				event.reply_token,
				[
				FlexSendMessage('使用指引', guide_message),
				TextSendMessage(text='請輸入有效指令')
				])
	else:
		if user_message[:3] != '試算表':
			active = False
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text='請輸入有效指令，或先建立試算表並與服務帳號共用。'))
		else:
			inputUserSheetId(message=user_message, id=userId)
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text='已成功加入試算表'))


	if active:
		twTZ = timezone(timedelta(hours=+8))
		date = datetime.now(twTZ).strftime('%Y-%m-%d')
		linebotDB.update_LastDate(id=userId, date=date)

# POSTBACK
@handler.add(PostbackEvent)
def handle_postback(event):
	postback_data = event.postback.data[2:]
	postback_title = event.postback.data[0]

	# guide
	if postback_title == 'R':
		guide_message = json.load(
			open('./guideFlexMessage.json', 'r', encoding='utf-8'))
		line_bot_api.reply_message(
			event.reply_token,
			FlexSendMessage(alt_text='使用指引', contents=guide_message))
	# send service account
	elif postback_title == 'G':
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(
				text='{}'.format(service_acc))
			)


	userId = event.source.user_id
	sheetId = linebotDB.check_UserSheet(userId)
	if sheetId != None:
		userGsheet = InputGsheet(sheetId)

		if postback_title == 'A':
			splitted_data = re.split(r"\s+", postback_data)
			twTZ = timezone(timedelta(hours=+8))
			date = datetime.now(twTZ).strftime('%Y-%m-%d')
			cost = splitted_data[0][1:]
			title = splitted_data[1]
			category = splitted_data[2][1:]
			try:
				# write in google sheet
				userGsheet.writeInKeeping(date, cost, title, category)
				# reply user
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage(text='已寫入帳目'))
			except:
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage(text='無法記帳，請確認已將試算表與服務帳號共用。'))
		# settlement
		elif postback_title == 'S':
			# result = [fist date, last date, total, total of each category]
			try:
				result = userGsheet.settlement()
				settlement_message = settleResult(
					result[0], result[1], result[2], result[3])
				line_bot_api.reply_message(
					event.reply_token,
					FlexSendMessage(alt_text='結算結果', contents=settlement_message))
				if postback_data == 'yes':
					userGsheet.InitSheet()
			except:
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage(
						text='無法完成結算，請確認已將試算表與服務帳號共用或試算表不為空白。'))


if __name__ == "__main__":
	port = int(os.environ.get('PORT', 8080))
	app.run(host='0.0.0.0', port=port)
