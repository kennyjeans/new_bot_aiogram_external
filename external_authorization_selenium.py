import multiprocessing
import time
import asyncio
#import telebot
import random
import datetime
import json
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from data_base.pg_db_func import clear_db_auth_user
#from urllib.request import urlopen

from settings import TG_TOKEN, ENVIRONMENT, WP_CONSUMER_KEY, WP_CONSUMER_SECRET
from utils import get_db_connection, check_proxy, get_valid_proxy
from external_wb_parser import parse_links, parse_orders, parse_receipts
from settings import proxy_auth

from dop_func_bot.dop_func import (bad_registration, captcha_registration, long_captcha_input, sms_registration,
                                   resend_sms_registration, good_auth, new_sms_registration, long_auth)

from data_base.aiosqlite_func import select_cp_sms, update_sms_quan, state_clear_auth, delete_sms_cp

TG_URL = 'https://api.telegram.org/bot'
WB_AUTH_URL = 'https://www.wildberries.ru/security/login?returnUrl=https%3A%2F%2Fwww.wildberries.ru%2F'
WB_ORDERS_URL = 'https://www.wildberries.ru/lk/myorders/archive'


DRIVER_STATE = {
    'initial': 1,
    'sms': 2,
    'captcha': 3,
    'authorized': 4,
    'phone_insert': 5,
    'resend_code': 6
}

ELEMENTS_STATE = {
    '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[1]/div/div[2]/input': 5,
    "/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[3]/div/img": 3,
    '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/button': 6,
    #'/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[4]/div/input[1]': 2
    '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[4]/div/input[2]': 2
}

ELEMENTS_STATE_LIST = [
    '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[1]/div/div[2]/input',
    "/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[3]/div/img",
    '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/button',
    #'/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[4]/div/input[1]',
    '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[4]/div/input[2]'

]


#bot = telebot.TeleBot(TG_TOKEN)


def create_selenium_processes():
    """
        Создает процессы Selenium в зависимости от окружения.
    """
    process_lst = []
    if ENVIRONMENT.value == 'LOCAL':
        processes_quantity = 2
    elif ENVIRONMENT.value == 'PROD' or ENVIRONMENT.value == 'SHOPOGOLIK':
        processes_quantity = 12
    else:
        return
    for process_id in range(1, processes_quantity, 1):
        p = multiprocessing.Process(target=start_selenium_process, args=(process_id,))
        process_lst.append(p)
        print(process_lst)
        p.start()
    for process__ in process_lst:
        process__.join()


def send_tg_photo(chat_id, captcha_iteration):
    """
    Отправляет фото капчи пользователю в Telegram.
    chat_id: int
    photo_url: -
    caprcha_interation: int
    """
    asyncio.run(captcha_registration(user_id=chat_id))



#def send_tg_message(chat_id, message_text):
#    """
#        Отправляет сообщение пользователю в Telegram.
#    """
#    bot.send_message(chat_id, message_text)

def get_captcha_from_db(chat_id, phone_number, captcha_iteration):
    """
    Получает капчу из базы данных.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    for _ in range(1, 20):
        get_captcha_st = f'''
        SELECT captcha FROM auth_user 
        WHERE chat_id = CAST({chat_id} AS VARCHAR(50))  AND 
        phone_number = CAST('{phone_number}' AS VARCHAR(50))
        AND captcha_iteration = {captcha_iteration}
        '''
        cur.execute(get_captcha_st)
        captcha_result = cur.fetchone()
        if captcha_result:
            if captcha_result[0]:
                conn.close()
                return captcha_result[0]
        time.sleep(10)
    conn.close()


def get_db_sms_code(chat_id, code_iteration, phone_number):
    """
        Получает SMS-код из базы данных.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    for _ in range(1, 20):
        get_sms_st = f'''
        select sms_code from auth_user 
        where chat_id = CAST({chat_id} AS VARCHAR(50)) and code_iteration = {code_iteration} and phone_number = CAST('{phone_number}' AS VARCHAR(50))
        '''
        cur.execute(get_sms_st)
        code_result = cur.fetchone()
        if code_result:
            if code_result[0]:
                conn.close()
                return code_result[0]
        time.sleep(10)
    conn.close()


def validate_proxy_name(proxy_name):
    """
    Валидирует имя прокси.
    """
    start_index = proxy_name.find('@')
    if start_index:
        return 'http://' + proxy_name[start_index+1:]
    else:
        return proxy_name


def start_selenium_process(process_id):
    """
    Запускает процесс Selenium для авторизации.
    """
    time.sleep(random.choice(range(3, 20)))
    print(f'запущен процесс {process_id}')
    conn = get_db_connection()
    cur = conn.cursor()
    while True:
        statement = f'''
        select chat_id, phone_number, proxy_name, proxy_id, user_agent from auth_user where selenium_id = {process_id}
        '''
        cur.execute(statement)
        chat_data = cur.fetchone()
        #print(chat_data, '!!!!!!!!!!!!')
        if chat_data:
            chat_id, phone_number, proxy_name, proxy_id, user_agent = chat_data
            try:
                result = make_authorization(process_id, phone_number, chat_id, proxy_name, proxy_id, user_agent)
                print(f'работа по {phone_number} завершена')
                if result == 500:
                    asyncio.run(long_captcha_input(chat_id))
                    asyncio.run(state_clear_auth(int(chat_id)))
                    asyncio.run(delete_sms_cp(int(chat_id)))
                    clear_db_auth_user(str(chat_id))
            except Exception as e:
                print(e, " Код там там где я и думаю ")
                asyncio.run(bad_registration(int(chat_id), errors=e))
                asyncio.run(state_clear_auth(int(chat_id)))
                asyncio.run(delete_sms_cp(int(chat_id)))
                clear_db_auth_user(str(chat_id))

                print(f'Some error in selenium process {process_id}')
            cur.execute(f'UPDATE selenium_process SET is_busy = false where process_id = {process_id}')
            conn.commit()
            update_selenium_id_st = f'''
            update auth_user set selenium_id = 0 
            where selenium_id = {process_id} and chat_id = '{chat_id}' and phone_number = '{phone_number}'
            '''
            cur.execute(update_selenium_id_st)
            conn.commit()
            #message = f'''
            #Работа по /wb {phone_number} завершена. Если вы не получили сообщение "Авторизация успешна!", \
            #попробуйте заново
            #    '''
            #send_tg_message(chat_id, message)
        time.sleep(5)


class DriverManager:
    def __init__(self, process_id, phone_number, chat_id, proxy_name, proxy_id, user_agent):
        self.process_id = process_id
        print('self.process_id', self.process_id)
        self.phone_number = phone_number
        print('self.phone_number', self.phone_number)
        self.chat_id = chat_id
        print('self.chat_id', self.chat_id)
        if check_proxy(proxy_name, proxy_id):
            self.proxy_name = proxy_name
            print('self.proxy_name', self.proxy_name)
        else:
            new_proxy_name = get_valid_proxy(phone_number, chat_id)
            if new_proxy_name:
                self.proxy_name = new_proxy_name
                print('self.proxy_name', self.proxy_name)
            else:
                self.state = 100
                print('self.state', self.state)
                return
        self.options = webdriver.ChromeOptions()
        print('self.options', self.options)
        self.state = DRIVER_STATE.get('initial')
        print('self.state', self.state)
        self.initial_time = datetime.datetime.now()
        print('self.initial_time', self.initial_time)
        self.captcha_iteration = 0
        print('self.captcha_iteration', self.captcha_iteration)
        self.code_iteration = 0
        print('self.code_iteration', self.code_iteration)
        self.user_agent = user_agent
        print('self.user_agent', self.user_agent)
        self.conn = get_db_connection()
        print('self.conn', self.conn)
        self.cur = self.conn.cursor()
        print('self.cur', self.cur)

        if ENVIRONMENT.value == 'PROD' or ENVIRONMENT.value == 'SHOPOGOLIK':

            path = f'C:/Users/Kenny/Desktop/new_bot_aiogram_external/{self.phone_number}'
            name_profile = 'Default'
            #print(proxy_auth(self.phone_number, self.proxy_name, proxy_id))
            #передаем плагин для авторизапции proxy
            self.options.add_extension(proxy_auth(self.phone_number, self.proxy_name, proxy_id))
            time.sleep(3)
            self.options.add_argument(f'--user-data-dir={path}') #директория с профилями
            self.options.add_argument(f'--profile-directory={name_profile}') #выбор профиля
            self.options.add_argument('--allow-profiles-outside-user-dir') #-
            self.options.add_argument('--enable-profile-shortcut-manager')
            self.options.add_argument('--headless=new') #скрывает гол.интерфейс
            self.options.add_argument('--no-sandbox') #песочница
            self.options.add_argument('--disable-gpu') #скрывае gpu
            self.options.add_argument(f'user-agent={user_agent}')
            time.sleep(2)

            #Local в данном боте уже не актуален
        elif ENVIRONMENT.value == 'LOCAL':
            self.options.add_argument("--no-sandbox")
            self.options.add_argument(f'--user-data-dir={phone_number}')

        else:
            print('Bad ENVIRONMENT in .env')
            return
        self.driver = webdriver.Chrome(options=self.options)

    def check_state(self):
        """
        Проверяет текущее состояние страницы.
        """
        print('check_state')
        for pattern in ELEMENTS_STATE_LIST:
            search_query = (By.XPATH, pattern)
            wait = WebDriverWait(self.driver, 1)
            try:
                element = wait.until(EC.visibility_of_all_elements_located(search_query))[0]
                if element:
                    print(pattern, ELEMENTS_STATE.get(pattern))
                    self.state = ELEMENTS_STATE.get(pattern)
                    return
                else:
                    continue
            except (TimeoutException, IndexError) as e:
                print(e)
                continue

        is_authorized = self.check_authtorized()
        if is_authorized:
            self.state = DRIVER_STATE.get('authorized')
            return
        time.sleep(5)
        self.check_state()

    def check_authtorized(self):
        """
        Проверяет, авторизован ли пользователь.
        """
        print('check_authorized')
        self.make_request(WB_ORDERS_URL)
        search_query = (By.XPATH, '/html/body/div[1]/main/div[1]/div/div[2]/div/ul[2]/li[2]/a')
        wait = WebDriverWait(self.driver, 3)
        element = wait.until(EC.visibility_of_all_elements_located(search_query))[0]
        if element:
            print(True)
            return True
        else:
            print(False)
            self.make_request(WB_AUTH_URL)
            return False

    def make_request(self, url):
        """
        Делает запрос к URL.
        """
        self.driver.get(url)
        time.sleep(7)

    def initial_behavior(self):
        """
        Начальное поведение драйвера.
        """
        print(self.code_iteration, self.captcha_iteration, self.process_id, self.chat_id, type(self.phone_number), '!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('initial_behavior')
        statement = f'''UPDATE auth_user
        SET code_iteration = {self.code_iteration},
        captcha_iteration = {self.captcha_iteration},
        sms_code = null,
        captcha = null
        WHERE selenium_id = {self.process_id}
        AND chat_id = CAST({self.chat_id} AS VARCHAR(50))
        AND phone_number = CAST('{self.phone_number}' AS VARCHAR(50))
        '''
        self.cur.execute(statement)
        self.conn.commit()
        self.make_request(WB_AUTH_URL)
        time.sleep(6)
        self.check_state()

    def phone_insert_behavior(self):
        """
        Поведение при вводе номера телефона.
        """
        print('phone_insert_behavior')
        phone_input = self.driver.find_element(
            By.XPATH,
            '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[1]/div/div[2]/input')
        phone_input.clear()
        phone_input.send_keys(self.phone_number)
        time.sleep(5)
        self.driver.find_element(By.ID, "requestCode").click()
        time.sleep(5)
        self.check_state()

    def sms_insert_behavior(self):
        """
        Поведение при вводе SMS-кода.
        """
        if self.code_iteration == 0:
            self.code_iteration += 1
        print('sms_insert_behavior')
        sms_code_field = self.driver.find_element(
            By.XPATH,
            '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[4]/div/input[2]')
        if self.code_iteration == 1:
            asyncio.run(sms_registration(user_id=int(self.chat_id)))
        elif self.code_iteration >= 2:
            asyncio.run(new_sms_registration(user_id=int(self.chat_id)))

        time.sleep(5)
        print("sms_insert_behavior", self.code_iteration)
        sms_code = get_db_sms_code(self.chat_id, self.code_iteration, self.phone_number)
        if sms_code:
            sms_code_field.clear()
            time.sleep(4)
            sms_code_field.send_keys(sms_code)

            self.code_iteration += 1
            time.sleep(10)
        time.sleep(5)
        self.check_state()

    def resend_code(self):
        """
        Повторная отправка SMS-кода.
        """
        print('resend_code')
        self.driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/button').click()
        asyncio.run(resend_sms_registration(int(self.chat_id)))
        time.sleep(10)
        self.check_state()

    def captcha_behavior(self):
        """
        Поведение при вводе капчи.
        """
        if self.captcha_iteration == 0:
            self.captcha_iteration += 1
        print('captcha_behavior')
        captcha = self.driver.find_element(By.XPATH,
                                           "/html/body/div[1]/main/div[2]/div/div[2]/div/div/form/div/div[3]/div/img")
        #captcha_src = captcha.get_attribute("src")
        captcha.screenshot(f"captchas/{self.chat_id}.png")
        send_tg_photo(self.chat_id, self.captcha_iteration)
        time.sleep(5)
        captcha_result = get_captcha_from_db(self.chat_id, self.phone_number, self.captcha_iteration)
        print("captcha_behavior", self.captcha_iteration)
        print(captcha_result)
        if not captcha_result:
            self.state = 500
        else:
            captcha_input = self.driver.find_element(By.ID, "smsCaptchaCode")
            captcha_input.clear()
            captcha_input.send_keys(captcha_result)
            self.captcha_iteration += 1
            time.sleep(5)
            self.check_state()

    def authorized_behavior(self):
        """
        Поведение при успешной авторизации.
        """
        print('authorized_behavior')
        asyncio.run(good_auth(int(self.chat_id)))
        auth_token = 'Bearer ' + json.loads(
            self.driver.execute_script('return localStorage.getItem("wbx__tokenData");')
        ).get('token')
        cookies_list = self.driver.get_cookies()
        cookies_str = ''
        for item in cookies_list:
            cookies_str += item.get('name') + '=' + item.get('value') + '; '
        cookies_str = cookies_str[:-2]
        update_verified_st = f'''
        update auth_user set is_verified = true, cookies = '{cookies_str}', auth_token = '{auth_token}'
        where chat_id = CAST({self.chat_id} AS VARCHAR(50))  and phone_number = CAST('{self.phone_number}' AS VARCHAR(50))
        '''

        self.cur.execute(update_verified_st)
        self.conn.commit()
        self.cur.execute(f"select id, customer_id from wp_orders where product_id = 542 and customer_id = (select wp_id from auth_user where phone_number = CAST('{self.phone_number}' AS VARCHAR(50)))")
        subscribe_info = self.cur.fetchone()
        self.cur.execute(f"select wp_id from auth_user where phone_number = CAST('{self.phone_number}' AS VARCHAR(50))")
        customer_id = self.cur.fetchone()
        self.cur.execute(f"SELECT wp_email FROM auth_user WHERE phone_number = CAST('{self.phone_number}' AS VARCHAR(50))")
        email_req = self.cur.fetchone()

        print(customer_id)

        if subscribe_info and isinstance(subscribe_info[0], int):
            try:
                url = f'https://mp-keshbek.ru/wp-json/wc/v2/orders/{subscribe_info[0]}?consumer_key={WP_CONSUMER_KEY}&consumer_secret={WP_CONSUMER_SECRET}'
                requests.post(url, data={"status": "completed"})
                print(f'Отработало на {url}')
            except Exception as e:
                print("Объеб 1 ", e)
        else:
            try:
                #Приобретаем product_id 542, status: completed
                print(email_req[0])
                url = f'https://mp-keshbek.ru/wp-json/wc/v2/orders?consumer_key={WP_CONSUMER_KEY}&consumer_secret={WP_CONSUMER_SECRET}'#'https://mp-keshbek.ru/api/createOrder.php'

                create_order_data = {"line_items": [{"product_id": 542, "quantity": 1}],
                                     "status": "completed",
                                     "customer_id": customer_id[0],
                                     "payment_method": "cod"}

                data = requests.post(url, json=create_order_data)
                print(url)
                print(data)

                ###########################################################
                #Меняем роль на "avt_kup"

                #api_url = "https://mp-keshbek.ru/api/changeRole.php"
                #api_data = {
                #    "token": "bk7ZubNZ1XuJXiXzDqyjgZPbopI8wK",
                #    "email": email_req[0],
                #    "role": "avt_kup"
                #}
                #api_data = requests.post(api_url, data=api_data)
                #print(api_url)
                #print(api_data)

            except Exception as e:
                print(e)
        self.cur.execute(
            f"select proxy_id from auth_user where chat_id = CAST({self.chat_id} AS VARCHAR(50)) and phone_number = CAST('{self.phone_number}' AS VARCHAR(50))"
        )
        proxy_id = self.cur.fetchone()
        if proxy_id:
            if proxy_id[0]:
                auth_data_dict = {self.phone_number: {
                    'cookies': cookies_str,
                    'auth_token': auth_token,
                    'user_agent': self.user_agent,
                    'proxy_name': self.proxy_name,
                    'chat_id': self.chat_id,
                    'proxy_id': proxy_id[0]
                }}
                parse_orders(auth_data_dict)
                parse_links(auth_data_dict)
                parse_receipts(one_user_phone=self.phone_number)
        time.sleep(5)
        self.check_state()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        В случае завершения работы или ошибок - завершит работу с БД и Driver-ом
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.conn.close()
        self.driver.quit()


def make_authorization(process_id, phone_number, chat_id, proxy_name, proxy_id, user_agent):
    """
    Выполняет процесс авторизации с использованием Selenium. Ищет по БД чем бы заняться
    """
    driver_manager = DriverManager(process_id, phone_number, chat_id, proxy_name, proxy_id, user_agent)
        #print(process_id, type(process_id), phone_number, type(phone_number), chat_id, type(chat_id), proxy_name, (type(proxy_name)), proxy_id, type(proxy_id), user_agent, type(user_agent))
    try:
        driver_manager.initial_behavior()
        while driver_manager.state != DRIVER_STATE.get('authorized') and \
                (datetime.datetime.now() - driver_manager.initial_time).seconds < (60*10):
            driver_manager.check_state()
            if driver_manager.state == DRIVER_STATE.get('initial'):
                driver_manager.initial_behavior()
            elif driver_manager.state == DRIVER_STATE.get('sms'):
                driver_manager.sms_insert_behavior()
            elif driver_manager.state == DRIVER_STATE.get('captcha'):
                driver_manager.captcha_behavior()
            elif driver_manager.state == DRIVER_STATE.get('phone_insert'):
                driver_manager.phone_insert_behavior()
            elif driver_manager.state == DRIVER_STATE.get('resend_code'):
                driver_manager.resend_code()
            else:
                print('Некорректное состояние драйвера', driver_manager.state)
                if driver_manager.state == 500:
                    try:
                        driver_manager.driver.quit()
                        driver_manager.conn.close()
                    except:
                        pass
                    return driver_manager.state
                else:
                    return
        if driver_manager.state == DRIVER_STATE.get('authorized'):
            driver_manager.authorized_behavior()
            driver_manager.driver.quit()
            driver_manager.conn.close()
        else:
            raise "Неизвестная ошибка"
    except Exception as e:
        driver_manager.driver.quit()
        driver_manager.conn.close()
        raise e


if __name__ == '__main__':
    create_selenium_processes()
