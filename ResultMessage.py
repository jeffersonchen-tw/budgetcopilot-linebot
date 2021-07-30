
def settleResult(first_date, last_date, total, settlement):

	message_dict = {
	"type": "bubble",
	"body": {
		"type": "box",
		"layout": "vertical",
		"spacing": "md",
		"contents": [
			{
				"type": "text",
				"text": "結算結果",
				"weight": "bold",
				"size": "xl"
			},
			{
				"type": "separator",
				"margin": "lg"
			},
			{
				"type": "box",
				"layout": "horizontal",
				"spacing": "sm",
				"contents": [
					{
					"type": "text",
					"contents": [
						{
							"type": "span",
							"text": "自",
							"size": "lg",
						},
						{
							"type": "span",
							"text": str(first_date),
							"size": "lg",
							"weight": "bold"
						},
						{
							"type": "span",
							"text": "到",
							"size": "lg",
						},
						{
							"type": "span",
							"text": str(last_date),
							"size": "lg",
							"weight": "bold"
						}
					]
					}
				]
			},
			{
				"type": "box",
				"layout": "horizontal",
				"justifyContent": "space-between",
				"spacing": "xxl",
				"contents": [
					{
						"type": "text",
						"text": "總共花費：",
						"size": "lg",
						"weight": "bold",
					},
					{
						"type": "text",
						"text": "$ {}".format(total),
						"size": "lg"
					}
				]
			},
			# 食
			{
				"type": "box",
				"layout": "horizontal",
				"justifyContent": "space-between",
				"spacing": "xxl",
				"contents": [
					{
						"type": "text",
						"text": "「食」：",
						"size": "lg",
						"weight": "bold",
					},
					{
						"type": "text",
						"text": "$ {}".format(settlement['食']),
						"size": "lg"
					}
				]
			},
			# 行
			{
				"type": "box",
				"layout": "horizontal",
				"justifyContent": "space-between",
				"spacing": "xxl",
				"contents": [
					{
						"type": "text",
						"text": "「行」：",
						"size": "lg",
						"weight": "bold",
					},
					{
						"type": "text",
						"text": "$ {}".format(settlement['行']),
						"size": "lg"
					}
				]
			},
			# 樂
			{
				"type": "box",
				"layout": "horizontal",
				"justifyContent": "space-between",
				"spacing": "xxl",
				"contents": [
					{
						"type": "text",
						"text": "「樂」：",
						"size": "lg",
						"weight": "bold",
					},
					{
						"type": "text",
						"text": "$ {}".format(settlement['樂']),
						"size": "lg"
					}
				]
			},
			# 其他
			{
				"type": "box",
				"layout": "horizontal",
				"justifyContent": "space-between",
				"spacing": "xxl",
				"contents": [
					{
						"type": "text",
						"text": "「其他」：",
						"size": "lg",
						"weight": "bold",
					},
					{
						"type": "text",
						"text": "$ {}".format(settlement['其他']),
						"size": "lg"
					}
				]
			}
		]
	}
	}
	return message_dict
