import psycopg2

from utils import get_db_connection


def delete_data_cancel_reg(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE auth_user SET phone_number = %(phone_number)s, chat_id = %(chat_id)s
     WHERE chat_id = %(user_id)s""", {'phone_number': None,
                                      'chat_id': None,
                                      'user_id': f"{user_id}"})
    conn.commit()
    conn.close()


def write_captcha(chat_id, captcha, captcha_iteration):
    """
    Записывает капчу в базу данных.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    statement = f""" 
        update auth_user set captcha = %(captcha)s, captcha_iteration = %(captcha_iteration)s
        where chat_id = CAST(%(chat_id)s AS VARCHAR(50))
                """
    try:
        cur.execute(statement, {'captcha': captcha,
                                'captcha_iteration': captcha_iteration,
                                'chat_id': chat_id,
                                })
    except psycopg2.Error as e:
        print(e)

    conn.commit()
    conn.close()


def write_sms_code(chat_id, sms_code, code_iteration):
    """
    Записывает SMS-код в базу данных.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    statement = f"""
        UPDATE auth_user SET sms_code = %(sms_code)s, code_iteration = %(code_iteration)s
        WHERE chat_id = CAST(%(chat_id)s AS VARCHAR(50))
    """
    try:
        cur.execute(statement, {'sms_code': sms_code,
                                'code_iteration': code_iteration,
                                'chat_id': chat_id
                                })
    except psycopg2.Error as e:
        print(e)
    conn.commit()
    conn.close()


def clear_db_auth_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT selenium_id FROM auth_user WHERE chat_id = CAST(%(user_id)s AS VARCHAR(50))""",
                {"user_id": user_id})
    selenium_id = cur.fetchone()
    cur.execute("""UPDATE selenium_process SET is_busy = %(is_busy)s WHERE process_id = %(selenium_id)s""",
                {"selenium_id": selenium_id[0],
                 "is_busy": False})
    statement = f"""
            UPDATE auth_user SET
            phone_number = %(sms_code)s,
            chat_id = %(code_iteration)s,
            captcha = %(captcha)s,
            captcha_iteration =  %(captcha_iteration)s,
            proxy_name = %(proxy_name)s,
            proxy_id = %(proxy_id)s,
            is_verified = %(is_verified)s,
            sms_code = %(sms_code)s,
            selenium_id = %(selenium_id)s,
            code_iteration = %(code_iteration)s,
            last_parsing_date = %(last_parsing_date)s,
            user_agent = %(user_agent)s,
            cookies = %(cookies)s,
            auth_token = %(auth_token)s
            WHERE chat_id = CAST(%(user_id)s AS VARCHAR(50))
        """
    try:
        cur.execute(statement, {'phone_number': None,
                                'chat_id': None,
                                'captcha': None,
                                "captcha_iteration": None,
                                "proxy_name": None,
                                "proxy_id": None,
                                "is_verified": None,
                                "sms_code": None,
                                "selenium_id": None,
                                "code_iteration": None,
                                "last_parsing_date": None,
                                "user_agent": None,
                                "cookies": None,
                                "auth_token": None,
                                "user_id": user_id
                                })
    except psycopg2.Error as e:
        print(e)
    conn.commit()
    conn.close()


def db_new_orders():
    """
    Возвращает: таблицу с новыми заказами (содержание)
    order_id,
    chat_id,
    link,
    product_id,
    keywords
    """
    conn = get_db_connection()
    cur = conn.cursor()
    new_orders_statement = '''
    select base_data.order_id, t2.chat_id, base_data.link, base_data.product_id, base_data.keywords
    from 
    (select 
    t1.id as order_id, 
    t1.customer_id as customer_id,
    wp_products.product_id as product_id, 
    wp_products.media_link as link,
    wp_products.short_description as keywords
    from (select * from wp_orders where is_link_send is not True and product_id not in (542, 357, 329)) as t1
    left join 
    wp_products
    on t1.product_id = wp_products.id) as base_data
    left join
    (select * from auth_user where is_verified is true) as t2
    on base_data.customer_id = t2.wp_id
    '''
    cur.execute(new_orders_statement)
    new_orders_data = cur.fetchall()
    conn.close()
    return new_orders_data


def select_accept_order(order_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT 
                    wp_products.product_id, 
                    wp_orders.id AS order_id, 
                    wp_orders.is_verified, 
                    auth_user.chat_id, 
                    auth_user.phone_number
                    FROM 
                    wp_orders
                    LEFT JOIN 
                    auth_user 
                    ON 
                    wp_orders.customer_id = auth_user.wp_id
                    LEFT JOIN 
                    wp_products 
                    ON 
                    wp_orders.product_id = wp_products.id
                    WHERE 
                    wp_orders.id = %(wp_order_id)s
                    AND wp_orders.is_confirmed IS TRUE
                    AND auth_user.chat_id = %(chat_id)s
                    AND auth_user.is_verified IS TRUE""", {"wp_order_id": order_id,
                                                           "chat_id": f'{user_id}'})
    data = cur.fetchall()
    conn.close()
    return data


def delete_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE wp_orders SET status = %(status)s WHERE id = %(order_id)s""", {"order_id": order_id,
                                                                                         "status": "cancelled"})
    conn.commit()
    conn.close()
    return


def select_accept_orders(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT 
    wp_products.product_id, 
    t2.order_id, 
    t2.chat_id, 
    t2.is_verified, 
    t2.phone_number
    FROM
        (
            SELECT 
                auth_user.phone_number AS phone_number, 
                auth_user.chat_id AS chat_id, 
                t1.is_confirmed AS is_verified, 
                t1.order_id, 
                t1.wp_product_id
            FROM
                (
                    SELECT 
                        wp_orders.id AS order_id, 
                        wp_orders.customer_id, 
                        wp_orders.product_id AS wp_product_id, 
                        wp_orders.is_confirmed 
                    FROM 
                        wp_orders 
                    WHERE 
                        wp_orders.is_confirmed = true
                ) AS t1
            LEFT JOIN 
                auth_user 
            ON 
                t1.customer_id = auth_user.wp_id
        ) AS t2
    LEFT JOIN 
        wp_products 
    ON 
        t2.wp_product_id = wp_products.id
    WHERE 
        t2.is_verified IS TRUE
        AND t2.chat_id = %(chat_id)s""", {"chat_id": f"{chat_id}"})

    data = cur.fetchall()
    return data





