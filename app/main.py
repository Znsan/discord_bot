import discord
from discord import app_commands 
import dotenv
import os
import json
from discord.ui import Button, TextInput, Modal, View
from PayPaython import PayPay

from server import server_thread

dotenv.load_dotenv()

intents = discord.Intents.default() 
bot = discord.Client(intents=intents) 
tree = app_commands.CommandTree(bot)
gld = discord.Object(id=1280408107888939018) #tree.syncとスラッシュコマンドで使うため

TOKEN = os.environ.get("TOKEN")


@bot.event
async def on_ready():
    #確認
    print('ログインしました')
    new_activity = f"Discord" 
    #アクティビティを設定 
    await bot.change_presence(activity=discord.Game(new_activity))
    #スラッシュ同期
    await tree.sync(guild=gld)


paypay = None

def load_client_uuid():
    """トークンファイルからclient_uuidを読み込みます。"""
    try:
        with open('token.json', 'r') as file:
            data = json.load(file)
            return data.get('client_uuid')
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def save_client_uuid(client_uuid):
    """client_uuidをトークンファイルに保存します。"""
    with open('token.json', 'w') as file:
        json.dump({'client_uuid': client_uuid}, file)

def initialize_paypay(client_uuid):
    """PayPayインスタンスを初期化します。"""
    if client_uuid:
        paypay_instance = PayPay(phone="09081549831", password="Yushin0914", client_uuid=client_uuid) # 設定してください
        print(f"[INFO] 既存のclient_uuidでログインしました: {client_uuid}")
    else:
        paypay_instance = PayPay(phone="09081549831", password="Yushin0914") # 設定してください
        otp = input("SMSに届いた4桁の番号をここに入力して下さい: ")
        paypay_instance.login(otp)
        client_uuid = paypay_instance.client_uuid
        save_client_uuid(client_uuid)
        print(f"[INFO] client_uuidを取得しました: {client_uuid}")
    
    return paypay_instance

@bot.event
async def on_ready():
    """ボットが準備完了したときに呼び出されます。"""
    global paypay
    client_uuid = load_client_uuid()
    paypay = initialize_paypay(client_uuid)
    print(f'{bot.user}　- ログインされました')
    await tree.sync(guild=gld)

class PayPayLinkModal(Modal):
    """PayPayリンクを受け取るためのモーダル。"""
    def __init__(self):
        super().__init__(title="購入")
        self.add_item(TextInput(label="PayPayのリンクを入力して下さい", placeholder="https://pay.paypay.ne.jp/xxxxxx"))

    async def on_submit(self, interaction: discord.Interaction):
        """モーダルが送信されたときに呼び出されます。"""
        link = self.children[0].value
        try:
            paypay.link_receive(link)
            await interaction.response.send_message(f"受け取りが成功しました", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"受け取れませんでした: {str(e)}", ephemeral=True)


@tree.command(name="receive_link", description="PayPayリンクを受け取るコマンド。")
async def receive_link(interaction: discord.Interaction):
    button = Button(label="購入", style=discord.ButtonStyle.primary)

    async def button_callback(interaction):
        await interaction.response.send_modal(PayPayLinkModal())

    button.callback = button_callback
    view = View(timeout=None) 
    view.add_item(button)

    embed = discord.Embed(
        title="テスト",
        description="テスト1\nテスト2\nテスト3\nテスト4",
        color=0xff0000
    )
    
    await interaction.response.send_message(embed=embed, view=view)


bot.run(TOKEN)
