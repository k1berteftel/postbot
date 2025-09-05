from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager, StartMode, ShowMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.action_data_class import DataInteraction
from states.state_groups import startSG


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager):
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK)


@user_router.callback_query(F.data == 'menu')
async def main_menu(clb: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


@user_router.channel_post()
async def send_channel_post(msg: Message, session: DataInteraction, scheduler: AsyncIOScheduler):
    channels = await session.get_channels()
    for channel in channels:
        if msg.chat.username and '@' + msg.chat.username == channel.channel:
            await session.add_channel_post(channel.id)
            channel = await session.get_channel(channel.id)
            if channel.posts >= channel.count:
                text = ''
                text += (f'🚨В канале {channel.channel} вышло {channel.posts} постов (больше чем {channel.count})'
                         f'\nОстановите публикацию постов в каналах:\n')
                for warn_channel in channel.warning_channels:
                    text += warn_channel + '\n'
                buttons = [[InlineKeyboardButton(text=warn_channel[1], url=f'https://t.me/{warn_channel[0][1::]}')]
                           for warn_channel in channel.warning_channels]
                buttons.append([InlineKeyboardButton(text='На главное меню', callback_data='menu')])
                for user in [5462623909, 1236300146]:
                    await msg.bot.send_message(
                        chat_id=user,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                    )
                text = 'Остановите публикацию постов в каналах:\n'
                for warn_channel in channel.warning_channels:
                    text += warn_channel + '\n'
                await msg.bot.send_message(
                    chat_id=965916015,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )

