#モジュールとconfig.pyの読み込み
import schedule, datetime, time, os, subprocess, ast, pprint, json, config, collections
#OAuthのライブラリの読み込み
from requests_oauthlib import OAuth1Session

#認証処理
CK = config.Consumer_key
CS = config.Consumer_secret
AT = config.Access_token
ATS = config.Access_secret
twitter = OAuth1Session(CK, CS, AT, ATS)

#取得制限の変数3つはは事前に宣言しておく必要がある
limit = 0
reset = 0
sec = 0


#retweets_of_me.jsonのときはoptionフラグを1にする
def get_tweet(url, option = 0):
  global limit, reset, sec
  if option == 1:
    res = twitter.get(url, params = {'count': 5})

  else:
    res = twitter.get(url)

    #取得制限について
    limit = res.headers['x-rate-limit-remaining']
    reset = res.headers['x-rate-limit-reset']
    sec = int(res.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.datetime.now().timetuple()) #UTCを秒数に変換

  raw_loaded_data = json.loads(res.text)

  return raw_loaded_data, limit, reset, sec


#リツイートされた自分のツイートを取得
url = "https://api.twitter.com/1.1/statuses/retweets_of_me.json"
loaded_data, _, _, _ = get_tweet(url, option=1)

#RTされたツイートのidでリストを作る
tweetid = [loaded_data[line]['id'] for line in range(len(loaded_data))]

#ツイートごとのRT関連情報を取得
#(APIを何回も叩きたくないのでres_holderにまとめておく)
res_holder = []
for target_id in tweetid:
  url = "https://api.twitter.com/1.1/statuses/retweets/" + str(target_id) + ".json"
  loaded_data, limit, reset, sec = get_tweet(url)
  [res_holder.append(loaded_data[r]) for r in range(len(loaded_data))]

#比較用のリスト（RTされたツイートのid、重複あり）を作る
holder = [d['retweeted_status'].get('id') for d in res_holder]

#5分前と現在の比較用リストを取得
with open('holder') as g:
  before = ast.literal_eval(g.read()) #1個前の辞書データ
now = holder

import pdb; pdb.set_trace() # 追加
#RT数を比較
for n in tweetid:
  RT_count = now.count(n) - before.count(n)

  if RT_count < 1:
    pass

  else:
    users = [res_holder[k]['user']['name'] for k in range(RT_count)]
    text = res_holder[0]['retweeted_status']['text']
    print('Retweeted by ' + str(users) + '\n' + text)

#定時監視用のデータを別ファイルに控える
with open('holder', mode='w') as f:
  f.write(str(holder))
#
##schedule.every(5).minutes.do(job)
##
### jobの実行監視、指定時間になったらjob関数を実行
##while True:
##        schedule.run_pending()
##        time.sleep(5)

