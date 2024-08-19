import time
import zipfile
from enum import Enum
from dotenv import load_dotenv
from environs import Env
import sentry_sdk
import os

# Инициализация объекта Env для чтения переменных окружения
load_dotenv()
env = Env()
env.read_env()

# Определение класса Enum для окружения(НЕ АКТУАЛЬНО)
class Environment(Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"
    SHOPOGOLIK = "SHOPOGOLIK"

# Чтение переменной окружения и создание объекта Environment(SHOPOGOLIK)
ENVIRONMENT: Environment = Environment.SHOPOGOLIK

if ENVIRONMENT.value == 'PROD' or ENVIRONMENT.value == 'LOCAL':
    TG_TOKEN = env.str('TG_TOKEN2')
elif ENVIRONMENT.value == 'SHOPOGOLIK':
    TG_TOKEN = env.str('TG_TOKEN_SHOPOGOLIK')

# Конфигурация базы данных PostgreSQL в зависимости от окружения
if ENVIRONMENT.value == 'PROD' or ENVIRONMENT.value == 'LOCAL':
    PG_DB = {
            'NAME': env.str("PG_DB_INTERNAL"),
            'USER': env.str("PG_USER"),
            'PASSWORD': env.str("PG_PASS"),
            'HOST': env.str("PG_HOST"),
            'PORT': env.str("PG_PORT"),
    }
elif ENVIRONMENT.value == 'SHOPOGOLIK':
    PG_DB = {
            'NAME': env.str("PG_DB_EXTERNAL"),
            'USER': env.str("PG_USER"),
            'PASSWORD': env.str("PG_PASS"),
            'HOST': env.str("PG_HOST"),
            'PORT': env.str("PG_PORT"),
    }
else:
    raise EnvironmentError

# Конфигурация базы данных MySQL
MYSQL_DB = {
    'NAME': env.str("MYSQL_DB"),
    'USER': env.str("MYSQL_USER"),
    'PASSWORD': env.str("MYSQL_PASS"),
    'HOST': env.str("MYSQL_HOST"),
    'PORT': env.str("MYSQL_PORT"),
}

# Инициализация Sentry для окружений PROD и SHOPOGOLIK
if ENVIRONMENT.value == 'PROD' or ENVIRONMENT.value == 'SHOPOGOLIK':
    sentry_sdk.init(
        dsn="https://37fa78e7680349409d9b9623a9ae045e@o1385781.ingest.us.sentry.io/6705914",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

# Чтение учетных данных Modulbank из переменных окружения
"""
MODULBANK_CREDS = {
    'MODULBANK_API_KEY': env.str("MODULBANK_API_KEY"),
    'MODULBANK_INN': env.str("MODULBANK_INN"),
    'MODULBANK_ACCOUNT_NUMBER': env.str("MODULBANK_ACCOUNT_NUMBER"),
    'MODULBANK_MAIN_ACCOUNT_ID': env.str("MODULBANK_MAIN_ACCOUNT_ID")
}
"""

# Чтение хоста ClickHouse из переменных окружения
#CH_HOST = env.str("CH_HOST")


# Чтение учетных данных WordPress из переменных окружения
WP_CONSUMER_SECRET = env.str("WP_CONSUMER_SECRET")
WP_CONSUMER_KEY = env.str("WP_CONSUMER_KEY")



def proxy_auth(phone, proxy_name, proxy_id):
    """
    Создаем zip для плагина Chrome
    он требуется для аворизации proxy
    :param phone: str
    :param proxy_name: str
    :return: str (name_zip_file)
    """
    """'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{str(PROXY_PORT)}'"""
    if os.path.isfile(f"C:/Users/Kenny/Desktop/new_bot_aiogram_external/proxy_list_phone/proxy_auth_plugin_{phone}_{str(proxy_id)}.zip"):
        plugin_file = f'C:/Users/Kenny/Desktop/new_bot_aiogram_external/proxy_list_phone/proxy_auth_plugin_{phone}_{str(proxy_id)}.zip'
        print(True)
        # чистим от шелухи из БД
    else:
        if 'https://' in proxy_name:
            new_proxy = proxy_name.strip().replace('https://', '')
        else:
            new_proxy = proxy_name

        if 'http://' in proxy_name:
            new_proxy = new_proxy.strip().replace('http://', '')
        else:
            new_proxy = proxy_name

        if '@' in proxy_name:
            new_proxy = new_proxy.strip().replace('@', ':')

        # Создаем список из данных
        new_proxy = new_proxy.split(':')
        print(new_proxy)

        PROXY_HOST = new_proxy[2]
        PROXY_PORT = new_proxy[3]
        PROXY_USER = new_proxy[0]
        PROXY_PASS = new_proxy[1]
        print(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
    
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
    
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

        plugin_file = os.path.join("C:/Users/Kenny/Desktop/new_bot_aiogram_external/proxy_list_phone", f"proxy_auth_plugin_{phone}_{str(proxy_id)}.zip")

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

    time.sleep(3)

    return plugin_file

