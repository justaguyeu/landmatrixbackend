from django.contrib import admin
from .models import DataEntry, Debt, StockItem, StockItem2, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock

@admin.register(DataEntry)
class DataEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'item_name', 'quantity', 'price', 'expense_name', 'expenses')
    search_fields = ('user__username', 'item_name')
    list_filter = ('date', 'user')

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price_per_unit','quantity_used', "restock_quantity" ,"last_restock_date")

@admin.register(StockItem2)
class StockItemAdmin2(admin.ModelAdmin):
    list_display = ('stock_name', 'area_in_square_meters', 'area_used_in_square_meters','price_per_square_meter','restock_area_in_square_meters','last_restock_date' )    

@admin.register(UserEntry)
class UserEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'item_name', 'quantity', 'total_price', 'discount_price')

@admin.register(UserEntry2)
class UserEntryAdmin2(admin.ModelAdmin):
    list_display = ('user', 'date', 'item_name', 'area_in_square_meters', 'total_price','percentage', 'discount_price')

@admin.register(UserEntryExpense)
class UserEntryAdminExpense(admin.ModelAdmin):
    list_display = ('user', 'date', 'expense_name', 'expenses')

@admin.register(UserEntryOutofstock)
class UserEntryAdminOutofstock(admin.ModelAdmin):
    list_display = ('user', 'date', 'name', 'price')    

# Make sure you only register each model once.
@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('user', 'debtor_name', 'stock_dimensions', 'stock_name', 'amount', 'date', 'status')
    list_filter = ('status', 'date', 'user')
    search_fields = ('debtor_name', 'stock_name', 'user__username')