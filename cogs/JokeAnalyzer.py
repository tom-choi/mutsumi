import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import aiohttp
import json
import base64
import asyncio
from openai import OpenAI
import logging

# 设置日志记录
logger = logging.getLogger(__name__)

class JokeAnalyzer(commands.Cog, name="joke_analyzer"):
    def __init__(self, bot) -> None:
        self.bot = bot
        
        # DeepSeek配置
        self.DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
        self.DEEPSEEK_MODEL = "deepseek-chat"
        self.deepseek_api_key = os.getenv("DSAPI")
        
        # MiniMax配置
        self.MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
        self.minimax_client = None
        if self.MINIMAX_API_KEY:
            self.minimax_client = OpenAI(
                api_key=self.MINIMAX_API_KEY,
                base_url="https://api.minimaxi.com/v1",
                timeout=30.0  # 增加超时时间
            )
        
        # 表情触发设置
        self.EMOJI_TRIGGER = "🤡"
        self.MAX_TOKENS = 150
        self.ANALYSIS_PROMPT = (
            "你是一個專業的笑話分析師。請用簡短幽默的風格解析以下內容的幽默點，如果是某種遊戲或動畫、戲劇參考，請指出作品名稱。"
            "分析笑點結構、預期違反和語言技巧。如果內容不是笑話，強行找到其中的幽默之處，並保持高情商回應。"
            "保持回應在100字以內，最後輸出'令人忍俊不禁。'。"
        )

    async def analyze_text_joke(self, content: str) -> str:
        """使用DeepSeek分析文字笑話"""
        if not self.deepseek_api_key:
            return "❌ DeepSeek API金鑰未配置，無法分析笑話"
        
        headers = {"Authorization": f"Bearer {self.deepseek_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": self.ANALYSIS_PROMPT},
                {"role": "user", "content": content}
            ],
            "max_tokens": self.MAX_TOKENS,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    self.DEEPSEEK_API_URL, 
                    headers=headers, 
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"DeepSeek API錯誤 (狀態碼: {response.status})")
                        return f"❌ API錯誤 (狀態碼: {response.status})"
                    
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.exception("文字分析失敗")
            return f"❌ 分析失敗: {str(e)}"
    
    async def analyze_image_joke(self, image_url: str) -> str:
        """使用MiniMax多模態API分析圖片笑點"""
        if not self.minimax_client:
            return "❌ MiniMax API金鑰未配置，無法分析圖片"
        
        messages = [
            {
                "role": "system",
                "content": "MM智能助理是一款由MiniMax自研的，沒有調用其他產品的接口的大型語言模型。"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self.ANALYSIS_PROMPT},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
        
        try:
            # 添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    completion = self.minimax_client.chat.completions.create(
                        model="MiniMax-Text-01",
                        messages=messages,
                        max_tokens=4096
                    )
                    return completion.choices[0].message.content
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"MiniMax API重試中 ({attempt+1}/{max_retries})")
                        await asyncio.sleep(2)  # 等待2秒后重试
                    else:
                        raise
        except Exception as e:
            logger.exception("圖片分析失敗")
            return f"❌ 圖片分析失敗: {str(e)}"
    
    @commands.hybrid_command(
        name="analyzejoke",
        description="分析神人笑話",
    )
    @app_commands.describe(content="要分析的笑話內容或圖片URL")
    async def analyze_joke_command(self, context: Context, *, content: str) -> None:
        """命令觸發笑話分析（支持文字和圖片URL）"""
        # 檢查是否為圖片URL
        if content.startswith("http") and any(content.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
            await context.send(f"🔍 正在分析圖片笑點...")
            analysis = await self.analyze_image_joke(content)
            title = "🤖 圖片笑話分析報告"
        else:
            if len(content) > 500:
                await context.send("❌ 內容太長了！請限制在500字以內")
                return
            await context.send(f"🔍 正在分析笑話...")
            analysis = await self.analyze_text_joke(content)
            title = "🤖 笑話分析報告"
        
        # 創建回應
        embed = discord.Embed(
            title=title,
            description=analysis[:2000],  # 限制描述长度
            color=0x097969  # 綠色
        )
        embed.add_field(name="原始內容", value=f"```{content[:200]}...```", inline=False)
        embed.set_footer(text="由 Mortis AI 提供分析")
        await context.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """當用戶添加🤡表情時觸發分析（支持文字和圖片）"""
        # 忽略機器人自己的反應
        if user.bot:
            return
        
        # 檢查是否是目標emoji
        if str(reaction.emoji) != self.EMOJI_TRIGGER:
            return
        
        message = reaction.message
        
        # 忽略空消息或機器人消息
        if not message.content and not message.attachments:
            return
        
        # 顯示處理中反應
        await message.add_reaction("🔍")
        
        analysis = ""
        title = ""
        content_source = ""
        is_image = False
        
        # 優先處理圖片附件
        if message.attachments:
            attachment = message.attachments[0]
            if attachment.content_type and attachment.content_type.startswith('image'):
                content_source = attachment.url
                analysis = await self.analyze_image_joke(attachment.url)
                title = "🤖 自動圖片笑點分析"
                is_image = True
        
        # 如果沒有圖片附件，處理文字內容
        elif message.content:
            if len(message.content) > 500:
                await message.reply("❌ 消息太長無法分析！請限制在500字以內")
                await message.remove_reaction("🔍", self.bot.user)
                return
            
            content_source = message.content
            analysis = await self.analyze_text_joke(message.content)
            title = "🤖 自動笑點分析"
        else:
            await message.remove_reaction("🔍", self.bot.user)
            return
        
        # 創建分析報告
        embed = discord.Embed(
            title=title,
            description=analysis[:2000],  # 限制描述长度
            color=0x097969  # 綠色
        )
        
        # 根據內容類型添加不同字段
        if is_image:
            embed.set_image(url=content_source)
            embed.add_field(
                name="原始圖片", 
                value=f"[跳轉到消息]({message.jump_url})",
                inline=False
            )
        else:
            embed.add_field(
                name="原始消息", 
                value=f"{content_source[:150]}...\n[跳轉到消息]({message.jump_url})",
                inline=False
            )
        
        embed.set_author(
            name=f"{user.display_name} 要求分析", 
            icon_url=user.display_avatar.url
        )
        
        try:
            # 發送分析結果
            await message.reply(embed=embed)
        except Exception as e:
            logger.error(f"發送分析結果失敗: {str(e)}")
            await message.reply(f"❌ 發送分析結果失敗: {str(e)}")
        finally:
            await message.remove_reaction("🔍", self.bot.user)

async def setup(bot) -> None:
    # 檢查API金鑰配置
    bot.deepseek_api_key = os.getenv("DSAPI")
    bot.minimax_api_key = os.getenv("MINIMAX_API_KEY")
    
    if not bot.deepseek_api_key:
        logger.warning("⚠️ DeepSeek API金鑰未配置，文字分析功能將受限")
    if not bot.minimax_api_key:
        logger.warning("⚠️ MiniMax API金鑰未配置，圖片分析功能將受限")
    
    await bot.add_cog(JokeAnalyzer(bot))