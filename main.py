import os
import pytube
import asyncio
from aiogram import Bot, Dispatcher, types
from config import API_TOKEN

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
yt = None


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Greet user after /start or /help command"""

    name = message.from_user.first_name + message.from_user.last_name if message.from_user.last_name \
        else message.from_user.first_name
    welcome_message = f"Hello, {name}!\nSend me a link to a YouTube video and I'll download it for you."
    await bot.send_message(message.chat.id, welcome_message)

    # Remove all .mp4 files
    dir_name = "/Users/nurto/PycharmProjects/YouTube Downloader Aiogram"
    files = os.listdir(dir_name)

    for item in files:
        if item.endswith(".mp4"):
            os.remove(os.path.join(dir_name, item))


async def youtube_download(message, path, call):
    """Dowmload YouTube video by pytube"""

    if call == 'High':
        await bot.send_message(message.chat.id, 'Loading...')
        video_path = path.streams.get_highest_resolution().download()
        video = open(video_path, 'rb')

        await bot.send_video(message.chat.id, video)
    else:
        await bot.send_message(message.chat.id, 'Loading...')
        video_path = path.streams.first().download()
        video_path_copy = video_path.split('\\')[-1]
        name = video_path_copy.split('.')[0]
        result = name + '.mp4'
        os.rename(video_path, result)
        video = open(result, 'rb')

        await bot.send_video(message.chat.id, video)


@dp.message_handler(content_types=['text'])
async def get_message(message: types.Message):
    """Get link from YouTube"""

    # Remove all .mp4 files
    dir_name = "/Users/nurto/PycharmProjects/YouTube Downloader Aiogram"
    files = os.listdir(dir_name)

    for item in files:
        if item.endswith(".mp4"):
            os.remove(os.path.join(dir_name, item))

    try:
        global yt
        yt = pytube.YouTube(message.text)

    except pytube.exceptions.RegexMatchError:
        error_message = "It doesn't look like a YouTube video link :(\nTry again."
        await bot.send_message(message.chat.id, error_message)

    keyboard = types.InlineKeyboardMarkup()
    high = types.InlineKeyboardButton('High', callback_data='High')
    low = types.InlineKeyboardButton('Low', callback_data='Low')
    keyboard.add(high, low)
    await bot.send_message(message.chat.id, 'Choose resolution:', reply_markup=keyboard)


@dp.callback_query_handler(text=['High', 'Low'])
async def download(callback: types.CallbackQuery):
    """Get callback data and call youtube_download"""

    await youtube_download(callback.message, yt, callback.data)


async def main():
    await dp.start_polling(dp)

if __name__ == '__main__':
    asyncio.run(main())
