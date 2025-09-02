from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()

    get_post_channel = State()
    get_notification_channel = State()
    get_warning_count = State()
    confirm_save = State()

    del_channels = State()
    confirm_del_channel = State()

    watch_channels = State()

    choose_channel = State()
    change_channel_menu = State()
    get_change_data = State()


class adminSG(StatesGroup):
    start = State()
    get_mail = State()
    get_time = State()
    get_keyboard = State()
    confirm_mail = State()
    deeplink_menu = State()
    deeplink_del = State()
    admin_menu = State()
    admin_del = State()
    admin_add = State()
