import discord
from discord import app_commands 
import discord
import dotenv
import os

from server import server_thread

dotenv.load_dotenv()

intents = discord.Intents.default() 
bot = discord.Client(intents=intents) 

tree = app_commands.CommandTree(bot)
gld = discord.Object(id=967705787956858931) #tree.syncとスラッシュコマンドで使うため

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


#verify
@tree.command(name="verify", description="認証パネルを設置", guild=gld)
async def VERIFY(interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
            return

        global auth_role
        auth_role = role

        ch = interaction.channel
        embed = discord.Embed(
            title="認証",
            description="__ルールをしっかり読んでから認証してください__",
            color=discord.Color.blue()
        )
        view = discord.ui.View()

        async def button_callback(interaction: discord.Interaction):
            if auth_role not in interaction.user.roles:
                await interaction.user.add_roles(auth_role)
                await interaction.response.send_message(f"{auth_role.name} ロールが付与されました。", ephemeral=True)
            else:
                await interaction.response.send_message(f"あなたは既に {auth_role.name} ロールを持っています。", ephemeral=True)

        button = discord.ui.Button(label="verify✅", style=discord.ButtonStyle.primary)
        button.callback = button_callback
        view.add_item(button)

        await ch.send(embed=embed, view=view)
        await interaction.response.send_message("認証パネルを設定しました。", ephemeral=True)



@tree.command(name='nuke', description='ログを削除します') 
async def DELETE(message: discord.Interaction):
        if message.user.guild_permissions.administrator:
            await message.channel.purge()
            await message.channel.send('Log Delete')
        else:
            await message.channel.send('あなたは管理者ではありません')        



bot.run(TOKEN)