import os
import json
import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import aiohttp

class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix="!", intents=intents, case_insensitive=True)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.tree.sync()
        # Start the user check loop
        asyncio.create_task(self.check_user_status())

    async def check_user_status(self):
        while True:
            print("체크 중...")
            user_data = await self.get_user_data(user_id)

            if user_data:
                is_unbanned = user_data.get("isBanned")
                if is_unbanned == False:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    nickname = user_data.get("name", "Unknown User")
                    thumbnail_url = await self.get_thumbnail_url(user_id)

                    webhook_url = os.getenv("WEBHOOK_URL")
                    payload = {
                        "content": "@everyone 경! 축!",
                        "embeds": [
                            {
                                "title": f"{nickname}의 계정 정지가 풀렸습니다!",
                                "description": f"```\n삭제된 시간 : {current_time}\n```\n```\n계정 상태 : 계정 정지가 풀림 ❌\n```",
                                "url": f"https://www.roblox.com/users/{user_id}/profile",
                                "color": 7864189,
                                "thumbnail": {
                                    "url": thumbnail_url
                                }
                            }
                        ],
                        "attachments": []
                    }
                    headers = {'Content-Type': 'application/json'}
                    async with aiohttp.ClientSession() as session:
                        async with session.post(webhook_url, json=payload, headers=headers) as response:
                            print("Webhook response:", response.status)
            else:
                print("Failed to retrieve user data.")

            await asyncio.sleep(0.5)

    async def get_user_data(self, user_id):
        url = f"https://users.roblox.com/v1/users/{user_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return user_data
                else:
                    print("Failed to retrieve user data. Status code:", response.status)
                    return None

    async def get_thumbnail_url(self, user_id):
        url = f"https://thumbnails.roproxy.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["data"][0]["imageUrl"] if data["data"] else None
                else:
                    print("Failed to retrieve thumbnail URL. Status code:", response.status)
                    return None

intents = discord.Intents.all()
bot = Bot(intents=intents)

RENDER_URL = "https://url-here"
TOKEN = os.getenv("BOT_TOKEN")
user_id = os.getenv("USER_ID")
webhook_url_s = os.getenv("WEBHOOK_URL")

# SETTING

@bot.hybrid_command(name='밴-체크봇-상태', description='봇 상태를 확인합니다.')
async def check_bot(interaction: discord.Interaction):
    response = requests.get(url=RENDER_URL)
    if response.status_code == 200 or 304:
        embed = discord.Embed(
            title=":white_check_mark: 여전히 작동중!! :white_check_mark:",
            description=f"```ansi\n\u001b[1;32m응답 코드 : {response.status_code}\n```\n```ansi\n\u001b[1;32m응답 메시지 : {response.text}\n```", 
            color=65280
        )
        await interaction.send(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=":x: 작동 중이지 않습니다! :x:",
            description=f"```ansi\n\u001b[1;32m응답 코드 : {response.status_code}\n```\n```ansi\n\u001b[1;32m응답 메시지 : {response.text}\n```", 
            color=16711680
        )
        await interaction.send(embed=embed, ephemeral=True)

@bot.hybrid_command(name='설정-상태', description='당신의 설정 상태를 확인합니다.')
async def setting_status(interaction: discord.Interaction):
    embed = discord.Embed(
        title="당신의 설정 상태",
        color=65000,
        description=f"[당신이 설정한 로블록스 유저 프로필 링크](https://www.roblox.com/users/{user_id}/profile)"
    )
    embed.add_field(
        name="웹훅",
        value=f"```\n{webhook_url_s}\n```",
        inline=False
    )
    embed.add_field(
        name="설정한 로블록스 유저 ID",
        value=f"```\n{user_id}\n```",
        inline=False
    )
    await interaction.send(embed=embed, ephemeral=True)

bot.run(TOKEN)
