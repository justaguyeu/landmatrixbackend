from django import forms
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DataEntry, Debt, Notification, StockItem, StockItem2, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock

class DataEntrySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = DataEntry
        fields = ['user', 'date', 'item_name', 'quantity', 'price', 'expense_name', 'expenses']

class StockItemSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    class Meta:
        model = StockItem
        fields = ['id', 'name', 'quantity', 'price_per_unit','added_date','month', "restock_quantity" ,"last_restock_date"]

    def get_month(self, obj):
     return obj.get_month()

class StockItemSerializer2(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    class Meta:
        model = StockItem2
        fields = ['id', 'stock_name', 'area_in_square_meters', 'price_per_square_meter','added_date','month', 'restock_area_in_square_meters','last_restock_date' ]

    def get_month(self, obj):
     return obj.get_month()
class UserEntrySerializer(serializers.ModelSerializer):
    item = serializers.StringRelatedField()
    user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

    class Meta:
        model = UserEntry
        fields = '__all__'

class UserEntrySerializer2(serializers.ModelSerializer):
    item = serializers.StringRelatedField()
    user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

    class Meta:
        model = UserEntry2
        fields = '__all__'

class UserEntrySerializerExpense(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

    class Meta:
        model = UserEntryExpense
        fields = '__all__'

class UserEntrySerializerOutofstock(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

    class Meta:
        model = UserEntryOutofstock
        fields = '__all__'        

class StockReportSerializer(serializers.ModelSerializer):
    remaining_stock = serializers.SerializerMethodField()
    total_value_used = serializers.SerializerMethodField()
    total_value_unused = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = ['name', 'quantity_used', 'remaining_stock', 'total_value_used', 'total_value_unused']

    def get_remaining_stock(self, obj):
        return obj.remaining_stock()

    def get_total_value_used(self, obj):
        return obj.total_value_used()

    def get_total_value_unused(self, obj):
        return obj.total_value_unused()

class StockItemRestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = ['name', 'quantity']

class StockItem2RestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem2
        fields = ['stock_name', 'area_in_square_meters']


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ['id', 'stock_name', 'debtor_name', 'stock_dimensions', 'amount', 'date', 'status', 'user']
        read_only_fields = ['user']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'stock_item']
