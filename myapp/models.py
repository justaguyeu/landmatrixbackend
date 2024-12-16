from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User




class DataEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expense_name = models.CharField(max_length=100, blank=True, null=True)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_name}"





# class NotificationPreference(models.Model):
#     NOTIFICATION_METHOD_CHOICES = [
#         ('email', 'Email'),
#         ('phone', 'Phone'),
#         ('text', 'Text Message'),
#         ('push', 'Push Notification'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     email = models.BooleanField(default=False)
#     push = models.BooleanField(default=False)
#     text = models.BooleanField(default=False)
#     phone_call = models.BooleanField(default=False)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)  # For phone numbers
#     email_address = models.EmailField(blank=True, null=True)  # For email addresses
#     preferred_method = models.CharField(max_length=10, choices=NOTIFICATION_METHOD_CHOICES, default='email')

#     def __str__(self):
#         return f'{self.user} Preferences'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    stock_item = models.ForeignKey('StockItem', null=True, blank=True, on_delete=models.CASCADE)
    substock_name = models.ForeignKey('StockItem2', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"
    
    




class NotificationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    receive_email = models.BooleanField(default=False)
    receive_sms = models.BooleanField(default=False)
    receive_push = models.BooleanField(default=False)
    receive_phone_call = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}'s notification preferences"
    
class StockItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()  # Total quantity available
    quantity_used = models.PositiveIntegerField(default=0)  # How much has been used
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    added_date = models.DateField()
    restock_quantity = models.PositiveIntegerField(default=0)
    last_restock_date = models.DateField(null=True, blank=True)
    

    def remaining_stock(self):
        """Calculate the remaining stock."""
        return self.quantity - self.quantity_used

    def total_value_used(self):
        """Total value of the used stock."""
        return self.quantity_used * self.price_per_unit

    def total_value_unused(self):
        """Total value of the remaining stock."""
        return self.remaining_stock() * self.price_per_unit

    def total_value_stock(self):
        """Total value of all stock."""
        return self.quantity * self.price_per_unit

    def is_depleted(self):
        """Check if the stock is depleted."""
        return self.remaining_stock() <= 0

    def __str__(self):
        return self.name

    def get_month(self):
        """Get the month when the stock was added."""
        return self.added_date.strftime('%Y-%m')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        remaining = self.remaining_stock()
        if remaining <= 0:
            send_stock_notification(
                stock_item=self,
                stock_name=self.name,
                remaining_stock=remaining,
                model_type='units'
            )

    # def check_stock_level(self):
    #     if self.remaining_stock <= 10:
    #         Notification.objects.create(
    #             user=User.objects.get(is_superuser=True),
    #             message=f"Stock for {self.stock_name} is running low ({self.remaining_stock}). Please restock.",
    #             stock_item=self
    #         )

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     remaining = self.remaining_area()

    #     if remaining <= 10:
    #         preferences = NotificationPreference.objects.all()

    #         for pref in preferences:
    #             message = f'{self.stock_name} stock is low! Only {remaining} square meters left.'

    #             if pref.receive_email and pref.email:
    #                 send_mail(
    #                     'Stock Low Notification',
    #                     message,
    #                     settings.DEFAULT_FROM_EMAIL,
    #                     [pref.email],
    #                 )

    #             if pref.receive_push:
    #                 # Add push notification logic here
    #                 pass

    #             if pref.receive_sms and pref.phone_number:
    #                 # Add SMS sending logic here
    #                 pass

    #             if pref.receive_phone_call and pref.phone_number:
    #                 # Add phone call logic here
    #                 pass

    #             Notification.objects.create(
    #                 user=pref.user,
    #                 message=message,
    #                 stock_item=self.stock_name
    #             )

class StockItem2main(models.Model):
    """
    Represents the main stock categories (e.g., regions).
    """
    stock_main = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.stock_main
class StockItem2(models.Model):
    """
    Represents individual stock branches under a main category.
    """
    substock_name = models.CharField(max_length=100)
    stock_main = models.ForeignKey(StockItem2main, on_delete=models.CASCADE, related_name="branches",blank=True, null=True)
    area_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2)
    area_used_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    added_date = models.DateField()
    restock_area_in_square_meters = models.PositiveIntegerField(default=0)
    last_restock_date = models.DateField(null=True, blank=True)

    # class Meta:
    #     unique_together = ('stock_name', 'stock_main')  # Ensure uniqueness of stock_name within a stock_main
    #     verbose_name = "Stock Item"
    #     verbose_name_plural = "Stock Items"

    def remaining_area(self):
        """
        Calculates the remaining area in square meters.
        """
        return self.area_in_square_meters - self.area_used_in_square_meters

    def total_value_used(self):
        """
        Calculates the total monetary value of the used stock.
        """
        return self.area_used_in_square_meters * self.price_per_square_meter

    def total_value_unused(self):
        """
        Calculates the total monetary value of the remaining stock.
        """
        return self.remaining_area() * self.price_per_square_meter

    def total_value_stock(self):
        """
        Calculates the total monetary value of the stock.
        """
        return self.area_in_square_meters * self.price_per_square_meter

    def is_depleted(self):
        """
        Determines if the stock is depleted.
        """
        return self.remaining_area() <= 0

    def get_month(self):
        """
        Returns the month the stock was added in 'YYYY-MM' format.
        """
        return self.added_date.strftime('%Y-%m')

    def save(self, *args, **kwargs):
        """
        Overrides the save method to send notifications if the stock is running low.
        """
        super().save(*args, **kwargs)
        remaining = self.remaining_area()
        if remaining <= 0:  # Notify if remaining stock is 10 or less
            send_stock_notification(
                stock_item=self,
                substock_name=self.substock_name,
                remaining_stock=remaining,
                model_type='square meters'
            )

    def __str__(self):
        return f"{self.substock_name} (Branch of {self.stock_main})"

class UserEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    

    def save(self, *args, **kwargs):
        try:
            stock_item = StockItem.objects.get(name=self.item_name)

            remaining_stock = stock_item.remaining_stock()
            if self.quantity > remaining_stock:
                raise ValueError("Not enough stock available.")
            
            if self.discount_price:
                # If there is a discount, subtract it from the calculated total
                self.total_price = (self.quantity * stock_item.price_per_unit) - self.discount_price
            else:
                # If no discount, use the regular calculation
                self.total_price = self.quantity * stock_item.price_per_unit
            
            # Update the stock item quantity used
            stock_item.quantity_used += self.quantity
            stock_item.save()


            # Check if stock is depleted
            if stock_item.is_depleted():
            # Send notification to the admin (this could be an email, alert, etc.)
            # You could implement a notification system here
                pass

        except StockItem.DoesNotExist:
            self.total_price = 0  # Handle cases where the stock item does not exist

        # Ensure the total price is not negative
        if self.total_price < 0:
            self.total_price = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.item_name} - {self.date}"



# class UserEntry2(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     stock_main = models.CharField(max_length=100, blank=True, null=True)
#     substock_name = models.CharField(max_length=100)
#     area_in_square_meters = models.DecimalField(
#         max_digits=10, 
#         decimal_places=5,
#         validators=[MinValueValidator(0)] 
#     )
#     total_price = models.DecimalField(max_digits=1000, decimal_places=2)
#     percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     name = models.CharField(max_length=100,blank=True, null=True)
#     email = models.EmailField(null=True, blank=True)
#     phone_number = models.CharField(max_length=15)

#     def save(self, *args, **kwargs):
#         try:
#             stock_item = StockItem2.objects.get(substock_name=self.substock_name)

#             remaining_area = stock_item.remaining_area()
#             if self.area_in_square_meters > remaining_area:
#                 raise ValueError("Not enough stock available.")

#             if self.discount_price:
#                 self.total_price = (self.area_in_square_meters * stock_item.price_per_square_meter * (self.percentage / 100)) - self.discount_price
#             else:
#                 self.total_price = self.area_in_square_meters * stock_item.price_per_square_meter

#             # Update the stock item quantity used
#             stock_item.area_used_in_square_meters += self.area_in_square_meters
#             stock_item.save()

#             if stock_item.is_depleted():
#                 send_stock_notification(
#                     admin_email="admin@example.com",
#                     message=f"Stock for {stock_item.substock_name} is depleted."
#                 )

#         except StockItem2.DoesNotExist:
#             self.total_price = 0

#         if self.total_price < 0:
#             self.total_price = 0

#         super().save(*args, **kwargs)

#         def __str__(self):
#             return f"{self.user.username} - {self.substock_name} - {self.date}"
class UserEntry2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    stock_main = models.CharField(max_length=100, blank=True, null=True)
    substock_name = models.CharField(max_length=100)
    area_in_square_meters = models.DecimalField(
        max_digits=10, 
        decimal_places=5,
        validators=[MinValueValidator(0)] 
    )
    total_price = models.DecimalField(max_digits=1000, decimal_places=2)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        # Simply save the object without additional logic
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.substock_name} - {self.date}"

class UserEntryExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    expense_name = models.CharField(max_length=100, blank=True, null=True)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"{self.user.username} - {self.expense_name} - {self.date}"
    
class UserEntryOutofstock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # New field for total price


    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.date}"
  

class StockRestock(models.Model):
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='restocks')
    quantity = models.PositiveIntegerField()
    restock_date = models.DateField()

    def __str__(self):
        return f"{self.stock_item.name} - {self.quantity} units on {self.restock_date}"
    

class Debt(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid')
    ]

    stock_name = models.CharField(max_length=100)
    debtor_name = models.CharField(max_length=100)
    stock_dimensions = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            # Fetch the related stock item price
            stock_item = StockItem.objects.get(name=self.stock_name)

            # Assuming the amount refers to the quantity of the stock item
            # You could calculate total price as (amount * stock price)
            self.total_price = self.amount * stock_item.price_per_unit  # Adjust based on your pricing model

            # Ensure total price is not negative
            if self.total_price < 0:
                self.total_price = 0

        except StockItem.DoesNotExist:
            # If the stock item doesn't exist, default to the amount itself
            self.total_price = self.amount

        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.debtor_name} owes {self.total_price} on {self.date}'
    
    
    

    
def send_stock_notification(substock_name, remaining_stock, model_type='unit'):
    try:
        admin_user = User.objects.get(is_superuser=True)  # Assuming the admin is a superuser
    except User.DoesNotExist:
        print('Admin user does not exist')
        return

    message = f"Stock Alert: {substock_name} has only {remaining_stock} {model_type} left."
    notification = Notification(
        user=admin_user,
        message=message,
        is_read=False
    )
    notification.save()
    print(f"Notification sent: {message}")
  

