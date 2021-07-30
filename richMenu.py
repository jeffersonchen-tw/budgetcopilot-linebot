from linebot import (
		LineBotApi
)
from linebot.models import (
	MessageAction, PostbackAction, URIAction,
	RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds
)

line_bot_api = LineBotApi('jOwDuGM3JXp1q1M0QBtzCQZBv2MbNpDezfaukDK2iZ+fr4iXWs9M4VnC/5SC8VELYxLLOiBkgaEYa2r0yEt4mRCs2B9AqZM0mdzp1oIQFk+59wsY1+o7bRVHM21bstRxP/2B/EMOpS+AaIOVn67I4wdB04t89/1O/w1cDnyilFU=')

def createRichMenu():
	rich_menu_to_create = RichMenu(
		size= RichMenuSize(width=800, height=270),
		selected= False,
		name= 'Tools',
		chat_bar_text='點擊使用選單',
		areas=[
		RichMenuArea(
			bounds=RichMenuBounds(x=0, y=0, width=265, height=270),
			action=URIAction(uri='https://github.com/jeffersonchen-tw')
			),
		RichMenuArea(
			bounds=RichMenuBounds(x=276, y=0, width=248, height=270),
			action=MessageAction(text='結算')
			),
		RichMenuArea(
			bounds=RichMenuBounds(x=535, y=0, width=265, height=270),
			action=PostbackAction(label='guide', data='R&guide')
			)
		])
	richMenuId = line_bot_api.create_rich_menu(rich_menu_to_create)

	image_path = './rich-menu.png'

	with open(file=image_path, mode='rb') as file:
		line_bot_api.set_rich_menu_image(rich_menu_id=richMenuId, content_type='image/png', content=file)
	line_bot_api.set_default_rich_menu(richMenuId)

def getRichMenuList():
	rich_menu_list = line_bot_api.get_rich_menu_list()
	for item in rich_menu_list:
		print(item.rich_menu_id)


def deleteRichMenu(id):
	line_bot_api.delete_rich_menu(id)

def deleteAllRichMenu():
	rich_menu_list = line_bot_api.get_rich_menu_list()
	for item in rich_menu_list:
		deleteRichMenu(item.rich_menu_id)

if __name__ == '__main__':
	createRichMenu()
