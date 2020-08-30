import schedule, datetime, time, get_retweet

schedule.every(5).minutes.do(get_retweet.main)

# jobの実行監視、指定時間になったらjob関数を実行
while True:
  schedule.run_pending()
  time.sleep(5)
