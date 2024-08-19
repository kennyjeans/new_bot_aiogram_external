import asyncio
from datetime import datetime

import aiohttp
import requests
import time
import random
import json
from urllib import parse

from data_base.aiosqlite_func import insert_items_for_confirmation
from data_base.pg_db_func import db_new_orders
from dop_func_bot.dop_func import new_product_send_users

from settings import TG_TOKEN
from utils import get_db_connection


header = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36', }


async def parse_position_keyword(product_id, keyword, low_price, high_price):
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as client:
        for _ in range(10):
            try:
                prod_ids_2d = await asyncio.gather(*[download_prod_id_by_keyword(page, product_id, keyword, client, low_price, high_price) for page in range(1, 101)])
                return prod_ids_2d
            except Exception as e:
                print("Eror func parse_position_keyword", e)
                await asyncio.sleep(random.random())
                continue

    return []


async def download_prod_id_by_keyword(page, product_id, keyword, client, low_price, high_price):
    url = (f"https://search.wb.ru/exactmatch/ru/common/v5/search?ab_testing=false&appType=1&curr=rub&dest=-1257786&page={page}&"
           + parse.urlencode({"query": f"{keyword}"}) + f"&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false&priceU={low_price*100};{high_price*100}")
    for _ in range(1):
        try:
            async with client.get(url, headers=header) as response:
                if response.status == 200:
                    try:
                        resp = await response.text()
                        #print(resp)
                        resp = json.loads(resp)
                        #print(resp)
                        # Проверка наличия товара на странице
                        for ind, article in enumerate(resp['data']['products']):
                            if article['id'] == int(product_id):
                                print([keyword, product_id, page, ind + 1])
                                return [keyword, product_id, page, ind + 1]
                        return []
                    except Exception as e:
                        print(e)
                        return []
        except:
            await asyncio.sleep(random.random())
    return []


def check_products_positions(product_id, keyword, low_price, high_price):
    res = asyncio.run(parse_position_keyword(product_id, keyword, low_price, high_price))
    for raw in res:
        if raw:
            return {'kw': raw[0], 'product_id': raw[1], 'page': raw[2], 'position': raw[3]}
    return {}


def tg_order_managing():

    conn = get_db_connection()
    cur = conn.cursor()
    while True:
        try:
            new_orders = db_new_orders()

            for new_order in new_orders:
                order_id, chat_id, image_link, product_id, short_description = new_order
                if not order_id or not chat_id or not product_id or not short_description:
                    continue
                print(new_order)
                short_description = short_description.split(',')
                keywords = []
                for kw in short_description:
                    kw = kw.lower()
                    kw = kw.lstrip()
                    kw = kw.rstrip()
                    keywords.append(kw)

                wb_price_url = f'https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={product_id}'
                print(wb_price_url)
                resp_price = requests.get(wb_price_url).json()
                try:
                    product_data = resp_price.get('data').get('products')[0]
                    product_price = resp_price.get('data').get('products')[0].get('sizes')[0].get('price').get('total')
                    brand_id = product_data.get('brandId')
                    product_price = int(product_price / 100)
                except Exception as e:
                    print(e)
                    continue
                product_price_low = product_price - round(product_price * 0.10)
                product_price_high = product_price + round(product_price * 0.10)
                is_send = False
                for kw in keywords:
                    products_pages = check_products_positions(product_id, kw, product_price_low, product_price_high)
                    print(products_pages)
                    page = products_pages.get('page')
                    position = products_pages.get('position')
                    if not page or not position:
                        continue
                    wb_search_url = (f'https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&'
                                     + parse.urlencode(
                                {"search": f"{kw}"}) + f'&fbrand={brand_id}' + f'&priceU={product_price_low * 100};'
                                                                               f'{product_price_high * 100}')
                    link_product_id = str(product_id)
                    link_product_id = link_product_id[:2] + '***' + link_product_id[5:]
                    date_time = time.time()
                    asyncio.run(insert_items_for_confirmation(user_id=int(chat_id),
                                                              photo=str(image_link),
                                                              order_id=int(order_id),
                                                              article=str(link_product_id),
                                                              page=int(page),
                                                              position=int(position),
                                                              wb_search_url=wb_search_url,
                                                              kw=str(kw),
                                                              date_time=date_time,
                                                              status=1))
                    asyncio.run(new_product_send_users(user_id=int(chat_id)))

                    is_send = True
                    cur.execute(f'update wp_orders set is_link_send = true where id = {order_id}')
                    conn.commit()
                    break
                if not is_send:
                    cur.execute(f'update wp_orders set is_link_send = false where id = {order_id}')
                    conn.commit()
            time.sleep(15)
        except Exception as e:
            print(e)
            time.sleep(60)


if __name__ == "__main__":
    tg_order_managing()

