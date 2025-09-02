from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog import getters

from states.state_groups import startSG, adminSG

user_dialog = Dialog(
    Window(
        Const('Главное меню'),
        Column(
            SwitchTo(Const('Добавить канал'), id='get_parse_channels_switcher', state=startSG.get_post_channel),
            SwitchTo(Const('Удалить канал'), id='del_parse_channels_switcher', state=startSG.del_channels),
            SwitchTo(Const('Просмотреть каналы'), id='show_channels_switcher', state=startSG.watch_channels),
        ),
        state=startSG.start
    ),
    Window(
        Const('Введите ссылку канал для подсчета постов\n\nДопустимый '
              'формат ввода:\n'
              'https://t.me/room_RO (ссылка)\n@room_RO (юзернейм)\n-1001053645184 (ID)'),
        TextInput(
            id='get_post_channel',
            on_success=getters.get_post_channel
        ),
        SwitchTo(Const('◀️Назад'), id='back', state=startSG.start),
        state=startSG.get_post_channel
    ),
    Window(
        Const('Введите каналы для контроля\n\nДопустимый '
              'формат ввода (каналы разделяются абзацами):\n'
              'https://t.me/room_RO (ссылка)\n@room_RO (юзернейм)\n-1001053645184 (ID)'),
        TextInput(
            id='get_notification_channel',
            on_success=getters.get_notification_channel
        ),
        SwitchTo(Const('◀️Назад'), id='back_get_post_channel', state=startSG.get_post_channel),
        state=startSG.get_notification_channel
    ),
    Window(
        Const('Введите количество постов за сутки (число)'),
        TextInput(
            id='get_warning_count',
            on_success=getters.get_warning_count
        ),
        SwitchTo(Const('◀️Назад'), id='back_get_notification_channel', state=startSG.get_notification_channel),
        state=startSG.get_warning_count
    ),
    Window(
        Format('При публикации «{count}» и более постов в канале {post_channel} прислать уведомление 🔔'),
        Row(
            Button(Const('Подтвердить'), id='save_channels', on_click=getters.save_channels),
            SwitchTo(Const('Отмена'), id='save_cancel', state=startSG.start),
        ),
        SwitchTo(Const('◀️Назад'), id='back_warning_count', state=startSG.get_warning_count),
        getter=getters.confirm_save_getter,
        state=startSG.confirm_save
    ),
    Window(
        Const('Выберите канал, который вы хотели бы удалить:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='del_channels_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_channel_selector
            ),
            width=1
        ),
        SwitchTo(Const('◀️Назад'), id='back', state=startSG.start),
        getter=getters.del_channels_getter,
        state=startSG.del_channels
    ),
    Window(
        Format('Вы действительно хотите удалить данный канал "{channel}"'),
        Row(
            Button(Const('Да'), id='del_channel', on_click=getters.del_channel),
            SwitchTo(Const('Отмена'), id='back_del_channels', state=startSG.del_channels),
        ),
        getter=getters.confirm_del_channel_getter,
        state=startSG.confirm_del_channel,
    ),
    Window(
        Const('Действующие каналы для подсчета постов и каналы для отмены'),
        Format('{text}'),
        Column(
            SwitchTo(Const('Изменить данные'), id='choose_channel_switcher', state=startSG.choose_channel),
        ),
        SwitchTo(Const('◀️Назад'), id='back', state=startSG.start),
        getter=getters.watch_channels_getter,
        state=startSG.watch_channels
    ),
    Window(
        Const('Выберите канал для изменения'),
        Group(
            Select(
                Format('{item[0]}'),
                id='choose_channels_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_channel_selector
            ),
            width=1
        ),
        SwitchTo(Const('◀️Назад'), id='back_watch_channels', state=startSG.watch_channels),
        getter=getters.choose_channel_getter,
        state=startSG.choose_channel
    ),
    Window(
        Const('Выберите пункт, который вы хотели бы изменить для канала:'),
        Format('{text}'),
        Column(
            Button(Const('Канал для подсчета'), id='channel_change_choose', on_click=getters.change_choose),
            Button(Const('Кол-во постов'), id='count_change_choose', on_click=getters.change_choose),
            Button(Const('Список каналов для контроля'), id='warning_change_choose', on_click=getters.change_choose),
        ),
        SwitchTo(Const('◀️Назад'), id='back_choose_channel', state=startSG.choose_channel),
        getter=getters.change_channel_menu_getter,
        state=startSG.change_channel_menu
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_change_data',
            on_success=getters.get_change_data
        ),
        SwitchTo(Const('◀️Назад'), id='back_change_channel_menu', state=startSG.change_channel_menu),
        getter=getters.get_change_data_getter,
        state=startSG.get_change_data
    ),
)