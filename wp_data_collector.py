import psycopg2
import requests
import datetime
import time
import logging
from psycopg2.extras import execute_values
from dateutil.relativedelta import relativedelta

from settings import WP_CONSUMER_KEY, WP_CONSUMER_SECRET
from utils import get_db_connection

    # URL для получения списка клиентов из WooCommerce
list_customers_url = f'https://mp-keshbek.ru/wp-json/wc/v2/customers?consumer_key={WP_CONSUMER_KEY}&consumer_secret={WP_CONSUMER_SECRET}&per_page=100&page=1&orderby=registered_date&order=desc&role=all'
    # URL для получения списка заказов из WooCommerce
list_orders_url = f'https://mp-keshbek.ru/wp-json/wc/v2/orders?consumer_key={WP_CONSUMER_KEY}&consumer_secret={WP_CONSUMER_SECRET}&per_page=100&page=1&orderby=date&order=desc'
    # URL для получения списка продуктов из WooCommerce
list_products_url = f'https://mp-keshbek.ru/wp-json/wc/v2/products?consumer_key={WP_CONSUMER_KEY}&consumer_secret={WP_CONSUMER_SECRET}'


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    #  Функция для сбора данных о заказах, клиентах и продуктах с сайта, использующего WooCommerce.
def wp_data_collect():
    conn = get_db_connection()
    cur = conn.cursor()
    while True:
        try:
    # Получение данных о последних заказах
            last_orders = requests.get(list_orders_url)
            last_orders = last_orders.json()
            db_orders = []
            for raw in last_orders:
                try:
                    my_date = datetime.datetime.strptime(raw.get('date_created'), '%Y-%m-%dT%H:%M:%S').date()
                except:
                    my_date = datetime.datetime.strptime(raw.get('date_created'), '%Y-%m-%dT%H:%M:%S.%f').date()
                product_info = raw.get('line_items')
                product_id = 0
                if product_info:
                    product_id = product_info[0].get('product_id')
                expire_date = None
                if product_id == 329:
                    expire_date = datetime.datetime.now().date() + relativedelta(months=1)
                db_orders.append([
                    raw.get('id'),
                    raw.get('customer_id'),
                    raw.get('status'),
                    raw.get('total'),
                    my_date,
                    expire_date,
                    product_id
                ])
    # Получение данных о последних клиентах
            last_users = requests.get(list_customers_url)
            last_users = last_users.json()
            db_users = []
            for raw in last_users:
                try:
                    my_date = datetime.datetime.strptime(raw.get('date_created'), '%Y-%m-%dT%H:%M:%S').date()
                except:
                    my_date = datetime.datetime.strptime(raw.get('date_created'), '%Y-%m-%dT%H:%M:%S.%f').date()
                db_users.append([
                    raw.get('email'),
                    raw.get('id'),
                    my_date,
                    raw.get('first_name') + ' ' + raw.get('last_name'),
                    raw.get('role')
                ])
    # Получение данных о продуктах с постраничным обходом

            products_page = 1
            while True:
                products_add_url = f'&page={products_page}&per_page=100&orderby=id'
                products_url = list_products_url + products_add_url
                products = requests.get(products_url).json()
                db_products = []
                for raw in products:
                    try:
                        my_date = datetime.datetime.strptime(raw.get('date_created'), '%Y-%m-%dT%H:%M:%S').date()
                    except:
                        my_date = datetime.datetime.strptime(raw.get('date_created'), '%Y-%m-%dT%H:%M:%S.%f').date()
                    if raw.get('short_description'):
                        short_description = raw.get('short_description').replace('<p>', '')
                        short_description = short_description.replace('</p>', '')
                    else:
                        short_description = ''
                    try:
                        if raw.get('images'):
                            image_link = raw.get('images')[0].get('src')
                        else:
                            image_link = ''
                    except:
                        image_link = ''
                    db_products.append([
                        raw.get('id'),
                        raw.get('name'),
                        my_date,
                        raw.get('price') if raw.get('price') else 0,
                        raw.get('stock_quantity') if raw.get('stock_quantity') and isinstance(raw.get('stock_quantity'), int) else 0,
                        short_description,
                        image_link,
                        raw.get('sku') if raw.get('sku') else 0,
                        ', '.join(attr.get('name', '') for attr in raw.get('attributes', []))
                    ])
                if len(products) < 100:
                    break
                else:
                    products_page += 1
    # Обновление данных в базе данных
            update_users_order_st = '''
            INSERT INTO wp_orders (
            id, 
            customer_id,
            status,
            total_sum,
            created_date,
            expire_date,
            product_id
            ) VALUES %s ON CONFLICT (id) DO Update set
            customer_id = EXCLUDED.customer_id,
            status = EXCLUDED.status,
            created_date = EXCLUDED.created_date,
            expire_date = EXCLUDED.expire_date;
            '''
            update_products_st = '''
            INSERT INTO wp_products (
            id, 
            name,
            created_date,
            price,
            stock_quantity,
            short_description,
            media_link,
            product_id,
            brand
            ) VALUES %s ON CONFLICT (id) DO Update set 
            created_date = EXCLUDED.created_date,
            name = EXCLUDED.name,
            price = EXCLUDED.price, 
            stock_quantity = EXCLUDED.stock_quantity, 
            short_description = EXCLUDED.short_description,
            media_link = EXCLUDED.media_link,
            product_id = EXCLUDED.product_id,
            brand = EXCLUDED.brand;
            '''
            update_users_st = '''
            INSERT INTO auth_user (
            wp_email,
            wp_id,
            wp_date,
            wp_name,
            wp_role
            ) VALUES %s ON CONFLICT (wp_email) DO Update set 
            wp_id = EXCLUDED.wp_id,
            wp_date = EXCLUDED.wp_date,
            wp_name = EXCLUDED.wp_name,
            wp_role = EXCLUDED.wp_role;
            '''
            execute_values(cur, update_users_st, db_users)
            conn.commit()
            execute_values(cur, update_products_st, db_products)
            conn.commit()
            execute_values(cur, update_users_order_st, db_orders)
            conn.commit()
            logging.info("Данные таблиц обновлены.")
    # Ожидание перед следующим запросом
            time.sleep(30)
        except psycopg2.Error as e:
            logging.info(f"Данные таблиц не обновлены.{e}")
    # В случае ошибки ожидание 60 секунд перед повторным запуском
            time.sleep(60)


if __name__ == '__main__':
    wp_data_collect()
