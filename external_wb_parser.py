import random
import requests
import datetime
import telebot
import time
import asyncio
from psycopg2.extras import execute_values
from bs4 import BeautifulSoup

from dop_func_bot.dop_func import restart_auth
from utils import get_db_connection, check_proxy, get_valid_proxy
from settings import TG_TOKEN, WP_CONSUMER_KEY, WP_CONSUMER_SECRET

ORDER_WB_URL = 'https://www.wildberries.ru/webapi/lk/myorders/archive/get'
LINKS_WB_URL = 'https://www.wildberries.ru/webapi/lk/receipts/data?count=10'
DELIVERY_WB_URL = 'https://www.wildberries.ru/webapi/v2/lk/myorders/delivery/active'


bot = telebot.TeleBot(TG_TOKEN)


def start_wb_parsing():
    auth_data_dict = get_actual_auth_data()
    parse_orders(auth_data_dict, is_full_parsing=False)
    auth_data_dict = get_actual_auth_data()
    parse_links(auth_data_dict, is_full_parsing=False)
    auth_data_dict = get_actual_auth_data()
    parse_delivery_data(auth_data_dict)
    parse_receipts(with_last_date=True)


def get_actual_auth_data():
    conn = get_db_connection()
    cur = conn.cursor()
    today = datetime.datetime.now().date()
    auth_data_dict = {}
    auth_data_statement = '''
    select phone_number, cookies, auth_token, user_agent, proxy_name, chat_id, proxy_id
    from auth_user 
    where (last_parsing_date != '{today}' or last_parsing_date is null)
    and is_verified is true
    '''
    cur.execute(auth_data_statement.format(today=today.strftime('%Y-%m-%d')))
    auth_data = cur.fetchall()
    if auth_data:
        for auth_data_raw in auth_data:
            auth_data_dict[auth_data_raw[0]] = {
                'cookies': auth_data_raw[1],
                'auth_token': auth_data_raw[2],
                'user_agent': auth_data_raw[3],
                'proxy_name': auth_data_raw[4],
                'chat_id': auth_data_raw[5],
                'proxy_id': auth_data_raw[6],
            }
    conn.close()
    return auth_data_dict


def parse_links(auth_data_dict, is_full_parsing=True):
    if not auth_data_dict:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    for phone_number, phone_data in auth_data_dict.items():
        base_url = LINKS_WB_URL
        payload_data = {'count': 10}
        db_data = []
        headers = {'Authorization': phone_data.get('auth_token'),
                   'Cookie': phone_data.get('cookies'),
                   'User-Agent': phone_data.get('user_agent')}
        user_proxy = phone_data.get('proxy_name')
        counter_errors = 0
        while True:
            time.sleep(random.random())
            try:
                resp = requests.post(base_url,
                                     headers=headers,
                                     proxies={'https': user_proxy, 'http': user_proxy},
                                     data=payload_data,
                                     timeout=6.0)
            except:
                is_valid = check_proxy(phone_data.get('proxy_name'), phone_data.get('proxy_id'))
                counter_errors += 1
                if not is_valid or counter_errors > 2:
                    user_proxy = get_valid_proxy(phone_number, phone_data.get('chat_id'))
                    continue
                else:
                     pass
                print(f'bad proxy for {phone_number}')
                continue
            if resp.status_code == 401:
                print(f'bad auth for {phone_number}')
                break
            try:
                resp = resp.json()
                resp = resp.get('value').get('data')
            except requests.exceptions.JSONDecodeError:
                update_is_verified_st = f'''
                update auth_user set is_verified = false 
                where chat_id = '{phone_data.get('chat_id')}' and phone_number = '{phone_number}'
                '''
                cur.execute(update_is_verified_st)
                conn.commit()
                cur.execute(
                    f"SELECT wp_email FROM auth_user WHERE is_verified = false and phone_number = '{phone_number}'")
                email_req = cur.fetchone()
                if email_req:
                    api_url = "https://mp-keshbek.ru/api/changeRole.php"
                    api_data = {
                        "token": "bk7ZubNZ1XuJXiXzDqyjgZPbopI8wK",
                        "email": email_req[0],
                        "role": "no_activ"
                    }
                    requests.post(api_url, data=api_data)
                    print(api_url)
                    print(api_data)
                cur.execute(f"select id from wp_orders where product_id = 542 and customer_id = (select wp_id from auth_user where phone_number = CAST('{phone_number}' AS VARCHAR(50)))")
                subscribe_info = cur.fetchone()
                print(phone_number, '111')
                if subscribe_info and isinstance(subscribe_info[0], int):
                    url = f'https://mp-keshbek.ru/wp-json/wc/v2/orders/{subscribe_info[0]}?consumer_key={WP_CONSUMER_KEY}&consumer_secret={WP_CONSUMER_SECRET}'
                    requests.post(url, data={"status": "failed"})
                asyncio.run(restart_auth(int(phone_data.get('chat_id'))))
                print('Ваша сессия авторизации истекла. Пожалуйста, авторизуйтесь заново')

                break
            last_receipt = resp.get('lastReceiptId')
            for receipt in resp.get('receipts'):
                try:
                    my_date = datetime.datetime.strptime(receipt.get('operationDateTime'),
                                                         '%Y-%m-%dT%H:%M:%S.%f').date()
                except:
                    my_date = datetime.datetime.strptime(receipt.get('operationDateTime'), '%Y-%m-%dT%H:%M:%SZ').date()
                try:
                    amount = int(receipt.get('operationSum'))
                except:
                    amount = None
                db_data.append([
                    receipt.get('receiptUid'),
                    receipt.get('link'),
                    phone_number,
                    my_date,
                    amount,
                    receipt.get('operationType'),
                    receipt.get('operationTypeId')
                ])
            if len(resp.get('receipts')) < 10:
                break
            else:
                if not is_full_parsing:
                    break
                payload_data = {
                    'count': 10,
                    'lastReceiptId': last_receipt,
                    'includeUserData': False,
                }
                base_url = LINKS_WB_URL + f'&lastReceiptId={last_receipt}&includeUserData=false'

        update_users_receipt_st = '''
        INSERT INTO receipt (
        receipt_uid, 
        link,
        phone_number, 
        receipt_date,
        amount,
        operation_type,
        operation_type_id
        ) VALUES %s ON CONFLICT (link) DO UPDATE SET 
            amount = EXCLUDED.amount,
            receipt_date = EXCLUDED.receipt_date,
            receipt_uid=EXCLUDED.receipt_uid,
            operation_type = EXCLUDED.operation_type,
            operation_type_id = EXCLUDED.operation_type_id
        '''
        execute_values(cur, update_users_receipt_st, db_data)
        conn.commit()
        print(phone_number)


def parse_delivery_data(auth_data_dict):
    if not auth_data_dict:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('delete from delivery_info')
    conn.commit()

    for phone_number, phone_data in auth_data_dict.items():
        db_data = []
        headers = {'Authorization': phone_data.get('auth_token'),
                   'Cookie': phone_data.get('cookies'),
                   'User-Agent': phone_data.get('user_agent')}
        user_proxy = phone_data.get('proxy_name')
        counter_errors = 0
        time.sleep(random.random())
        try:
            resp = requests.post(DELIVERY_WB_URL,
                                 headers=headers,
                                 proxies={'https': user_proxy, 'http': user_proxy},
                                 timeout=6.0)
        except:
            is_valid = check_proxy(phone_data.get('proxy_name'), phone_data.get('proxy_id'))
            counter_errors += 1
            if not is_valid or counter_errors > 2:
                user_proxy = get_valid_proxy(phone_number, phone_data.get('chat_id'))
                continue
            print(f'bad proxy for {phone_number}')
            continue
        if resp.status_code == 401:
            print(f'bad auth for {phone_number}')
            break
        try:
            resp = resp.json()
            resp = resp.get('value').get('positions')
        except requests.exceptions.JSONDecodeError:
            update_is_verified_st = f'''
            update auth_user set is_verified = false 
            where chat_id = '{phone_data.get('chat_id')}' and phone_number = '{phone_number}'
            '''
            cur.execute(update_is_verified_st)
            conn.commit()
            # bot.send_message(phone_data.get('chat_id'),
            #                  'Ваша сессия авторизации истекла. Пожалуйста, авторизуйтесь заново')
            print(phone_number, '222')
            break
        for order in resp:
            try:
                my_date = datetime.datetime.strptime(order.get('orderDate')[:-2], '%Y-%m-%dT%H:%M:%S.%f').date()
            except:
                my_date = datetime.datetime.strptime(order.get('orderDate')[:-2], '%Y-%m-%dT%H:%M:%S').date()
            try:
                amount = int(order.get('price'))
            except:
                amount = None
            db_data.append([
                order.get('rId'),
                order.get('code1S'),
                order.get('name'),
                phone_number,
                my_date,
                amount,
                order.get('postPayment'),
                order.get('prepaid'),
                order.get('address'),
                order.get('officeId'),
                order.get('trackingStatus')
            ])

        update_users_order_st = '''
        INSERT INTO delivery_info (
        order_id,
        product_id, 
        name,
        phone_number,
        order_date,
        price,
        post_payment,
        prepaid, 
        office_address,
        office_id,
        tracking_status
        ) VALUES %s
        '''
        execute_values(cur, update_users_order_st, db_data)
        conn.commit()
        print(phone_number)
    conn.close()


def check_user_orders(auth_data_dict, product_id, wp_order_id):
    if not auth_data_dict:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    is_finded = False
    for phone_number, phone_data in auth_data_dict.items():
        cur.execute(f"delete from delivery_info where phone_number = '{phone_number}'")
        conn.commit()
        db_data = []
        headers = {'Authorization': phone_data.get('auth_token'),
                   'Cookie': phone_data.get('cookies'),
                   'User-Agent': phone_data.get('user_agent')}

        user_proxy = phone_data.get('proxy_name')
        counter_errors = 0
        time.sleep(random.random())
        try:
            resp = requests.post(DELIVERY_WB_URL,
                                 headers=headers,
                                 proxies={'https': user_proxy, 'http': user_proxy},
                                 timeout=6.0)
            #print(resp)
        except Exception as e:
            print(e)
            is_valid = check_proxy(phone_data.get('proxy_name'), phone_data.get('proxy_id'))
            counter_errors += 1
            if not is_valid or counter_errors > 2:
                user_proxy = get_valid_proxy(phone_number, phone_data.get('chat_id'))
                continue
            print(f'bad proxy for {phone_number}')
            continue
        if resp.status_code == 401:
            print(f'bad auth for {phone_number}')
            break
        try:
            resp = resp.json()
            resp = resp.get('value').get('positions')
            #print(resp, "####################################################")
        except requests.exceptions.JSONDecodeError:
            update_is_verified_st = f'''
            update auth_user set is_verified = false 
            where chat_id = '{phone_data.get('chat_id')}' and phone_number = '{phone_number}'
            '''
            cur.execute(update_is_verified_st)
            conn.commit()

            # bot.send_message(phone_data.get('chat_id'),
            #                  'Ваша сессия авторизации истекла. Пожалуйста, авторизуйтесь заново')
            print(phone_number, '333')
            break
        for order in resp:
            try:
                my_date = datetime.datetime.strptime(order.get('orderDate')[:-2], '%Y-%m-%dT%H:%M:%S.%f').date()
            except Exception as e:
                print(e)
                my_date = datetime.datetime.strptime(order.get('orderDate')[:-2], '%Y-%m-%dT%H:%M:%S').date()
            try:
                amount = int(order.get('price'))
            except Exception as e:
                print(e)
                amount = None
            if order.get('code1S') == int(product_id):
                print(0)
                is_finded = True
                cur.execute('update wp_orders set is_confirmed = true where id = %(wp_order_id)s',
                            {'wp_order_id': wp_order_id})
                conn.commit()
            db_data.append([
                order.get('rId'),
                order.get('code1S'),
                order.get('name'),
                phone_number,
                my_date,
                amount,
                order.get('postPayment'),
                order.get('prepaid'),
                order.get('address'),
                order.get('officeId'),
                order.get('trackingStatus')
            ])

        update_users_order_st = '''
        INSERT INTO delivery_info (
        order_id,
        product_id, 
        name,
        phone_number,
        order_date,
        price,
        post_payment,
        prepaid, 
        office_address,
        office_id,
        tracking_status
        ) VALUES %s
        '''
        execute_values(cur, update_users_order_st, db_data)
        conn.commit()
        print(phone_number)
    conn.close()
    return is_finded


def parse_orders(auth_data_dict, is_full_parsing=True):
    if not auth_data_dict:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    for phone_number, phone_data in auth_data_dict.items():
        db_data = []
        headers = {'Authorization': phone_data.get('auth_token'),
                   'Cookie': phone_data.get('cookies'),
                   'User-Agent': phone_data.get('user_agent')}
        user_proxy = phone_data.get('proxy_name')
        offset = 0
        limit = 150
        counter_errors = 0
        while True:
            time.sleep(random.random())
            try:
                resp = requests.post(ORDER_WB_URL,
                                     headers=headers,
                                     proxies={'https': user_proxy, 'http': user_proxy},
                                     data={'limit': limit, 'offset': offset, 'type': 'all'},
                                     timeout=6.0)
            except:
                is_valid = check_proxy(phone_data.get('proxy_name'), phone_data.get('proxy_id'))
                counter_errors += 1
                if not is_valid or counter_errors > 2:
                    user_proxy = get_valid_proxy(phone_number, phone_data.get('chat_id'))
                    continue
                print(f'bad proxy for {phone_number}')
                continue
            if resp.status_code == 401:
                print(f'bad auth for {phone_number}')
                break
            try:
                resp = resp.json()
                resp = resp.get('value').get('archive')
            except requests.exceptions.JSONDecodeError:
                update_is_verified_st = f'''
                update auth_user set is_verified = false 
                where chat_id = '{phone_data.get('chat_id')}' and phone_number = '{phone_number}'
                '''
                cur.execute(update_is_verified_st)
                conn.commit()
                cur.execute(
                    f"SELECT wp_email FROM auth_user WHERE phone_number = '{phone_number}'")
                email_req = cur.fetchone()
                if email_req:
                    api_url = "https://mp-keshbek.ru/api/changeRole.php"
                    api_data = {
                        "token": "bk7ZubNZ1XuJXiXzDqyjgZPbopI8wK",
                        "email": email_req[0],
                        "role": "no_activ"
                    }
                    requests.post(api_url, data=api_data)
                    print(api_url)
                    print(api_data)
                asyncio.run(restart_auth(int(phone_data.get('chat_id'))))
                print(phone_number, '444')
                break
            for order in resp:
                office = order.get('office')
                try:
                    my_date = datetime.datetime.strptime(order.get('orderDateString'), '%Y-%m-%dT%H:%M:%S.%fZ').date()
                except:
                    my_date = datetime.datetime.strptime(order.get('orderDateString'), '%Y-%m-%dT%H:%M:%SZ').date()
                try:
                    amount = int(order.get('price'))
                except:
                    amount = None
                db_data.append([
                    order.get('rId'),
                    order.get('code1S'),
                    order.get('name'),
                    phone_number,
                    my_date,
                    amount,
                    order.get('paymentType'),
                    order.get('status'),
                    order.get('supplierId'),
                    order.get('officeId'),
                    office.get('address') if office else None,
                ])
            if len(resp) < limit:
                break
            else:
                if not is_full_parsing:
                    break
                offset += 150
        update_users_order_st = '''
        INSERT INTO users_order (
        order_id, 
        product_id, 
        name,
        phone_number,
        order_date,
        amount,
        payment_type,
        status,
        supplier_id,
        office_id,
        office_address
        ) VALUES %s ON CONFLICT (order_id) DO update set status = EXCLUDED.status, order_date = EXCLUDED.order_date;
        '''
        execute_values(cur, update_users_order_st, db_data)
        conn.commit()
        print(phone_number, '666')

    conn.close()


def make_request(url):
    for i in range(3):
        try:
            resp = requests.get(url, timeout=5.0)
            return resp
        except:
            print(f'some_error in request {url}')
            continue

# products-supplier-inn gray ИНН продавца

def parse_receipts(with_last_date=False, one_user_phone=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if with_last_date:
        last_date = datetime.datetime.now().date() - datetime.timedelta(days=10)
    else:
        last_date = datetime.datetime(year=1970, month=1, day=1).date()
    if not one_user_phone:
        all_links_statement = '''
        select link, phone_number, receipt_uid
        from receipt 
        where receipt_date > '{last_date}' and receipt_date > '2023-09-01' 
        order by (receipt_date, link) asc
        '''
    else:
        all_links_statement = f"""
        select link, phone_number, receipt_uid
        from receipt 
        where receipt_date > '{last_date.strftime('%Y-%m-%d')}' and receipt_date > '2024-07-01' 
        and phone_number = '{one_user_phone}'
        order by (receipt_date, link) asc
        """

    update_receipt_info_st = '''
    INSERT INTO receipt_info (
    order_id, 
    link,
    receipt_uid,
    name,
    phone_number,
    quantity,
    price,
    cost,
    supplier_inn
    ) VALUES %s ON CONFLICT (order_id) DO update set quantity = EXCLUDED.quantity, price = EXCLUDED.price, name=EXCLUDED.name, supplier_inn=EXCLUDED.supplier_inn;
    '''
    cur.execute(all_links_statement.format(last_date=last_date.strftime('%Y-%m-%d')))
    links_data = cur.fetchall()
    base_tags = ['products-item products-item', 'products-item products-item first']
    result = []
    uniq_orders = set()
    counting_receipt_map = {}
    for link_data in links_data:
        resp = make_request(link_data[0])
        if not resp:
            continue
        receipt = resp.text
        soup = BeautifulSoup(receipt, 'html.parser')
        for tag in base_tags:
            elements = soup.findAll('div', class_=tag)
            for element in elements:
                text_info = element.find('div', class_='products-prop-value').text.strip().split('\n')
                supplier_inn = element.find('div', class_='products-supplier-inn gray').text.strip().split('\n')
                try:
                    name = text_info[0].lstrip()
                    name = name.rstrip()
                except:
                    print(f'error in name {link_data[0]}')

                    break
                try:
                    order_id = text_info[2].lstrip()
                    order_id = order_id.rstrip()
                    supplier_inn = element.find('div', class_='products-supplier-inn gray').text.strip()
                except:
                    print(f'error in order_id {link_data[0]}')
                    break


                quantity = float(element.find('div', class_='products-cell products-cell_count')
                                 .text.replace('\n', ''))
                cost = float(element.find('div', class_='products-cell products-cell_cost')
                             .text.replace('\n', ''))
                price = float(element.find('div', class_='products-cell products-cell_price')
                              .text.replace('\n', ''))
                if order_id not in uniq_orders:
                    uniq_orders.add(order_id)
                    counting_receipt_map[order_id] = {
                            'order_id': order_id,
                            'link': link_data[0],
                            'receipt_uid': link_data[2],
                            'name': name,
                            'phone_number': link_data[1],
                            'quantity': int(quantity),
                            'price': int(price),
                            'cost': int(cost),
                            'supplier_inn': supplier_inn
                           }
                else:
                    counting_receipt_map[order_id]['quantity'] = (counting_receipt_map.get(order_id).get('quantity') +
                                                                  int(quantity))
                    counting_receipt_map[order_id]['cost'] = counting_receipt_map.get(order_id).get('cost') + int(price)

        for k, value in counting_receipt_map.items():
            result.append([value.get('order_id'),
                           value.get('link'),
                           value.get('receipt_uid'),
                           value.get('name'),
                           value.get('phone_number'),
                           value.get('quantity'),
                           value.get('price'),
                           value.get('cost'),
                           value.get('supplier_inn')
                           ])
        print(link_data[0])
        counting_receipt_map = {}
        uniq_orders = set()
        if result:
            execute_values(cur, update_receipt_info_st, result)
            conn.commit()
        result = []


if __name__ == '__main__':
    start_wb_parsing()
