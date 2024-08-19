import telebot
import mysql.connector
from utils import get_db_connection#, execute_ch
from settings import MYSQL_DB, ENVIRONMENT
from settings import TG_TOKEN
from datetime import datetime



    # Функция для валидации номера телефона и преобразования его в международный формат


def validate_phone_number(phone_number):
    if phone_number:
    # Удаляем ненужные символы из номера телефона
        for sym in ['-', ' ', '(', ')']:
            phone_number = phone_number.replace(sym, '')
    # Если номер начинается с '8', заменяем на '+7'
        if phone_number[0] == '8':
            result = '+7' + phone_number[1:]
            return result if len(result) >= 12 else None
    # Если номер начинается с '7' и его длина 11 символов, добавляем '+'
        if phone_number[0] == '7' and len(phone_number) == 11:
            return '+' + phone_number
        else:
    # В остальных случаях проверяем длину номера и добавляем '+'
            return '+' + phone_number if len(phone_number) >= 12 else None


def get_users_from_mysql():
    conn_mysql = mysql.connector.connect(
        host=MYSQL_DB.get('HOST'),
        port=MYSQL_DB.get('PORT'),
        database=MYSQL_DB.get('NAME'),
        user=MYSQL_DB.get('USER'),
        password=MYSQL_DB.get('PASSWORD')
    )
    try:
        cur_mysql = conn_mysql.cursor()
        user_data_statement = '''
            SELECT phone, id, is_active, card_number, registration_date, name FROM users
        '''
        cur_mysql.execute(user_data_statement)
        users_bitrix = cur_mysql.fetchall()
    finally:
        cur_mysql.close()
        conn_mysql.close()
    return users_bitrix


if __name__ == '__main__':
    # Инициализация бота с токеном
    bot = telebot.TeleBot(TG_TOKEN)
    # Установка соединения с базой данных
    conn = get_db_connection()
    cur = conn.cursor()

    # Выполняем запрос для получения количества доступных прокси

    cur.execute('select count(*) from proxy where is_busy is false and is_healthy is true;')
    total_available_proxy = cur.fetchone()

    # Отправляем информацию о количестве доступных прокси пользователям

    for chat_id in [749619659, 750668606, 503185188]:
        # Выбираем имя бота в зависимости от окружения
        bot_name = '@MPKESHBECK_bot' if ENVIRONMENT.value == "SHOPOGOLIK" else '@AuthWbBot'
        try:
            bot.send_message(chat_id, f'Свободных прокси у бота {bot_name}: {total_available_proxy[0]}')
        except Exception as e:
            print('Telegram Error:', e)

    try:
    # Формируем запрос для получения данных пользователей из MySQL

        users_bitrix = get_users_from_mysql()
        for user in users_bitrix:
            try:
                reg_date = user[4].date() if isinstance(user[4], datetime) else user[4]
            except Exception as e:
                print('Date Processing Error:', e)
                reg_date = user[4]

            secure_card = None
            if user[3]:
                secure_card = user[3][:6] + "******" + user[3][-4:]

            result = (
                validate_phone_number(user[0]),  # phone_number
                user[1],  # bitrix_id
                user[2],  # is_active
                user[3],  # card_number
                reg_date,  # registration_date
                user[5],  # name
                secure_card  # secure_card
            )
            print(result)

            insert_statement = f'''
                INSERT INTO vectors_manager 
                (phone_number, bitrix_id, is_active, card_number, registration_date, name, secure_card) 
                VALUES (%s,%s,%s,%s,%s,%s,%s) on conflict(bitrix_id) DO NOTHING; 
                '''
            try:
                cur.execute(insert_statement, result)
                conn.commit()
            except Exception as e:
                print('Database Error:', e)
                conn.rollback()
    finally:
        cur.close()
        conn.close()


# Функция для валидации номера телефона в ClickHouse
# Clickhouse validate func
# import sys
# if __name__ == '__main__':
#     for phone_number in sys.stdin:
#         for sym in ['-', ' ', '(', ')']:
#             phone_number.replace(sym, '')
#         if phone_number[0] == '8':
#             result = '+7' + phone_number[1:]
#             if len(result) == 12:
#                 print(result, end='')
#             else:
#                 print('', end='')
#         sys.stdout.flush()