from django.contrib import admin
from .models import DataEntry, Debt, StockItem, StockItem2, StockItem2main, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock

@admin.register(DataEntry)
class DataEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'item_name', 'quantity', 'price', 'expense_name', 'expenses')
    search_fields = ('user__username', 'item_name')
    list_filter = ('date', 'user')

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price_per_unit','quantity_used', "restock_quantity" ,"last_restock_date")


class StockItem2Inline(admin.TabularInline):  # Use TabularInline or StackedInline
    model = StockItem2
    extra = 1  # This will add an extra empty form for adding a new sub-stock
    fields = ('substock_name', 'area_in_square_meters', 'price_per_square_meter', 'added_date')
    fk_name = 'stock_main'  # Ensures that the relationship is created via the 'stock_main' ForeignKey

class StockItem2mainAdmin(admin.ModelAdmin):
    list_display = ('stock_main',)  # Shows the 'stock_main' field in the main stock list view
    inlines = [StockItem2Inline]  # Display the related substocks inside the main stock's admin page

class StockItem2Admin(admin.ModelAdmin):
    list_display = ('substock_name', 'stock_main', 'area_in_square_meters', 'price_per_square_meter', 'added_date')
    list_filter = ('stock_main',)
    search_fields = ('substock_name', 'stock_main__stock_main')

# Register models with the admin interface
admin.site.register(StockItem2main, StockItem2mainAdmin)
admin.site.register(StockItem2, StockItem2Admin)

@admin.register(UserEntry)
class UserEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'item_name', 'quantity', 'total_price', 'discount_price')

@admin.register(UserEntry2)
class UserEntryAdmin2(admin.ModelAdmin):
    list_display = ('user', 'date', 'substock_name', 'area_in_square_meters', 'total_price','percentage', 'discount_price',"name", "email", "phone_number")

@admin.register(UserEntryExpense)
class UserEntryAdminExpense(admin.ModelAdmin):
    list_display = ('user', 'date', 'expense_name', 'expenses')

@admin.register(UserEntryOutofstock)
class UserEntryAdminOutofstock(admin.ModelAdmin):
    list_display = ('user', 'date', 'name', 'price')    

# Make sure you only register each model once.
@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('user', 'debtor_name', 'stock_dimensions', 'stock_name', 'amount', 'date', 'status', "email", "phone_number")
    list_filter = ('status', 'date', 'user')
    search_fields = ('debtor_name', 'stock_name', 'user__username')

  