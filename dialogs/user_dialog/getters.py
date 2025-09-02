from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG


config: Config = load_config()


async def get_post_channel(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    channel = text.strip()
    post_channel = ''
    if channel.startswith('@'):
        post_channel = channel
    if channel.startswith('https') or channel.startswith('t.me'):
        post_channel = '@' + channel.split('/')[-1]
    try:
        channel = int(channel)
        channel = await msg.bot.get_chat(channel)
        post_channel = '@' + channel.username
    except Exception:
        ...
    if not post_channel:
        await msg.answer('Ни один канал не удалось распознать, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['post_channel'] = post_channel
    await dialog_manager.switch_to(startSG.get_notification_channel)


async def get_notification_channel(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    channels = text.strip().split('\n')
    warning_channels = []
    for channel in channels:
        if channel.startswith('@'):
            warning_channels.append(channel)
        if channel.startswith('https') or channel.startswith('t.me'):
            warning_channels.append('@' + channel.split('/')[-1])
        try:
            channel = int(channel)
            channel = await msg.bot.get_chat(channel)
            warning_channels.append('@' + channel.username)
        except Exception:
            ...
    if not warning_channels:
        await msg.answer('Ни один канал не удалось распознать, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['warning_channels'] = warning_channels
    await dialog_manager.switch_to(state=startSG.get_warning_count)


async def get_warning_count(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        count = int(text)
    except Exception:
        await msg.delete()
        await msg.answer('Кол-во постов для оповещения должно быть числом, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['count'] = count
    await dialog_manager.switch_to(state=startSG.confirm_save)


async def confirm_save_getter(dialog_manager: DialogManager, **kwargs):
    count = dialog_manager.dialog_data.get('count')
    post_channel = dialog_manager.dialog_data.get('post_channel')
    return {
        'count': count,
        'post_channel': post_channel
    }


async def save_channels(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    count = dialog_manager.dialog_data.get('count')
    post_channel = dialog_manager.dialog_data.get('post_channel')
    warning_channels = dialog_manager.dialog_data.get('warning_channels')
    await session.add_channel(post_channel, count, warning_channels)
    await clb.message.answer('Канал был успешно добавлен')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(startSG.start)


async def del_channels_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channels = await session.get_channels()
    buttons = [(channel.channel, channel.id) for channel in channels]
    return {
        'items': buttons
    }


async def del_channel_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['channel_id'] = int(item_id)
    await dialog_manager.switch_to(startSG.confirm_del_channel)


async def confirm_del_channel_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channel_id = dialog_manager.dialog_data.get('channel_id')
    channel = await session.get_channel(channel_id)
    return {
        'channel': channel.channel
    }


async def del_channel(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channel_id = dialog_manager.dialog_data.get('channel_id')
    await session.del_channel(channel_id)
    await clb.message.answer('Канал был успешно удален')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(startSG.start)


async def watch_channels_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channels = await session.get_channels()
    text = ''
    for channel in channels:
        text += f'Канал "{channel.channel}" ({channel.count})'
        for warn_channel in channel.warning_channels:
            text += f'\n - {warn_channel}'
        text += '\n\n'
    return {'text': text}


async def choose_channel_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channels = await session.get_channels()
    buttons = [(channel.channel, channel.id) for channel in channels]
    return {
        'items': buttons
    }


async def choose_channel_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['channel_id'] = int(item_id)
    await dialog_manager.switch_to(startSG.change_channel_menu)


async def change_channel_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channel_id = dialog_manager.dialog_data.get('channel_id')
    channel = await session.get_channel(channel_id)
    text = ''
    text += f'Канал "{channel.channel}" ({channel.count})'
    for warn_channel in channel.warning_channels:
        text += f'\n - {warn_channel}'

    return {'text': text}


async def change_choose(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    choose = clb.data.split('_')[0]
    if choose == 'warning':
        choose = 'warning_channels'
    dialog_manager.dialog_data['column'] = choose
    await dialog_manager.switch_to(startSG.get_change_data)


async def get_change_data_getter(dialog_manager: DialogManager, **kwargs):
    column = dialog_manager.dialog_data.get('column')
    if column == 'channel':
        text = 'Введите новый канал для подсчета постов'
    elif column == 'count':
        text = 'Введите кол-во постов для уведомления'
    else:
        text = 'Введите каналы для контроля'

    return {'text': text}


async def get_change_data(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    column = dialog_manager.dialog_data.get('column')
    text = text.strip()
    if column == 'channel':
        post_channel = ''
        if text.startswith('@'):
            post_channel = text
        if text.startswith('https') or text.startswith('t.me'):
            post_channel = '@' + text.split('/')[-1]
        try:
            channel = int(text)
            channel = await msg.bot.get_chat(channel)
            post_channel = '@' + channel.username
        except Exception:
            ...
        if not post_channel:
            await msg.answer('Ни один канал не удалось распознать, пожалуйста попробуйте снова')
            return
        data = post_channel
    elif column == 'count':
        try:
            count = int(text)
        except Exception:
            await msg.delete()
            await msg.answer('Кол-во постов для оповещения должно быть числом, пожалуйста попробуйте снова')
            return
        data = count
    else:
        channels = text.split('\n')
        warning_channels = []
        for channel in channels:
            if channel.startswith('@'):
                warning_channels.append(channel)
            if channel.startswith('https') or channel.startswith('t.me'):
                warning_channels.append('@' + channel.split('/')[-1])
            try:
                channel = int(channel)
                channel = await msg.bot.get_chat(channel)
                warning_channels.append('@' + channel.username)
            except Exception:
                ...
        if not warning_channels:
            await msg.answer('Ни один канал не удалось распознать, пожалуйста попробуйте снова')
            return
        data = warning_channels
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    channel_id = dialog_manager.dialog_data.get('channel_id')
    kwargs = {column: data}
    await session.update_channel(channel_id, **kwargs)
    await msg.answer('Данные были успешно обновлены')
    await dialog_manager.switch_to(startSG.change_channel_menu)