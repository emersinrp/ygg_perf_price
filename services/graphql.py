import requests
from config import settings

def get_price(token: str):
    query = {
        "query": "query MyQuery { get_price(filters: {sku_code: [\"000000000000031933\"], rounded: 2, payment_code: \"R019\", condition: \"YB2B\", distribution_channel_code: \"10\", buyer_code: \"0007554445\", fifo_range: [\"Z100\", \"Z098\", \"Z101\", \"Z102\"]}) { agregators { sales_region_agregator { sales_organization_agregator { price_sales_agregator { edges { node { distribution_channel_code material_type_size_agregator { box { brl { price_itens { sku_code item_category_agregator { item_category_code price_detail { base_price price discount_price tributary_substitution_price tributary_substitution_discount_price discount_percent } } } } } } } } } } } } } }"
    }
    headers = settings.HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.post(settings.PRICE_URL, json=query, headers=headers)
    response.raise_for_status()
    return response.json()