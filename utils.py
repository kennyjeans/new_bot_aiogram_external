import requests
import psycopg2
import time
import os

from clickhouse_driver import Client

from settings import PG_DB, ENVIRONMENT#, CH_HOST

WB_BASE_URL = 'https://www.wildberries.ru'


def check_proxies_pool(url_test, dc_proxies):

    """
    Проверяет список прокси на доступность.
    Возвращает список рабочих прокси.
    """

    good_proxies = []
    for ind, proxy_name in enumerate(dc_proxies):
        try:
            resp = requests.get(url_test, proxies={'http': proxy_name,
                                                   'https': proxy_name
                                                   })
            if resp.status_code == 200:
                good_proxies.append(proxy_name)
                print(resp.status_code)
                continue
        except:
            print(ind, proxy_name)
    return good_proxies


def get_db_connection():
    """
    Устанавливает соединение с базой данных PostgreSQL.
    Возвращает объект соединения.
    """
    return psycopg2.connect(dbname=PG_DB.get('NAME'),
                            user=PG_DB.get('USER'),
                            password=PG_DB.get('PASSWORD'),
                            host=PG_DB.get('HOST'),
                            port=PG_DB.get('PORT'))


def delete_proxy(phone):
    """
    Удаляем лишни прокси
    :param phone:
    :return:
    """
    list_proxys = os.listdir('proxy_list_phone')
    for i in list_proxys:
        # ищем мусорные прокси по номеру
        # создаем строку
        str_proxy = i.split(".").pop(0).split('_')
        #print(str_proxy)
        if str(str_proxy[3]) == str(phone):
            #print(str_proxy[3])
            if os.path.isfile(f"proxy_list_phone/proxy_auth_plugin_{str(str_proxy[3])}_{str(str_proxy[4])}.zip"):
                os.remove(f"proxy_list_phone/proxy_auth_plugin_{str(str_proxy[3])}_{str(str_proxy[4])}.zip")


def check_proxy(proxy_name, proxy_id):
    """
    Получает рабочий прокси из базы данных.
    Если прокси доступен, обновляет его статус и связывает с пользователем.
    """
    print(proxy_name, proxy_id)
    if ENVIRONMENT.value == 'LOCAL':
        return True
    try:
        print(proxy_name)
        resp = requests.get(WB_BASE_URL, proxies={'http': proxy_name, 'https': proxy_name}, timeout=15)
        print(resp)
        if resp.status_code == 200:
            return True

    except Exception as e:
        print(e)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'update proxy set is_healthy = false where proxy_id = {proxy_id}')
        cur.execute(f'SELECT phone_number FROM auth_user WHERE proxy_id = {proxy_id}')
        phone = cur.fetchone()
        conn.commit()
        #проверяем на наличие неакутального zip plagina, в случае наличия удаляется
        delete_proxy(phone)




def get_valid_proxy(phone_number, chat_id):
    """
    Получает рабочий прокси из базы данных.
    Если прокси доступен, обновляет его статус и связывает с пользователем.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('select proxy_name, proxy_id from proxy where is_busy is false and is_healthy is true limit 1')
    proxy_data = cur.fetchone()
    if proxy_data:
        proxy_name, proxy_id = proxy_data
        if check_proxy(proxy_name, proxy_id):
            cur.execute(f'update proxy set is_busy = true where proxy_id = {proxy_id}')
            update_proxy_name_st = f'''
            update auth_user set proxy_name = '{proxy_name}' 
            where phone_number = '{phone_number}' and chat_id = CAST({chat_id} AS VARCHAR(50))
            '''
            cur.execute(update_proxy_name_st)
            update_proxy_id_st = f'''
            update auth_user set proxy_id = {proxy_id} 
            where phone_number = '{phone_number}' and chat_id = CAST({chat_id} AS VARCHAR(50))
            '''
            cur.execute(update_proxy_id_st)
            conn.commit()
            conn.close()
            return proxy_name
        time.sleep(7)
        return get_valid_proxy(phone_number, chat_id)
    else:
        conn.close()
        return


def write_ch(statement, data):
    """
    Записывает данные в базу данных ClickHouse.
    """
    ch_client = Client(host=CH_HOST, password=PG_DB.get('PASSWORD'), user='default')
    ch_client.execute(statement, data)


def execute_ch(statement):
    """
    Выполняет запрос к базе данных ClickHouse и возвращает результат.
    """
    ch_client = Client(host=CH_HOST, password=PG_DB.get('PASSWORD'), user='default')
    return ch_client.execute(statement)


#
# cur.execute('delete from proxy')
# proxies_db = cur.fetchall()
#
# def validate_proxy_name(proxy_name):
#     start_index = proxy_name.find('@')
#     if start_index:
#         return proxy_name[start_index+1:]
#     else:
#         return proxy_name
#
# bad_proxy = []
# for raw in proxies_db:
#     proxy_name = validate_proxy_name(raw[1])
#     start_index = proxy_name.find(':')
#     port = proxy_name[start_index+1:]
#     if len(port) == 4:
#         bad_proxy.append(raw)
#
# st = '''
# insert into proxy (proxy_id, proxy_name, is_busy, is_healthy) values %s
# '''
#
# db_insert = []
#
# counter = 245
# for raw in available_proxy:
#     db_insert.append([counter, raw, False, True])
#     counter += 1
#
# conn1 = psycopg2.connect(dbname='shopogolik_project',
#                             user=PG_DB.get('USER'),
#                             password=PG_DB.get('PASSWORD'),
#                             host=PG_DB.get('HOST'),
#                             port=PG_DB.get('PORT'))
# execute_values(cur1, st, db_insert[92:])
# conn1.commit()


