from aiogram.fsm.state import State, StatesGroup


class StateEmail(StatesGroup):
    email_state = State()


class StatePhone(StatesGroup):
    phone_state = State()


#class StateAuth(StatesGroup):
#    auth_state = State()


class StateNewAdmin(StatesGroup):
    new_admin_state = State()


class StateDelAdmin(StatesGroup):
    del_admin_state = State()


