from locust import HttpUser, task, between

class MerchShopUser(HttpUser):
    wait_time = between(1, 2)
    token = None
    
    def on_start(self):
        response = self.client.post("/api/auth", json={
            "username": f"user_{self.user_id}",
            "password": "password"
        })
        self.token = response.json()['token']
    
    @task(2)
    def get_info(self):
        self.client.get("/api/info", 
                       headers={'Authorization': f'Bearer {self.token}'})
    
    @task(1)
    def buy_item(self):
        self.client.get("/api/buy/cup",
                       headers={'Authorization': f'Bearer {self.token}'})
    
    @task(1)
    def send_coins(self):
        self.client.post("/api/sendCoin",
                        headers={'Authorization': f'Bearer {self.token}'},
                        json={
                            "toUser": f"user_{(self.user_id + 1) % 100}",
                            "amount": 10
                        })