# locustfile.py
from locust import HttpUser, between
from tasks.price_task import PriceTaskSet

class WebsiteUser(HttpUser):
    host = "https://ygg.brf.cloud"
    tasks = [PriceTaskSet]
    wait_time = between(1, 5)