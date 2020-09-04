#モジュールとconfig.pyの読み込み
import os, ast, pprint, json, config, datetime, time, subprocess, re, sys
#OAuthのライブラリの読み込み
from requests_oauthlib import OAuth1Session

#認証処理（グローバル変数）
CK = config.Consumer_key
CS = config.Consumer_secret
AT = config.Access_token
ATS = config.Access_secret
twitter = OAuth1Session(CK, CS, AT, ATS)


def main():
  #リツイートされた自分のツイートを取得
  url = "https://api.twitter.com/1.1/statuses/retweets_of_me.json"
  loaded_data, _, _, _ = get_tweet(url, option=1)

  if 'errors' in loaded_data:
    print('API limit: ' + str(sec) + 'sec')
    sys.exit()

  #RTされたツイートのidでリストを作る
  tweetid = [loaded_data[line]['id'] for line in range(len(loaded_data))]

  #ツイートごとのRT関連情報を取得
  #(APIを何回も叩きたくないのでres_holderにまとめておく)
  res_holder = []

#  import pdb; pdb.set_trace() # 追加
  for i, target_id in enumerate(tweetid):
    url = "https://api.twitter.com/1.1/statuses/retweets/" + str(target_id) + ".json"
    loaded_data, limit, reset, sec = get_tweet(url)
    if len(loaded_data) == 0:
      continue

    if 'errors' in loaded_data:
      print('API limit: ' + str(sec) + 'sec')
      sys.exit()

    del loaded_data[0]['source']
    del loaded_data[0]['retweeted_status']['source']
    raw_debug = re.sub('[\']', '\"', str(loaded_data[0]))
    debug = re.sub('(True|False|None)', '\"\"', raw_debug)
    with open('loaded/loaded_data' + str(i), mode = 'w') as x:
      x.write(debug)

    [res_holder.append(loaded_data[r]) for r in range(len(loaded_data))]

  #比較用のリスト（RTされたツイートのid、重複あり）を作る
  holder = [d['retweeted_status'].get('id') for d in res_holder]

  #5分前と現在の比較用リストを取得
  with open('holder') as g:
    before = ast.literal_eval(g.read()) #1個前の辞書データ
  now = holder

  #RT数を比較
  for n in tweetid:
    RT_count = now.count(n) - before.count(n)

    if RT_count < 1:
      pass

    else:
      for z in range(len(res_holder)):
        if n in res_holder[z]['retweeted_status'].values():
          text = res_holder[z]['retweeted_status']['text']
          break

      users = [str(k) + ' ' +  res_holder[k]['user']['name'] for k in range(RT_count)]
      raw_notify_text = 'Retweeted by ' + str(users) + '\n' + '\n' + text
      notify_text = re.sub('[\]\[\']', '', raw_notify_text) #カッコとクォートをなくす
      action = 'bash /data/data/com.termux/files/home/github/get_favorited/test.sh ' + re.sub('[\]\[\'\,]', '', str(n))
      command = ['termux-notification', '-t', 'RTされたよ！', '-c', notify_text, '--priority', 'max', '--action', action]
      subprocess.run(command)

  #定時監視用のデータを別ファイルに控える
  with open('holder', mode='w') as f:
    f.write(str(holder))


#retweets_of_me.jsonのときはoptionフラグを1にする
def get_tweet(url, option = 0):
  limit = 0
  reset = 0
  sec = 0

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


if __name__ == '__main__':
  main()
