from locust import TaskSet, task
from config import settings
from services.auth import get_token
from utils.timer import TokenRefresher
from data.skus import SKUS
from data.buyers import BUYER_CODES
import random
import logging
import json
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("locust.sku")

refresher = TokenRefresher(get_token)

sku_blocks = [SKUS[i:i+30] for i in range(0, len(SKUS), 30)]

ALERT_THRESHOLD_SECONDS = 10
RUN_GET_PRICE = os.getenv("RUN_GET_PRICE", "1") == "1"
RUN_SKU_BLOCK = os.getenv("RUN_SKU_BLOCK", "1") == "1"

class PriceTaskSet(TaskSet):
    def log_result(self, name, elapsed, buyer_code, sku_count, empty=False):
        token_age = refresher.get_token_age()
        age_str = f"{token_age:.1f}s" if token_age else "?"

        if empty:
            logger.warning(f"⚠️ EMPTY: No price data | {name} | buyer_code: {buyer_code} | SKUs: {sku_count} | token_age: {age_str}")
        elif elapsed > ALERT_THRESHOLD_SECONDS:
            logger.warning(f"⚠️ ALERT: {name} reply: {elapsed:.3f}s | buyer_code: {buyer_code} | SKUs: {sku_count} | token_age: {age_str}")
        else:
            logger.info(f"{name} reply: {elapsed:.3f}s | buyer_code: {buyer_code} | SKUs: {sku_count} | token_age: {age_str}")
    
    @task
    def fetch_price(self):
        if not RUN_GET_PRICE:
            return

        token = refresher.get_token()
        if not token:
            return

        sku_list_json = json.dumps(SKUS)
        buyer_code = random.choice(BUYER_CODES)

        query = {
            "query": f"""
            query MyQuery {{
              get_price(
                filters: {{
                  sku_code: {sku_list_json},
                  rounded: 2,
                  payment_code: \"R019\",
                  condition: \"YB2B\",
                  distribution_channel_code: \"10\",
                  buyer_code: \"{buyer_code}\",
                  fifo_range: [\"Z100\", \"Z098\", \"Z101\", \"Z102\"]
                }}
              ) {{
                agregators {{ sales_region_agregator {{ sales_organization_agregator {{ price_sales_agregator {{ edges {{ node {{ distribution_channel_code }} }} }} }} }} }}
              }}
            }}
            """
        }

        headers = settings.HEADERS.copy()
        headers["Authorization"] = f"Bearer {token}"
        start = time.time()
        response = self.client.post("/financial/price", json=query, headers=headers, name="Get price - Full SKUs")
        elapsed = time.time() - start

        empty = False
        if response.status_code == 200:
            try:
                result = response.json()
                data = result.get("data", {}).get("get_price", {})
                if not data or not data.get("agregators"):
                    empty = True
            except Exception as e:
                logger.error(f"Error parsing response: {e}")

        self.log_result("Get price - Full SKUs", elapsed, buyer_code, len(SKUS), empty)

    @task
    def fetch_price_with_random_block(self):
        if not RUN_SKU_BLOCK:
            return

        token = refresher.get_token()
        if not token:
            return

        skus = random.choice(sku_blocks)
        sku_list_json = json.dumps(skus)
        buyer_code = random.choice(BUYER_CODES)

        query = {
            "query": f"""
            query MyQuery {{
              get_price(
                filters: {{
                  sku_code: {sku_list_json},
                  rounded: 2,
                  payment_code: \"R019\",
                  condition: \"YB2B\",
                  distribution_channel_code: \"10\",
                  buyer_code: \"{buyer_code}\",
                  fifo_range: [\"Z100\", \"Z098\", \"Z101\", \"Z102\"]
                }}
              ) {{
                agregators {{ sales_region_agregator {{ sales_organization_agregator {{ price_sales_agregator {{ edges {{ node {{ distribution_channel_code }} }} }} }} }} }}
              }}
            }}
            """
        }

        headers = settings.HEADERS.copy()
        headers["Authorization"] = f"Bearer {token}"
        start = time.time()
        response = self.client.post("/financial/price", json=query, headers=headers, name="Get price - Block 30 SKUs")
        elapsed = time.time() - start

        empty = False
        if response.status_code == 200:
            try:
                result = response.json()
                data = result.get("data", {}).get("get_price", {})
                if not data or not data.get("agregators"):
                    empty = True
            except Exception as e:
                logger.error(f"Error parsing response: {e}")

        self.log_result("Get price - Block 30 SKUs", elapsed, buyer_code, len(skus), empty)