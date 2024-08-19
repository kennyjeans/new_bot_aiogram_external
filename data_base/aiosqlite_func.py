import aiosqlite as sq
import asyncio


async def create_data_base():
    async with sq.connect(database="C:\\Users\\user\\Desktop\\aiorgam_external_bot\\data_base\\data_base_bot\\data_base_bot.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS data_msd(
                            user_id INTEGER,
                            registration INTEGER,
                            edit_start_auth INTEGER,
                            shopping INTEGER,
                            edit_wb_auth INTEGER,
                            edit_products INTEGER
                            )""")
        await db.commit()
        await db.close()


#зполняем id собщений при Начатом процессе авторизации
async def insert_registration_data(user_id, message_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""INSERT INTO data_msd(user_id, registration) VALUES (?, ?)""", [user_id, message_id])
        await db.commit()
        await db.close()


#зполняем id собщений при Начатом процессе авторизации
async def insert_edit_start_auth(user_id, message_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""INSERT INTO data_msd(user_id, edit_start_auth) VALUES (?, ?)""", [user_id, message_id])
        await db.commit()
        await db.close()


#зполняем id собщений при условии что пользователь уже авторизован
async def insert_shopping(user_id, message_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""INSERT INTO data_msd(user_id, shopping) VALUES (?, ?)""", [user_id, message_id])
        await db.commit()
        await db.close()


#вытаскиваем все id сообщений полученные при регистрации (email, phone)
async def select_registration(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT registration FROM data_msd 
                                     WHERE user_id = (?) AND registration IS NOT NULL""",
                              [user_id]) as cur:
            data = await cur.fetchall()
            return data #data[0][0], data[1][0]


#вытаскиваем все id сообщений полученные при Начатом процессе авторизации
async def select_edit_start_auth(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT edit_start_auth FROM data_msd 
                                     WHERE user_id = (?) AND edit_start_auth IS NOT NULL""",
                              [user_id]) as cur:
            data = await cur.fetchall()
            return data #data[0][0], data[1][0]


#удаляем msd_id из бд
async def delete_message_id_registration(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""DELETE FROM data_msd WHERE user_id = (?) AND registration IS NOT NULL""", [user_id])
        await db.commit()
        await db.close()


async def delete_edit_start_auth(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""DELETE FROM data_msd WHERE user_id = (?) AND edit_start_auth IS NOT NULL""", [user_id])
        await db.commit()
        await db.close()


async def delete_shopping(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""DELETE FROM data_msd WHERE user_id = (?) AND shopping IS NOT NULL""", [user_id])
        await db.commit()
        await db.close()


async def create_table_state():
    async with sq.connect(database="C:\\Users\\Admin\\Desktop\\aiogram_wb_auth\\data_base\\data_base_bot\\data_base_bot.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS state_auth(
                            user_id INTEGER,
                            captcha BOOL,
                            sms BOOL
                            )""")
        await db.commit()
        await db.close()


async def state_clear_auth(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""UPDATE state_auth SET captcha = (?), sms = (?) WHERE user_id = (?)""",
                         [False, False, user_id])
        await db.commit()
        await db.close()


async def set_state_auth(user_id, state):
    """
    state:
    sms: str
    cp: str
    """
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT * FROM state_auth WHERE user_id = (?)""", [user_id]) as cur:
            data = await cur.fetchone()
            if data is None:
                await db.execute("""INSERT INTO state_auth(user_id) VALUES (?)""", [user_id])

        if state == "sms":
            await db.execute("""UPDATE state_auth SET captcha = (?), sms = (?) WHERE user_id = (?)""",
                             [False, True, user_id])

        elif state == "cp":
            await db.execute("""UPDATE state_auth SET captcha = (?), sms = (?) WHERE user_id = (?)""",
                             [True, False, user_id])

        await db.commit()
        await db.close()


async def check_state(user_id):
    await asyncio.sleep(1)
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT * FROM state_auth WHERE user_id = (?)""", [user_id]) as cur:
            data = await cur.fetchone()
            if data is not None:
                if data[1] is True or data[1] == 1:
                    return "cp"
                elif data[2] is True or data[2] == 1:
                    return "sms"
                return

            #data = asyncio.run(select_registration(323))
#print(data[0][0], data[1][0])#
#asyncio.run(delete_message_id_registration(323))
#asyncio.run(create_data_base())
#asyncio.run(create_table_state())


async def create_admin_table():
    async with sq.connect(database="C:\\Users\\user\\Desktop\\aiorgam_external_bot\\data_base\\data_base_bot\\data_base_bot.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS admins(
                            user_id INTEGER,
                            name TEXT
                            )""")
        await db.commit()
        await db.close()
        return


async def new_admin(user_id, name):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""INSERT INTO admins(user_id, name) VALUES (?, ?)""",
                         [int(user_id), str(name)])
        await db.commit()
        await db.close()
        return


async def check_admin(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT * FROM admins WHERE user_id = (?)""",
                              [user_id]) as cur:
            admin = await cur.fetchone()
            if admin is not None:
                return True
            else:
                return False


async def select_admins():
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT user_id FROM admins""") as cur:
            admins = await cur.fetchall()
            return admins


async def create_table_sms_cp():
    async with sq.connect(database="C:\\Users\\user\\Desktop\\aiorgam_external_bot\\data_base\\"
                                   "data_base_bot\\data_base_bot.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS cp_sms_quan(
                            user_id INTEGER,
                            cp INTEGER,
                            sms INTEGER,
                            resend INTEGER
                            )""")
        await db.commit()
        await db.close()
        return


async def update_sms_quan(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT sms FROM cp_sms_quan WHERE user_id = (?)""", [user_id]) as cur:
            quan_sms = await cur.fetchone()
        await db.execute("""UPDATE cp_sms_quan SET sms = (?) WHERE user_id = (?)""",
                         [quan_sms[0] + 1, user_id])
        await db.commit()
        await db.close()
        return


async def update_cp_quan(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT cp FROM cp_sms_quan WHERE user_id = (?)""", [user_id]) as cur:
            quan_cp = await cur.fetchone()
        await db.execute("""UPDATE cp_sms_quan SET cp = (?) WHERE user_id = (?)""",
                         [quan_cp[0] + 1, user_id])
        await db.commit()
        await db.close()


async def update_resend(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT resend FROM cp_sms_quan WHERE user_id = (?)""", [user_id]) as cur:
            quan_cp = await cur.fetchone()
        await db.execute("""UPDATE cp_sms_quan SET cp = (?) WHERE user_id = (?)""",
                         [quan_cp[0] + 1, user_id])
        await db.commit()
        await db.close()


async def select_cp_sms(user_id, find_is):
    """
    user_id = user_id
    find_is = "sms" or "cp" or "resend"
    """
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        if find_is == "sms":
            async with db.execute("""SELECT sms FROM cp_sms_quan WHERE user_id = (?)""",
                                  [user_id]) as cur:
                data = await cur.fetchone()
                return data[0]
        elif find_is == "cp":
            async with db.execute("""SELECT cp FROM cp_sms_quan WHERE user_id = (?)""",
                                  [user_id]) as cur:
                data = await cur.fetchone()
                return data[0]

        elif find_is == "resend":
            async with db.execute("""SELECT resend FROM cp_sms_quan WHERE user_id = (?)""",
                                  [user_id]) as cur:
                data = await cur.fetchone()
                return data[0]
        else:
            print("Такого варианта нет")

        await db.close()


async def insert_start_sms_cp(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT * FROM cp_sms_quan WHERE user_id = (?)""", [user_id]) as cur:
            data = await cur.fetchone()
            if data is None:
                await db.execute("""INSERT INTO cp_sms_quan(user_id, cp, sms, resend) VALUES (?, ?, ?, ?)""",
                                 [user_id, 0, 0, 0])
                await db.commit()
            else:
                pass

        await db.close()


async def delete_sms_cp(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""UPDATE cp_sms_quan SET sms = (?), cp = (?), resend = (?) WHERE user_id = (?)""",
                         [0, 0, 0, user_id])
        await db.commit()
        await db.close()


async def delete_edit_wb_auth(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""DELETE FROM data_msd WHERE user_id = (?) AND edit_wb_auth IS NOT NULL""", [user_id])
        await db.commit()
        await db.close()


async def select_edit_wb_auth(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT edit_wb_auth FROM data_msd 
                                     WHERE user_id = (?) AND edit_wb_auth IS NOT NULL""",
                              [user_id]) as cur:
            data = await cur.fetchall()
            return data #data[0][0], data[1][0]


async def insert_edit_wb_auth(user_id, message_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""INSERT INTO data_msd(user_id, edit_wb_auth) VALUES (?, ?)""", [user_id, message_id])
        await db.commit()
        await db.close()


async def insert_msd_products(user_id, message_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT user_id FROM data_msd WHERE user_id = (?)""",
                              [user_id]) as cur:
            data = await cur.fetchone()
        if data is None:
            await db.execute("""INSERT INTO data_msd(user_id, edit_products) VALUES (?, ?)""",
                             [user_id, message_id])
            await db.commit()
            await db.close()

        else:
            await db.execute("""UPDATE data_msd SET edit_products = (?) WHERE user_id = (?)""",
                             [message_id, user_id])
            await db.commit()
            await db.close()


async def clear_edit_products(message_id, user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""UPDATE edit_products SET edit_products = (?) WHERE user_id = (?)""",
                         [message_id, user_id])
        await db.commit()
        await db.close()


async def select_edit_products(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT edit_products FROM data_msd WHERE user_id = (?) 
                                      AND edit_products IS NOT NULL""",
                              [user_id]) as cur:
            data = await cur.fetchone()
            if data == None:
                return None
            else:
                return data[0]


async def create_table_items_for_confirmation():
    async with sq.connect(database="C:\\Users\\user\\Desktop\\aiorgam_external_bot\\data_base\\data_base_bot\\data_base_bot.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS items_for_confirmation(
                            user_id INTEGER,
                            photo TEXT,
                            order_id INTEGER,
                            article TEXT,
                            page INTEGER,
                            position INTEGER,
                            wb_search_url TEXT,
                            kw TEXT,
                            date_time REAL,
                            status INTEGER
                            )""")
        await db.commit()
        await db.close()


async def insert_items_for_confirmation(user_id, photo, order_id, article, page, position,
                                        wb_search_url, kw, date_time, status):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""INSERT INTO items_for_confirmation(
                            user_id,
                            photo,
                            order_id,
                            article,
                            page,
                            position,
                            wb_search_url,
                            kw,
                            date_time,
                            status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         [int(user_id), photo, int(order_id),
                          article, int(page), int(position),
                          str(wb_search_url), str(kw), date_time,
                          status])
        await db.commit()
        await db.close()


async def delete_items_for_confirmation(user_id, order_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""DELETE FROM items_for_confirmation WHERE user_id = (?) AND order_id = (?)""",
                         [int(user_id),
                          int(order_id)])
        await db.commit()
        await db.close()


async def check_new_products(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT * FROM items_for_confirmation WHERE user_id = (?) 
                                      ORDER BY date_time DESC""",
                              [user_id]) as cur:
            data = await cur.fetchall()
            return data


async def update_status_product(user_id, order_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""UPDATE items_for_confirmation SET status = (?) WHERE user_id = (?) AND order_id = (?)""",
                         [0, user_id, order_id])
        await db.commit()
        await db.close()


async def page_products():
    async with sq.connect(database="C:\\Users\\user\\Desktop\\aiorgam_external_bot\\data_base\\data_base_bot\\data_base_bot.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS page_products(
                            user_id INTEGER,
                            page INTEGER
                            )""")
        await db.commit()
        await db.close()


async def new_insert_or_update_page_products(user_id):
    """
    на первую страницу товаров
    """
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT user_id FROM page_products WHERE user_id = (?)""",
                              [user_id]) as cur:
            data = await cur.fetchone()
        if data is None:
            await db.execute("""INSERT INTO page_products(user_id, page) VALUES (?, ?)""",
                             [user_id, 1])
            await db.commit()
            await db.close()

        else:
            await db.execute("""UPDATE page_products SET page = (?) WHERE user_id = (?)""",
                             [1, user_id])
            await db.commit()
            await db.close()


async def update_page_products(user_id, plus_minus):
    """
    + страница
    - страница
    """
    products = await check_new_products(user_id)
    count_products = len(products)
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT page FROM page_products WHERE user_id = (?)""",
                              [user_id]) as cur:
            page = await cur.fetchone()
            print(page)
        if plus_minus == "+":
            if count_products >= page[0] + 1:
                await db.execute("""UPDATE page_products SET page = (?) WHERE user_id = (?)""",
                                 [page[0] + 1, user_id])
                await db.commit()
                await db.close()
                return True
            else:
                return False
        elif plus_minus == "-":
            if 0 < (page[0] - 1):
                await db.execute("""UPDATE page_products SET page = (?) WHERE user_id = (?)""",
                                 [page[0] - 1, user_id])
                await db.commit()
                await db.close()
                return True
            else:
                return False
        else:
            return False


async def select_page_product(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        async with db.execute("""SELECT page FROM page_products WHERE user_id = (?)""",
                              [user_id]) as cur:
            page = await cur.fetchone()
            return page[0]


async def delete_admin(user_id):
    async with sq.connect(database="data_base/data_base_bot/data_base_bot.db") as db:
        await db.execute("""DELETE FROM admins WHERE user_id = (?)""", [user_id])
        await db.commit()
        await db.close()







#asyncio.run(create_admin_table())
#asyncio.run(select_admins())
#asyncio.run(create_table_sms_cp())
#asyncio.run(delete_message_id_registration(323))
#asyncio.run(create_data_base())
#asyncio.run(create_table_state())
#asyncio.run(create_table_items_for_confirmation())
#asyncio.run(page_products())