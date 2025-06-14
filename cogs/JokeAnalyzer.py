import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import aiohttp
import json

class JokeAnalyzer(commands.Cog, name="joke_analyzer"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
        self.DEEPSEEK_MODEL = "deepseek-chat"
        self.EMOJI_TRIGGER = "🤡"  # 機器人emoji
        self.MAX_TOKENS = 150  # 限制回應長度
        self.ANALYSIS_PROMPT = (
            "你是一個專業的笑話分析師。請用簡短幽默的風格解析以下笑話的幽默點，"
            "分析笑點結構、預期違反和語言技巧。如果內容不是笑話，強行找到其中的幽默之處，並保持高情商回應。"
            "保持回應在100字以內，最後輸出'令人忍俊不禁。'。"
        )

    async def analyze_joke(self, joke_text: str) -> str:
        """使用DeepSeek API分析笑話"""
        if not self.bot.deepseek_api_key:
            return "❌ DeepSeek API金鑰未配置，無法分析笑話"
        
        headers = {
            "Authorization": f"Bearer {self.bot.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": self.ANALYSIS_PROMPT},
                {"role": "user", "content": joke_text}
            ],
            "max_tokens": self.MAX_TOKENS,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.DEEPSEEK_API_URL, 
                    headers=headers, 
                    data=json.dumps(payload)
                ) as response:
                    
                    if response.status != 200:
                        return f"❌ API錯誤 (狀態碼: {response.status})"
                    
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"❌ 分析失敗: {str(e)}"
            

    @commands.hybrid_command(
        name="analyzejoke",
        description="分析神人笑話",
    )
    @app_commands.describe(joke="要分析的笑話內容")
    async def analyze_joke_command(self, context: Context, *, joke: str) -> None:
        """直接命令觸發笑話分析"""
        if len(joke) > 500:
            await context.send("❌ 笑話太長了！請限制在500字以內")
            return
        
        # 顯示處理中訊息
        await context.send(f"🔍 正在分析笑話...")
        
        analysis = await self.analyze_joke(joke)
        embed = discord.Embed(
            title="🤖 笑話分析報告",
            description=analysis,
            color=0x097969  # 綠色
        )
        embed.add_field(name="原始笑話", value=f"```{joke[:200]}...```", inline=False)
        embed.set_footer(text="由 Mortis 提供分析")
        await context.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """當用戶添加機器人emoji時觸發分析"""
        # 忽略機器人自己的反應
        if user.bot:
            return
        
        print(f"Reaction added by {user.display_name}: {reaction.emoji}")

        # 檢查是否是目標emoji
        if str(reaction.emoji) != self.EMOJI_TRIGGER:
            return
        
        message = reaction.message
        print(f"Received reaction from {user.display_name} on message: {message.content}")
        
        # 忽略空消息或機器人消息
        if not message.content or message.author.bot:
            return
        
        # 限制分析長度
        if len(message.content) > 500:
            await message.reply("❌ 消息太長無法分析！請限制在500字以內")
            return
        
        # 顯示處理中反應
        await message.add_reaction("🔍")
        
        # 進行分析
        analysis = await self.analyze_joke(message.content)
        
        # 創建分析報告
        embed = discord.Embed(
            title="🤖 自動笑點分析",
            description=analysis,
            color=0x097969  # 綠色
        )
        embed.add_field(
            name="原始消息", 
            value=f"[跳轉到消息]({message.jump_url})",
            inline=False
        )
        embed.set_author(
            name=f"{user.display_name} 要求分析", 
            icon_url=user.display_avatar.url
        )
        
        # 發送分析結果
        await message.reply(embed=embed)
        await message.remove_reaction("🔍", self.bot.user)

async def setup(bot) -> None:
    # 檢查API金鑰配置
    bot.deepseek_api_key = os.getenv("DSAPI")  # 替換為實際API金鑰
    if not hasattr(bot, "deepseek_api_key"):
        print("⚠️ 警告: DeepSeek API金鑰未配置，笑話分析功能將受限")
    
    await bot.add_cog(JokeAnalyzer(bot))