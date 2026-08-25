#18. Internet Subscription Management
class Subscription:
 def _init_(self, subscription_id, customer_name, plan_name, monthly_price):
      self.subscription_id = subscription_id
      self.customer_name = customer_name
      self.plan_name = plan_name
      self.monthly_price = monthly_price
      self.is_active = {self.is_active}
 def display_subscription_info(self):
   print("subscription_id:", self.subscription_id)
   print("customer_name:", self.customer_name)
   print("plan_name:", self.plan_name)
   print("monthly_price:", self.monthly_price)
 def update_plan(self, new_plan):
    self.plan_name = new_plan
    print("updated_plan:",self.plan_name) 

class SubscriptionManagement(Subscription):
  def _init_(self,subscription_id, customer_name, plan_name, monthly_price):
      super().__init__()
      self.subscriptions = []

  def activate_subscription(self, subscription_id):
     for subscriptions in subscriptions:
        if self.subscription_id == subscription_id and self.is_active == False:
           self.is_active = True
           print(f"{self.subscription_id} is the activated successfully")

  def deactivate_subscription(self, subscription_id):
    for subscriptions in subscriptions:
        if self.subscription_id == subscription_id and self.is_active == True:
           self.is_active = False
           print(f"{self.subscription_id} is the deactivated successfully")

Subscription1 = SubscriptionManagement(1001, "eshwar", "data_plan", 499)
Subscription1.display_subscription_info()
Subscription1.activate_subscription(1001)
Subscription1.update_plan("hotstar")
Subscription1.display_subscription_info()
Subscription1.deactivate_subscription(1001)
Subscription1.display_subscription_info
