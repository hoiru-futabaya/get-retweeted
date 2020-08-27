import schedule
import datetime
import time
import os
import subprocess, ast
import pprint, json, config #標準のjsonモジュールとconfig.pyの読み込み
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み

def get_retweet():
	hantei = 0 #RT数の総数の変動で通知の有無をみる
	dict = {}

	CK = config.Consumer_key
	CS = config.Consumer_secret
	AT = config.Access_token
	ATS = config.Access_secret
	twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

	url = "https://api.twitter.com/1.1/statuses/retweets_of_me.json" #タイムライン取得エンドポイント

	params ={'count' : 5} #取得数
	res = twitter.get(url, params = params)
	timelines = json.loads(res.text) #レスポンスからタイムラインリストを取得
	#pprint.pprint()


	for line in timelines:

		target_id = line['id_str']
		url2 = "https://api.twitter.com/1.1/statuses/retweets/" + target_id + ".json" #タイムライン取得エンドポイント

		res2 = twitter.get(url2)
		timelines2 = json.loads(res2.text) #レスポンスからタイムラインリストを取得

		if 'errors' in timelines:
			break

		limit = res2.headers['x-rate-limit-remaining'] #リクエスト可能残数の取得
		reset = res2.headers['x-rate-limit-reset'] #リクエスト叶残数リセットまでの時間(UTC)
		sec = int(res2.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.datetime.now().timetuple()) #UTCを秒数に変換

		dict[int(target_id)] = len(timelines2)

		hantei += len(timelines2)

	return hantei, dict, timelines2, limit, sec, twitter

holder = get_retweet()

if 'errors' in holder[2]:
	print(holder[2])
	print("limit: " + holder[3])
	print("sec: " + str(holder[4]))

else:
	with open('holder') as g:
		before = ast.literal_eval(g.read()) #1個前の辞書データ
	get = get_retweet()
	now = get[1]

	if not now == before:
		for i in now:
			url3 = "https://api.twitter.com/1.1/statuses/retweets/" + str(i) + ".json"
			res3 = get[5].get(url3)
			timelines3 = json.loads(res3.text) #レスポンスからタイムラインリストを取得
			rt_users = []

			#import pdb; pdb.set_trace() # 追加
			if i not in before:
				for k in range(now[i]):
					users = timelines3[k]['user']['name']
					rt_users.append(users)
				print('Retweeted by ' + str(rt_users) + '\n' + timelines3[0]['retweeted_status']['text'])

			elif not now[i] == before[i] :
				for k in range(now[i]-before[i]):
					users = timelines3[k]['user']['name']
					rt_users.append(users)
				print('Retweeted by ' + str(rt_users) + '\n' + timelines3[0]['retweeted_status']['text'])
	#定時監視用のデータを別ファイルに控える
	with open('holder', mode='w') as f:
		f.write(str(holder[1]))

#schedule.every(5).minutes.do(job)
#
## jobの実行監視、指定時間になったらjob関数を実行
#while True:
#        schedule.run_pending()
#        time.sleep(5)
