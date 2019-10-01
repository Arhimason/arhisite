import importlib

# todo auto check all modules?
IMPORT_PRICES_FROM = [
    'bot_handler.modules.burger_king'
]

PRICES = {}

for module in IMPORT_PRICES_FROM:
    config_file = importlib.import_module(f'{module}._config')
    prices_dict = config_file.PRICES
    PRICES.update(prices_dict)

PAYMENT_VALID_TIME = 30
