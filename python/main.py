# インストールした discord.py を読み込む
import sys
import discord
import os
import discord.app_commands
import asyncio
import datetime
from discord.ext import tasks
import csv
from PIL import Image
import io
import zipfile

'''
コマンドの登録方法
@tree.command(name="<コマンド名>", description="<コマンドの説明>")

(機能によるが，基本的に)
async def <コマンド名> (interaction: discord.Interaction):
    機能...
    
    
'''



###
# 自分のBotのアクセストークンに置き換えてください
TOKEN  = os.getenv("TOKEN")
# 催促を送るチャンネルID（ここに送信します）
target_channel_id = os.getenv("CHANNEL")  # 置き換えてください

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # discordbot.py のある場所
HOME_DIR = os.path.join(os.path.dirname(BASE_DIR), "home")

# 必要なら作成
os.makedirs(HOME_DIR, exist_ok=True)

# カレントディレクトリを home に変更
os.chdir(HOME_DIR)


# Discord botクライアント
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client) #←ココ
intents.guilds = True

'''
     &%%%%%%&=                                       +#&                   
      =#     &&                                       %&                   
      =#      #     =#@@@#=       =%@@@&        &@@@& %&   #@@#    #@@+    
      =#    =%+    &&     +%=     +    +#     &&    =&@&    +%      #=     
      =@%%%#%     =#+++++++&%     =+++++#    =%       #&     &&    %+      
      =#    +%    =#             #%=   =#    +%       %&      %+  &&       
      =#     +%    %&           &&     =#     %=     =@&       %=+%        
     =&@++    +%+   &%&++++&&   =%&+++%%#+=    &&+++&&#%=      =##=        
                                                                #=         
                                                               %&          
                                                           +%%%%%%         
'''
@client.event
async def on_ready():
    await tree.sync()  # これが重要！
    print(f'Logged in as {client.user}!')

    
'''
     +%&                          +++#         =++%&                       
      &&                             #            &&                       
      &&=#@@%       =#@@@#=          #            &&          %@@@%        
      &#+   =%+    &&     +%=        #            &&        &+     +&      
      &&     &&   =#+++++++&%        #            &&       +%       &&     
      &&     &&   =#                 #            &&       &&       &%     
      &&     &&    %&                #            &&       =%       %=     
     +%%+   +%%+    &%&++++&&    ++++#++++    =+++%%+++=     &+++++&=           
'''

@tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!")




'''                                                                        
        =%%%%%=              %%#%            %@=                           
        %=                     +%             %=                           
      ++#&+++    +%+++&%       +%      =%+++&%#=   %&+++%+    ++#+%++%=    
        %=      +&     =%      +%     =%     =@=  %=     &+     #&         
        %=      %+      %=     +%     &&      %= =@@@@@@@@#     #          
        %=      +&     =%      +%     =%     =@=  %=            #          
      ++#&+++    +%++++%    +++&#+++   =%+++&%#&=  %&++++&&   ++#++++      
'''

@tree.command(
    name="make_directory",
    description="指定した名前のディレクトリを作成します"
)
@discord.app_commands.describe(folder_name="作成するディレクトリ名（例: directory）")
async def create_folder(interaction: discord.Interaction, folder_name:str):
    await interaction.response.defer()
    try:
        if not folder_name:
            await interaction.followup.send("ディレクトリ名が空です。キャンセルしました。")
            return

        path = f"./{folder_name}"

        os.makedirs(path, exist_ok=False)
        await interaction.followup.send(f"ディレクトリ `{folder_name}` を作成しました。")

    except FileExistsError:
        await interaction.followup.send(f"`{folder_name}` はすでに存在しています。")

    except asyncio.TimeoutError:
        await interaction.followup.send("60秒以内に入力がなかったため、処理をキャンセルしました。")

'''
                                                                 #%                                                     
                                                                                                                        
   +@@@#+%    =@@@@%=   =@@@#= %@@@&   %@@@#=                 =@@@%     #@%#@#=#@#=   =@@@@%=      %@@@++@#=   %@@@#=   
  &%    +%          %=    +%    +%   =%     =%                   +%      &%  +%  =%         %=   +&    =#%   =%     =%  
   =&&&&&=     +&&&&#+     &&  =#    %%&&&&&&#+  =&&&&&&&&=      +%      &&  +%  =%    +&&&&#+   %      +%   %%&&&&&&#+ 
         %=  =@=    %+      #= %=    &+                          +%      &&  +%  =%  =@=    %+   %=     +%   &+         
  @#    +%   +%    #@+      =#&&      &%     %+                  +%      &&  +%  =%  +%    #@+    %=   &#%    &%     %+ 
  +=&&&&+     =&&&& +&+      +&        =&&&&&=                &&&&&&&&= &&&& =&&  &&= =&&&& +&+    +&&&=+%     =&&&&&=  
                                                                                                        +&              
                                                                                                   &####+ 
'''

@tree.command(
    name="save_image",
    description="画像に名前を付け，指定したディレクトリに保存します（拡張子不要）"
)
@discord.app_commands.describe(
    folder_name="保存先のディレクトリ名（例: directory）, 無記入ならdownloads",
    base_name="保存する画像ファイル名（例: cat）",
    attachment="保存したい画像ファイル"
)
async def save_named_image(
    interaction: discord.Interaction,
    folder_name: str,
    base_name: str,
    attachment: discord.Attachment
):
    await interaction.response.defer()

    if not attachment.content_type or not attachment.content_type.startswith("image/"):
        await interaction.followup.send("❌ 添付されたファイルは画像ではありません。")
        return

    try:
        # 空の場合は downloads に設定
        if not folder_name.strip():
            folder_name = "downloads"

        # ディレクトリ作成
        os.makedirs(folder_name, exist_ok=True)

        # 拡張子の取得
        ext = os.path.splitext(attachment.filename)[1]
        if not ext:
            ext = ".png"  # 拡張子がない場合のデフォルト

        save_path = os.path.join(folder_name, base_name + ext)

        # 保存
        await attachment.save(save_path)

        await interaction.followup.send(f"✅ 画像を `{save_path}` に保存しました。")

    except Exception as e:
        await interaction.followup.send(f"❌ 保存中にエラーが発生しました: {e}")

'''
                                   &+                              &+      
  %%+ +%%=   +%%%%=      %%%&++  +%##%%%&    &%%%%     +%%  %%&  +%##%%%&  
   =#%+  +  +&    &&   =#   =%+    &+             #=     %%%  +=   &+      
   =%      =@@@@@@@@+   +@@@@=     &+        &@@@@@+     %=        &+      
   =%       %=               &&    &+       %+    %+     %=        &+      
 =+&#+++=    %+++++%=  %&++++%=    +%+++%&  &&+++%@&=  ++#&+++     +%+++%& 
'''

@tree.command(name="restart", description="Botを再起動します（管理者限定）")
@discord.app_commands.checks.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("Botを再起動します。しばらくお待ちください...", ephemeral=True)
    await asyncio.sleep(1)
    await client.close()  # Discordセッションを閉じて正常終了させる
    
    

@tree.command(name="shutdown", description="Botを終了します（runnerなし）")
async def shutdown(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 権限がありません。", ephemeral=True)
        return

    await interaction.response.send_message("🛑 Botを終了します。再起動は行いません。", ephemeral=False)

    await client.close()
    sys.exit(99)  # runner.py に再起動しないことを伝える終了コード
    
'''
     +&                                                                    
     &#                                                                    
     &#                                                                    
  &%%#@%%%%%%%+       &%%%&   +%%%+        +%%%%%+            &%%%%&=      
     &#                  %#=&%+   &&     &#&=   =&#&        %#&=   =&#&    
     &#                  %@#            #%         &#      @&         %%   
     &#                  %#            +@=          #&    &#           @+  
     &#                  %#            &@%%%%%%%%%%%%+    %@%%%%%%%%%%%%+  
     &#                  %#            =@=                =@=              
     +@                  %#             =#+         &+     +#+         &+  
      &%&++++&%%=    =+++##++++++         &%&+++++&%&        &%&+++++&%+   

'''
def tree_str(path: str, prefix: str = "") -> str:
    lines = []
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return ""

    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "

        # ドットで始まる場合 → 再帰せず名前だけ表示
        if entry.startswith("."):
            lines.append(prefix + connector + entry)
            continue

        lines.append(prefix + connector + entry)

        if os.path.isdir(full_path):
            extension = "    " if is_last else "│   "
            # 再帰的に表示（ドットで始まるディレクトリは除外済み）
            lines.append(tree_str(full_path, prefix + extension))
    return "\n".join(lines)

@tree.command(
    name="show_tree",
    description="Botの起動ディレクトリの階層構造を表示します"
)
async def show_tree(interaction: discord.Interaction):
    base_path = os.getcwd()
    output = base_path + "\n" + tree_str(base_path)

    if len(output) > 1900:
        output = output[:1900] + "\n...（省略）"

    await interaction.response.send_message(f"```\n{output}\n```")



'''
                                           %=                         =%%  
                                           %=                           %= 
                                                                        %= 
  =+%&+&++&=   %&+++&%=  =%#&+%%%+&%    =++#&      =&#&&++%&     %++++&&#= 
    &#        %=      %=  &%  =#   #+      %&       +#     #=   %=     =@= 
    &&       =@@@@@@@@@&  &&  =#   #+      %&       +%     #+  +%       %= 
    &&        %=          &&  =#   #+      %&       +%     #+   %=     =@= 
  ++%%+++=     &&+++++&= =%%+ =@+  #&=  +++#%+++   =&#+   +#&=   %++++&&#&=
'''

# 催促を送るチャンネルID（ここに送信します）
target_channel_id = 1374204851076071454  # 置き換えてください


# グローバル変数（起動中のみ）
deadline = None

# 通知タイミング（期限までの日数）
REMINDER_DAYS = [7, 3, 1, 0]  # 7日前、3日前、前日、当日

# 送信済み通知を管理（期限ごとに初期化）
sent_reminders = set()

@tasks.loop(minutes=60)  # 1時間ごとにチェック（負荷抑制）
async def reminder_task():
    global deadline, target_channel_id, sent_reminders

    if not deadline or not target_channel_id:
        return

    now = datetime.datetime.now()
    if now > deadline:
        # 期限過ぎたので停止＋最終通知
        channel = client.get_channel(target_channel_id)
        if channel:
            await channel.send("⚠️ 提出期限が過ぎました。提出がまだの方は速やかに対応してください。")
        reminder_task.cancel()
        print("期限過ぎたためリマインド停止")
        return

    channel = client.get_channel(target_channel_id)
    if channel is None:
        print("指定チャンネルが見つかりません")
        return

    days_left = (deadline.date() - now.date()).days

    # 対象日かつ未通知ならリマインド
    if days_left in REMINDER_DAYS and days_left not in sent_reminders:
        sent_reminders.add(days_left)
        mention_text = "@everyone"
        if days_left == 0:
            msg = f"{mention_text} 〆切当日です！忘れずに提出してください！"
        else:
            msg = f"{mention_text} 提出期限まであと {days_left} 日です。準備は大丈夫ですか？"
        try:
            await channel.send(msg)
            print(f"リマインド送信: 期限まであと{days_left}日")
        except Exception as e:
            print(f"送信エラー: {e}")

@reminder_task.before_loop
async def before_reminder():
    await client.wait_until_ready()
    print("リマインドタスク開始")

@tree.command(name="set_deadline", description="提出期限を設定します（例: 2025-07-01 23:59）")
@discord.app_commands.describe(
    date_time="提出期限を「YYYY-MM-DD HH:MM」の形式で入力してください",
)
async def set_deadline(interaction: discord.Interaction, date_time: str):
    global deadline, sent_reminders

    try:
        new_deadline = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    except ValueError:
        await interaction.response.send_message("日時の形式が正しくありません。`YYYY-MM-DD HH:MM` の形式で入力してください。", ephemeral=True)
        return

    now = datetime.datetime.now()

    if deadline and deadline > now:
        await interaction.response.send_message(
            f"既に期限が設定されています（{deadline.strftime('%Y-%m-%d %H:%M')}）。変更する場合は先に期限解除してください。",
            ephemeral=True)
        return

    deadline = new_deadline
    sent_reminders = set()

    if reminder_task.is_running():
        reminder_task.cancel()
    reminder_task.start()

    await interaction.response.send_message(
        f"提出期限を {deadline.strftime('%Y-%m-%d %H:%M')} に設定しました。", ephemeral=False)


@tree.command(name="cancel_deadline", description="提出期限とリマインダーを解除します")
async def clear_deadline(interaction: discord.Interaction):
    global deadline, sent_reminders

    deadline = None
    sent_reminders = set()

    if reminder_task.is_running():
        reminder_task.cancel()

    await interaction.response.send_message("提出期限とリマインダーを解除しました。", ephemeral=True)


@tree.command(name="show_deadline", description="現在の提出期限と通知先チャンネルを表示します")
async def show_deadline(interaction: discord.Interaction):
    if deadline:
        await interaction.response.send_message(
            f"現在の提出期限は {deadline.strftime('%Y-%m-%d %H:%M')}、通知チャンネルIDは {target_channel_id} です。",
            ephemeral=True)
    else:
        await interaction.response.send_message("現在、提出期限は設定されていません。", ephemeral=True)
    

'''
  =++++++++++++++=                                             &%#@+                                
  %@     ##     #%                                               =@+                                
  %@     ##     #%                                               =@+                                
  %@     ##     #%        ==++++=              =++++=  =         =@+    =+++++         =++++=  =    
  &#     ##     %&      ##+=   =%@=          #@+    +@@@         =@+     ##          #@+    +@@@    
         ##                      +@=        #%        &#         =@+  =#%=          #%        &#    
         ##                      =@+        &#=                  =@+=%#+            &#=             
         ##              +#@@@@@@#@+          +@@@@@%+           =@@@@&               +@@@@@%+      
         ##            %%+       =@+                 =&%         =@& =%#=                    =&%    
         ##           &#         =@+       %#          #%        =@+   +@&         %#          #%   
         ##           +@=       &@@+       %@%        &@=        =@+     %@=       %@%        &@=   
     %%%%@@%%%%        =&%%%%%&+++@#%%     %#+&&%%%%%&+        &%#@+     &@@#%%    %#+&&%%%%%&+     
                                                                                                 
'''
CSV_FILE = 'tasks.csv'
FIELDNAMES = ['ID', 'User', 'Date', 'Task', 'Done']

# 初期化：CSVファイルがなければ作成
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

def read_tasks():
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_tasks(tasks):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in tasks:
            writer.writerow(task)

@tree.command(name="add_task", description="タスクを追加します")
@discord.app_commands.describe(content="タスクの内容を入力してください")
async def add_task(interaction: discord.Interaction, content: str):
    tasks = read_tasks()
    new_id = 1 if not tasks else int(tasks[-1]["ID"]) + 1
    new_task = {
        "ID": str(new_id),
        "User": interaction.user.display_name,
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Task": content,
        "Done": "False"
    }
    tasks.append(new_task)
    write_tasks(tasks)
    await interaction.response.send_message(f"✅ タスク追加: `{content}` by {interaction.user.display_name}")

@tree.command(name="done_task", description="指定したタスクを完了にします")
@discord.app_commands.describe(task_id="完了するタスクの番号を入力してください")
async def done_task(interaction: discord.Interaction, task_id: int):
    tasks = read_tasks()
    found = False
    for task in tasks:
        if int(task["ID"]) == task_id:
            if task["Done"] == "True":
                await interaction.response.send_message("⚠️ すでに完了済みのタスクです")
                return
            task["Done"] = "True"
            found = True
            break
    if not found:
        await interaction.response.send_message("❌ 該当するタスクが見つかりません")
        return
    write_tasks(tasks)
    await interaction.response.send_message(f"✅ タスク {task_id} を完了にしました")

@tree.command(name="show_tasks", description="現在のタスク一覧を表示します")
async def list_tasks(interaction: discord.Interaction):
    tasks = read_tasks()
    if not tasks:
        await interaction.response.send_message("📋 現在タスクはありません")
        return
    message = "📋 **タスク一覧**\n"
    for task in tasks:
        status = "✅" if task["Done"] == "True" else "🕓"
        message += f"{task['ID']}. {status} `{task['Task']}` - {task['User']} ({task['Date']})\n"
    await interaction.response.send_message(message)
    
    
'''
         +%@=                  =++++++++                                                            
           #=                      #&                                                               
    +%%%&  #=      +%%%&=          #&      &%&+%%+ =%%+      =&%%%&        =&%%&= %%&     &%%%&=    
  =%+   =%%@=    &&     &&         #&       &@%  %@%  %&    &&=   +#=     &&    &&@=    +#+   =&%=  
 =#       +@=   %&       =#        #&       &#   &#   &#           %&    %+      +@=   +#       =#  
 %&        #=   #=        #=       #&       &#   &#   &#     +%%%%%#&    #=       #=   %#%%%%%%%%@+ 
 +%       =@=   %+       =#        #&       &#   &#   &#   &#+     %&    #+      =@=   +%           
  %+      #@=   =#       %+        #&       &#   &#   &#   #=     =#&    =#      #@=    %&       #+ 
   =&%%%%+=@#&    +&%%%&+=     &%%%@#%%%+  &#@%  &@%  &@%  =&%%%%&+##%=   =+%%%%+=#=     =&%%%%&+=  
                                                                                  #=                
                                                                                 +%                 
                                                                           +%%%%%+                   
'''
@tree.command(name="get_image", description="指定した画像を表示します")
@discord.app_commands.describe(filename="表示する画像ファイル名（例: cat.png）")
@discord.app_commands.describe(folder="ファイルがあるディレクトリ名（例: folder）")
async def show_image(interaction: discord.Interaction, folder: str,filename: str):
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        await interaction.response.send_message("❌ ファイルが見つかりませんでした。")
        return

    file = discord.File(filepath)
    await interaction.response.send_message(content=f"🖼️ `{filename}` を表示します：", file=file)


@tree.command(name="delete_image", description="指定した画像を削除します")
@discord.app_commands.describe(filename="削除する画像ファイル名（例: cat.png）")
@discord.app_commands.describe(folder="ファイルがあるディレクトリ名（例: folder）")
async def show_image(interaction: discord.Interaction, folder: str,filename: str):
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        await interaction.response.send_message("❌ ファイルが見つかりませんでした。")
        return

    try:
        os.remove(filepath)
        await interaction.response.send_message(f"🗑️ 画像 `{filename}` を削除しました。")
    except Exception as e:
        await interaction.response.send_message(f"⚠️ 削除に失敗しました: {str(e)}")
        
        
'''
      .----:  -                                                                                                                   
    :%#:   -%+%                                                                                                                   
   =#.       =%                                                                                                                   
  :%.         =     .===++===.   -*@+++++.-++*=  :+*%.=*+++==-      =+*%.:=+++*:    :+*+++++=.       :++++===%:      :++++===%:   
  =#               :#.      .#:   :@+   +@:  .%:   -@%:      -*       -@*+    .:   -#.      :%:     :%.      *:     :%.      *:   
  =#              .%:        :%.  :%:   =#    %-   -@:        *+      -%.         .%.        -%      *+              *+           
  -%              :%          %:  :%:   =#    %-   -%.        =#      -%          :@===========       .-===-=-        .-===-=-    
   *-         ..  .%:        :%.  :%:   =#    %-   -@-        *=      -%          .%-               .        +#     .        +#   
    +=       *%.   :%:      :%:   :%:   =#    %-   -@%-      =*       -%           .%=       :#.    %*       **     %*       **   
     .-=****+:       -=****=-    =#@#=  =@*:  %#+  -%.-+***+=:     =**#@*****-       -+****+=-.     #+=++**++-      #+=++**++-    
                                                   -%                                                                             
                                                   -%                                                                             
                                                 -#%@###:                                 
'''
@tree.command(name="compress_image", description="画像を指定した画質で圧縮します")
@discord.app_commands.describe(
    attachment="圧縮したい画像ファイルを添付してください（jpg/png）",
    quality="画質（0～100, 数字が大きいほど高画質）"
)
async def compressimage(
    interaction: discord.Interaction,
    attachment: discord.Attachment,
    quality: discord.app_commands.Range[int, 1, 100]
):
    await interaction.response.defer()  # 処理中表示

    if not attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        await interaction.followup.send("❌ 対応形式は `.jpg`, `.jpeg`, `.png` のみです。")
        return

    try:
        # 元画像をバイナリで取得
        img_bytes = await attachment.read()
        img = Image.open(io.BytesIO(img_bytes))

        # PNG → JPEG変換するか確認
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 圧縮してバッファに保存
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="compressed.jpg")
        await interaction.followup.send(content=f"📦 圧縮完了（品質：{quality}）", file=file)

    except Exception as e:
        await interaction.followup.send(f"❌ 圧縮中にエラーが発生しました：{e}")
        

@tree.command(name="get_directory", description="指定ディレクトリ内の画像を全て圧縮します")
@discord.app_commands.describe(
    folder_path="画像が入っているディレクトリのパス（相対パス）",
    quality="圧縮画質（1～100, JPEG変換）"
)
async def compress_folder(
    interaction: discord.Interaction,
    folder_path: str,
    quality: discord.app_commands.Range[int, 1, 100]
):
    await interaction.response.defer(thinking=True)

    if not os.path.isdir(folder_path):
        await interaction.followup.send("❌ 指定されたディレクトリが存在しません。")
        return

    compressed_images = []
    supported_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(supported_ext):
                full_path = os.path.join(root, filename)
                try:
                    with Image.open(full_path) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=quality)
                        buffer.seek(0)
                        compressed_images.append((filename, buffer.read()))
                except Exception as e:
                    print(f"❌ {filename} の圧縮に失敗: {e}")

    if not compressed_images:
        await interaction.followup.send("❗ 対応画像が見つかりませんでした。")
        return

    # ZIP圧縮
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for name, data in compressed_images:
            zipf.writestr(name, data)
    zip_buffer.seek(0)

    file = discord.File(fp=zip_buffer, filename="compressed_images.zip")
    await interaction.followup.send(content=f"✅ 圧縮完了（{len(compressed_images)}枚, 品質={quality}）", file=file)

from minesweeper import MinesweeperView  # 先ほどのファイル名に合わせてインポート
@tree.command(name="minesweeper", description="Discordでマインスイーパーを遊ぶ")
async def minesweeper(interaction: discord.Interaction):
    view = MinesweeperView()
    await interaction.response.send_message("マインスイーパー開始！地雷を避けて全部開けてね！", view=view)
    
    
'''

              @@@@@@@@@@@@@@@#&         #@@@@@@@@@@@@@#%+          #@@@@@@@@@@@@@@@@@@@@#           
                 #@&        +%@@+         =@@        =+%@#+           =@#             &@#           
                 #@&           %@%        =@@            @@&          =@#             &@#           
                 #@&            #@=       =@@             #@+         =@#             &@#           
                 #@&            %@&       =@@              @@=        =@#      =+      %+           
                 #@&            #@+       =@@              &@%        =@#      #@=                  
                 #@&           &@#        =@@              =@#        =@@%%%%%%@@=                  
                 #@&        =+#@%         =@@              =@#        =@@%%%%%%@@=                  
                 #@@@@@@@@@@@@&           =@@              =@#        =@#      #@=                  
                 #@%+++++++==             =@@              +@%        =@#      =+                   
                 #@&                      =@@              #@=        =@#                           
                 #@&                      =@@             &@%         =@#                           
                 #@&                      =@@            &@%          =@#                           
                 #@&                      =@@         =&#@&           =@#                           
              @@@@@@@@@@@@#             #@@@@@@@@@@@@@@@+          #@@@@@@@@@@@@=                   
              +++++++++++++             +++++++++++++==            +++++++++++++                    

'''

from python.confirm_delete_view import ConfirmDeleteView  # 分割したクラスをインポート
@tree.command(name="delete_directory", description="指定したディレクトリを削除します（空でなくても確認後に削除）")
@discord.app_commands.describe(directory="削除したいディレクトリのパス")
async def rmdir(interaction: discord.Interaction, directory: str):
    base_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.join(base_dir, directory))

    if not target_dir.startswith(base_dir):
        await interaction.response.send_message("セキュリティ上、Botのディレクトリ外は操作できません。", ephemeral=True)
        return

    if not os.path.exists(target_dir):
        await interaction.response.send_message(f"指定されたディレクトリは存在しません: `{directory}`", ephemeral=True)
        return

    if not os.path.isdir(target_dir):
        await interaction.response.send_message(f"`{directory}` はディレクトリではありません。", ephemeral=True)
        return

    if os.listdir(target_dir):
        view = ConfirmDeleteView(target_dir, interaction.user.id)
        await interaction.response.send_message(
            f"ディレクトリ `{directory}` は空ではありません。削除してよろしいですか？",
            view=view,
            ephemeral=True
        )
        await view.wait()
        if view.result is None:
            await interaction.followup.send("応答がありませんでした。削除を中止します。", ephemeral=True)
    else:
        try:
            os.rmdir(target_dir)
            await interaction.response.send_message(f"ディレクトリ `{directory}` を削除しました。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"削除に失敗しました: {e}", ephemeral=True)

import uuid
from extract_pdf import extract_pdf_content

@tree.command(name="extract_pdf", description="PDFの指定ページのテキストと画像を抽出")
@discord.app_commands.describe(
    page="抽出したいページ番号（1始まり）",
    file="対象のPDFファイル"
)
async def extract_pdf(
    interaction: discord.Interaction,
    page: int,
    file: discord.Attachment
):
    if not file.filename.lower().endswith(".pdf"):
        await interaction.response.send_message("PDFファイルをアップロードしてください", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    # 一時ファイルの保存
    session_id = str(uuid.uuid4())
    os.makedirs(f"tmp/{session_id}", exist_ok=True)
    pdf_path = f"tmp/{session_id}/{file.filename}"
    await file.save(pdf_path)

    try:
        text, images = extract_pdf_content(pdf_path, page, f"tmp/{session_id}")
        files = [discord.File(img) for img in images]
        response = f"📄 **ページ {page} のテキスト:**\n```{text[:1900]}```"
        await interaction.followup.send(response, files=files or None)
    except Exception as e:
        await interaction.followup.send(f"エラー: {e}")
    finally:
        # 後始末
        for root, dirs, files in os.walk(f"tmp/{session_id}", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            os.rmdir(root)
# 実行
#Botの起動とDiscordサーバーへの接続
client.run(TOKEN)