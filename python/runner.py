from dotenv import load_dotenv
import os
import subprocess
import time

load_dotenv()  # .env 読み込み
env = os.environ.copy()

while True:
    print("Botを起動中...")
    process = subprocess.Popen(["python", "discordbot.py"], env=env)
    exit_code = process.wait()
    print("Botが終了しました。5秒後に再起動します...")
    time.sleep(5)
    if exit_code == 99:  # Botが終了時に exit(99) を呼んだら再起動しない
        print("終了要求を受け取ったため、再起動せず停止します。")
        break

    print("Botが終了しました。5秒後に再起動します...")
    time.sleep(5)