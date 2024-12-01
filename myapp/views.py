from decimal import Decimal
from urllib import request, response
from venv import logger
from django.forms import ValidationError
from django.http import JsonResponse
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .models import DataEntry, Debt, Notification, NotificationPreference, StockItem, StockItem2, StockItem2main, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock
from django.db.models import F 
from .serializers import DataEntrySerializer, DebtSerializer, NotificationSerializer, StockItem2RestockSerializer, StockItem2mainSerializer, StockItemRestockSerializer, StockItemSerializer, StockItemSerializer2, StockReportSerializer, UserEntrySerializer, UserEntrySerializer2, UserEntrySerializerExpense, UserEntrySerializerOutofstock
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from .models import NotificationPreference
from .utils import send_sms, send_email
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from urllib.parse import unquote  # Ensure this is imported
from .models import StockItem2

from myapp import models

from myapp import serializers


class DataEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = DataEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DataEntry.objects.all()
        return DataEntry.objects.filter(user=user)

    def perform_create(self, serializer):
        # Correcting the indentation
        serializer.save(user=self.request.user)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Extract username and password from request
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            # Authenticate the user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Authentication successful, proceed with token generation
                response = super().post(request, *args, **kwargs)
                
                # Add custom data to the response based on user type
                if user.is_staff:
                    response.data['is_staff'] = True
                    response.data['message'] = "Login successful. Welcome, admin!"
                else:
                    response.data['is_staff'] = False
                    response.data['message'] = "Login successful. Welcome, user!"
                
                return response
            else:
                # User authentication failed (incorrect password or non-existent user)
                return Response({
                    'message': "Invalid credentials. Check your username and password."
                }, status=401)

        except User.DoesNotExist:
            # Handle case where user does not exist
            return Response({
                'message': "User does not exist."
            }, status=400)
class MonthlyReportView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        if not month:
            return Response({"error": "Month parameter is required."}, status=400)
        
        try:
            year, month_number = map(int, month.split('-'))
            start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
            if month_number == 12:
                end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
            else:
                end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

        # Fetch UserEntry and UserEntry2 data
        user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
        user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
        
        # Fetch ExpenseEntry data
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
        debt_entries = Debt.objects.filter(date__gte=start_date, date__lt=end_date)
        outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date)

        # Combine daily totals for both UserEntry and UserEntry2
        daily_totals = (
            user_entries.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )

        daily_totals2 = (
            user_entries2.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )
       

        # Merge sales data from both UserEntry and UserEntry2
        combined_sales_totals = {}
        for entry in daily_totals:
            date = entry['date']
            combined_sales_totals[date] = entry['total_sales']

        for entry in daily_totals2:
            date = entry['date']
            if date in combined_sales_totals:
                combined_sales_totals[date] += entry['total_sales']
            else:
                combined_sales_totals[date] = entry['total_sales']

        # Combine daily totals with expenses
        daily_expenses = (
            expense_entries.values('date')
            .annotate(total_expenses=Sum('expenses'))
            .order_by('date')
        )

        daily_debts = (
            debt_entries.values('date')
            .annotate(total_debts=Sum('amount'))
            .order_by('date')
        )

        daily_outofstock = (
            outofstock_entries.values('date')
            .annotate(total_outofstock=Sum('price'))
            .order_by('date')
        )

        combined_daily_totals = []
        all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_outofstock) | set(item['date'] for item in daily_debts) | set(item['date'] for item in daily_expenses)

        for date in sorted(all_dates):
            daily_sales = combined_sales_totals.get(date, 0)
            daily_outofstock_value = next((item['total_outofstock'] for item in daily_outofstock if item['date'] == date), 0)or 0
            daily_debts_value = next((item['total_debts'] for item in daily_debts if item['date'] == date), 0) or 0
            daily_expense_value = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)or 0
            combined_daily_totals.append({
                'date': date,
                'total_sales': daily_sales,
                'total_expenses': daily_expense_value,
                'total_debts': daily_debts_value,
                'total_outofstock': daily_outofstock_value, 
                'profit': daily_sales + daily_outofstock_value - daily_expense_value
            })

        # Calculate monthly totals
        total_sales = sum(combined_sales_totals.values())
        total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
        total_debts = debt_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0
        profit = total_sales + total_outofstock - total_expenses

        monthly_totals = {
            'total_sales': total_sales,
            'total_expenses': total_expenses,
            'total_debts': total_debts,
            'total_outofstock': total_outofstock,
            'profit': profit,
        }

        return Response({'daily_totals': combined_daily_totals, 'monthly_totals': monthly_totals})

class WeeklyReportView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            return Response({"error": "Start date and end date parameters are required."}, status=400)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Fetch UserEntry and UserEntry2 data
        user_entries = UserEntry.objects.filter(date__gte=start_date, date__lte=end_date)
        user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lte=end_date)
        
        # Fetch ExpenseEntry data
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lte=end_date)
        debt_entries = Debt.objects.filter(date__gte=start_date, date__lt=end_date)
        outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date)

        # Combine daily totals for both UserEntry and UserEntry2
        daily_totals = (
            user_entries.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )

        daily_totals2 = (
            user_entries2.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )

        # Merge sales data from both UserEntry and UserEntry2
        combined_sales_totals = {}
        for entry in daily_totals:
            date = entry['date']
            combined_sales_totals[date] = entry['total_sales']

        for entry in daily_totals2:
            date = entry['date']
            if date in combined_sales_totals:
                combined_sales_totals[date] += entry['total_sales']
            else:
                combined_sales_totals[date] = entry['total_sales']

        # Combine daily totals with expenses
        daily_expenses = (
            expense_entries.values('date')
            .annotate(total_expenses=Sum('expenses'))
            .order_by('date')
        )

        daily_debts = (
            debt_entries.values('date')
            .annotate(total_debts=Sum('amount'))
            .order_by('date')
        )

        daily_outofstock = (
            outofstock_entries.values('date')
            .annotate(total_outofstock=Sum('price'))
            .order_by('date')
        )

        combined_daily_totals = []
        all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_outofstock) | set(item['date'] for item in daily_debts)

        for date in sorted(all_dates):
            daily_sales = combined_sales_totals.get(date, 0)
            daily_outofstock_value = next((item['total_outofstock'] for item in daily_outofstock if item['date'] == date), 0)or 0
            daily_debts_value = next((item['total_debts'] for item in daily_debts if item['date'] == date), 0) or 0
            daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0) or 0
            combined_daily_totals.append({
                'date': date.strftime('%Y-%m-%d'),  # Convert date to string format
                'total_sales': daily_sales,
                'total_debts': daily_debts_value,
                'total_outofstock': daily_outofstock_value, 
                'total_expenses': daily_expense,
                'profit': daily_sales + daily_outofstock_value - daily_expense
            })

        # Calculate weekly totals
        total_sales = sum(combined_sales_totals.values())
        total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
        total_debts = debt_entries.aggregate(Sum('amount'))['amount__sum'] or 0
        total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0
        profit = total_sales + total_outofstock - total_expenses

        weekly_totals = {
            'total_sales': total_sales,
            'total_debts': total_debts,
            'total_outofstock': total_outofstock,
            'total_expenses': total_expenses,
            'profit': profit,
        }

        return Response({'daily_totals': combined_daily_totals, 'weekly_totals': weekly_totals})

#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         if not month:
#             return Response({"error": "Month parameter is required."}, status=400)
        
#         try:
#             year, month_number = map(int, month.split('-'))
#             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
#             # Get the first day of the next month for `end_date`
#             if month_number == 12:
#                 end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
#             else:
#                 end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

#         # Fetch UserEntry data
#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
        
#         # Fetch ExpenseEntry data
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
        
#         # Calculate daily totals for sales and expenses
#         daily_totalss = (
#             user_entries.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         # Combine daily totals with expenses
#         daily_expenses = (
#             expense_entries.values('date')
#             .annotate(total_expenses=Sum('expenses'))
#             .order_by('date')
#         )

#         # Merge daily totals and daily expenses
#         combined_daily_totals = []
#         all_dates = set([item['date'] for item in daily_totalss] + [item['date'] for item in daily_expenses])

#         for date in sorted(all_dates):
#             daily_sales = next((item['total_sales'] for item in daily_totalss if item['date'] == date), 0)
#             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
#             combined_daily_totals.append({
#                 'date': date,
#                 'total_sales': daily_sales,
#                 'total_expenses': daily_expense,
#                 'profit': daily_sales - daily_expense
#             })

#         # Calculate monthly totals
#         total_sales = user_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         profit = total_sales - total_expenses

#         monthly_totalss = {
#             'total_sales': total_sales,
#             'total_expenses': total_expenses,
#             'profit': profit,
#         }

#         return Response({'daily_totalss': combined_daily_totals, 'monthly_totalss': monthly_totalss})
    
class MonthlyReportView2(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        if not month:
            return Response({"error": "Month parameter is required."}, status=400)
        
        try:
            year, month_number = map(int, month.split('-'))
            start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
            
            if month_number == 12:
                end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
            else:
                end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

        # Fetch UserEntry data
        user_entries = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
        
        # Fetch ExpenseEntry data
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
        
        # Calculate daily totals for sales and expenses
        daily_totalss = (
            user_entries.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )

        # Combine daily totals with expenses
        daily_expenses = (
            expense_entries.values('date')
            .annotate(total_expenses=Sum('expenses'))
            .order_by('date')
        )

        # Merge daily totals and daily expenses
        combined_daily_totalss = []
        all_dates = set([item['date'] for item in daily_totalss] + [item['date'] for item in daily_expenses])

        for date in sorted(all_dates):
            daily_sales = next((item['total_sales'] for item in daily_totalss if item['date'] == date), 0)
            daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
            combined_daily_totalss.append({
                'date': date,
                'total_sales': daily_sales,
                'total_expenses': daily_expense,
                'profit': daily_sales - daily_expense
            })

        # Calculate monthly totals
        total_sales = user_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
        profit = total_sales - total_expenses

        monthly_totalss = {
            'total_sales': total_sales,
            'total_expenses': total_expenses,
            'profit': profit,
        }

        return Response({'daily_totalss': combined_daily_totalss, 'monthly_totalss': monthly_totalss})  

class StockItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer

    def get(self, request):
        selected_month = request.query_params.get('month')
        
        if selected_month:
            try:
                year, month = map(int, selected_month.split('-'))
                
               
                stock_items = StockItem.objects.filter(
                    date_added__year=year,
                    date_added__month=month
                )
            except ValueError:
                return Response({"error": "Invalid month format. Please use 'YYYY-MM' format."}, status=400)

        else:
            
            stock_items = StockItem.objects.all()
        
        serializer = StockItemSerializer(stock_items, many=True)
        return Response(serializer.data)

class UserEntryViewSet(viewsets.ModelViewSet):
    queryset = UserEntry.objects.all()
    serializer_class = UserEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntry.objects.all()
        return UserEntry.objects.filter(user=user)
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        # Custom behavior during update (if needed)
        serializer.save(user=self.request.user)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

    def post(self, request):
        serializer = UserEntrySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def put(self, request, pk):
        try:
            data = UserEntry.objects.get(pk=pk)
        except UserEntry.DoesNotExist:
            return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserEntrySerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)   

# class UserEntryViewSet(viewsets.ModelViewSet):
#     queryset = UserEntry.objects.all()
#     serializer_class = UserEntrySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """
#         Customize queryset: return all entries for admin users and filtered entries for regular users.
#         """
#         user = self.request.user
#         if user.is_staff:
#             return UserEntry.objects.all()  # Admin gets all entries
#         return UserEntry.objects.filter(user=user)  # Regular users see only their own entries

#     def perform_create(self, serializer):
#         """
#         Automatically assign the logged-in user when creating a new UserEntry.
#         """
#         serializer.save(user=self.request.user)

#     def update(self, request, *args, **kwargs):
#         """
#         Override the update method to handle PUT requests for updating an entry.
#         """
#         try:
#             instance = self.get_object()  # Get the entry to be updated
#         except Data.DoesNotExist:
#             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = DataSerializer(instance, data=request.data, partial=False)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserEntryViewSet2(viewsets.ModelViewSet):
    queryset = UserEntry2.objects.all()
    serializer_class = UserEntrySerializer2
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntry2.objects.all()
        return UserEntry2.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        # Custom behavior during update (if needed)
        serializer.save(user=self.request.user)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

    def post(self, request):
        serializer = UserEntrySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def put(self, request, pk):
        try:
            data = UserEntry.objects.get(pk=pk)
        except UserEntry.DoesNotExist:
            return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserEntrySerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class UserEntryViewSetExpense(viewsets.ModelViewSet):
    queryset = UserEntryExpense.objects.all()
    serializer_class = UserEntrySerializerExpense
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntryExpense.objects.all()
        return UserEntryExpense.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)       

class UserEntryViewSeta(viewsets.ModelViewSet):
    queryset = UserEntry.objects.all()
    serializer_class = UserEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntry.objects.all()
        return UserEntry.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Custom behavior during update (if needed)
        serializer.save(user=self.request.user)
class UserEntryViewSet2a(viewsets.ModelViewSet):
    queryset = UserEntry2.objects.all()
    serializer_class = UserEntrySerializer2
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntry2.objects.all()
        return UserEntry2.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserEntryViewSetExpensea(viewsets.ModelViewSet):
    queryset = UserEntryExpense.objects.all()
    serializer_class = UserEntrySerializerExpense
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntryExpense.objects.all()
        return UserEntryExpense.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

class UserEntryViewSetOutofstock(viewsets.ModelViewSet):
    queryset = UserEntryOutofstock.objects.all()
    serializer_class = UserEntrySerializerOutofstock
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserEntryOutofstock.objects.all()
        return UserEntryOutofstock.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)               


class StockReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')

        if month:
            try:
                year, month = map(int, month.split('-'))
                start_date = datetime(year, month, 1)
                end_date = (start_date + timedelta(days=31)).replace(day=1)
            except ValueError:
                return Response({"error": "Invalid month format."}, status=400)
        else:
            start_date = None
            end_date = None

        stock_items = StockItem.objects.all()

        report = []
        for stock in stock_items:
            user_entries = UserEntry.objects.filter(item_name=stock.name)
            if start_date and end_date:
                user_entries = user_entries.filter(date__gte=start_date, date__lt=end_date)

            quantity_used = user_entries.aggregate(Sum('quantity'))['quantity__sum'] or 0
            remaining_stock = stock.quantity - quantity_used
            total_value_used = quantity_used * stock.price_per_unit
            total_value_unused = remaining_stock * stock.price_per_unit
            total_value_stock = stock.quantity * stock.price_per_unit

            report.append({
                'item_name': stock.name,
                'total_quantity': stock.quantity,
                'quantity_used': quantity_used,
                'remaining_stock': remaining_stock,
                'total_value_used': total_value_used,
                'total_value_unused': total_value_unused,
                'total_value_stock': total_value_stock,
            })

        return JsonResponse(report, safe=False)
    
class StockReportView2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')

        if month:
            try:
                year, month = map(int, month.split('-'))
                start_date = datetime(year, month, 1)
                end_date = (start_date + timedelta(days=31)).replace(day=1)
            except ValueError:
                return Response({"error": "Invalid month format."}, status=400)
        else:
            start_date = None
            end_date = None

        stock_items = StockItem2.objects.all()

        report = []
        for stock in stock_items:
            user_entries = UserEntry2.objects.filter(substock_name=stock.substock_name)
            if start_date and end_date:
                user_entries = user_entries.filter(date__gte=start_date, date__lt=end_date)

            area_used_in_square_meters = user_entries.aggregate(Sum('area_in_square_meters'))['area_in_square_meters__sum'] or 0
            remaining_stock = stock.area_in_square_meters - area_used_in_square_meters
            total_value_used = area_used_in_square_meters * stock.price_per_square_meter
            total_value_unused = remaining_stock * stock.price_per_square_meter
            total_value_stock = stock.area_in_square_meters * stock.price_per_square_meter

            report.append({
                'stock_main': str(stock.stock_main),
                'substock_name': stock.substock_name,
                'total_quantity': stock.area_in_square_meters,
                'quantity_used': area_used_in_square_meters,
                'remaining_stock': remaining_stock,
                'total_value_used': total_value_used,
                'total_value_unused': total_value_unused,
                'total_value_stock': total_value_stock,
            })
            
        return JsonResponse(report, safe=False)    
class StockItemListCreateView(generics.ListCreateAPIView):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')

        if month:
            try:
                selected_month = datetime.strptime(month, "%Y-%m").date()
                stock_items = StockItem.objects.filter(
                    added_date__year=selected_month.year,
                    added_date__month=selected_month.month
                )
            except ValueError:
                return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
        else:
            stock_items = StockItem.objects.all()

        serializer = StockItemSerializer(stock_items, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data
        item_name = data.get('item_name')
        restock_quantity = int(data.get('quantity'))

        try:
            stock_item = StockItem.objects.get(name=item_name)
            stock_item.quantity += restock_quantity
            stock_item.save()

            return Response({
                "message": f"Stock updated successfully. New quantity for {item_name} is {stock_item.quantity}."
            }, status=200)

        except StockItem.DoesNotExist:
            return Response({"error": "Item not found."}, status=404)
        
        
        

def get_substocks(request, main_stock):
    try:
        # Decode URL-encoded characters (e.g., spaces as %20)
        main_stock = unquote(main_stock)
        
        # Query the StockItem2 model to get sub-stocks under the selected main stock
        substocks = StockItem2.objects.filter(stock_main__stock_main=main_stock)
        
        # Prepare the response data
        data = {'branches': list(substocks.values('id', 'substock_name'))}
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)     

class StockItem2mainCreateView(generics.ListCreateAPIView):
    queryset = StockItem2main.objects.all()
    serializer_class = StockItem2mainSerializer   
class StockItemListCreateView2(generics.ListCreateAPIView):
    queryset = StockItem2.objects.all()
    serializer_class = StockItemSerializer2
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')

        if month:
            try:
                selected_month = datetime.strptime(month, "%Y-%m").date()
                stock_items = StockItem2.objects.filter(
                    added_date__year=selected_month.year,
                    added_date__month=selected_month.month
                )
            except ValueError:
                return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
        else:
            stock_items = StockItem2.objects.all()

        serializer = StockItemSerializer2(stock_items, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data
        item_name = data.get('substock_name') 
        restock_quantity = Decimal(data.get('area_in_square_meters'))

        try:
            # Use the correct field name for querying
            stock_item = StockItem2.objects.get(substock_name=item_name)
            
            # Update the stock area in square meters
            stock_item.area_in_square_meters += restock_quantity
            stock_item.save()

            return Response({
                "message": f"Compound updated successfully. New quantity for {item_name} is {stock_item.area_in_square_meters}."
            }, status=200)

        except StockItem2.DoesNotExist:
            return Response({"error": "Item not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        

class StockItemListCreateViewa(generics.ListCreateAPIView):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        
        
        if month:
            try:
                
                selected_month = datetime.strptime(month, "%Y-%m").date()

               
                stock_items = StockItem.objects.filter(
                    added_date__year=selected_month.year,
                    added_date__month=selected_month.month
                )
            except ValueError:
                return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
        else:
            stock_items = StockItem.objects.all()

        serializer = StockItemSerializer(stock_items, many=True)
        return Response(serializer.data)
    
class StockItemListCreateView2a(generics.ListCreateAPIView):
    queryset = StockItem2.objects.all()
    serializer_class = StockItemSerializer2
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        
        
        if month:
            try:
                
                selected_month = datetime.strptime(month, "%Y-%m").date()

               
                stock_items = StockItem2.objects.filter(
                    added_date__year=selected_month.year,
                    added_date__month=selected_month.month
                )
            except ValueError:
                return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
        else:
            stock_items = StockItem2.objects.all()

        serializer = StockItemSerializer2(stock_items, many=True)
        return Response(serializer.data)



class StockItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]


class AvailableStockItemsView(APIView):
    def get(self, request):
        available_stock_items = StockItem.objects.filter(quantity__gt=F('quantity_used'))
        serialized_data = StockItemSerializer(available_stock_items, many=True).data
        return Response(serialized_data)   
    
class AvailableStockItemsView2(APIView):
    def get(self, request):
        available_stock_items = StockItem2.objects.filter(area_in_square_meters__gt=F('area_used_in_square_meters'))
        serialized_data = StockItemSerializer2(available_stock_items, many=True).data
        return Response(serialized_data)   


class YearlyReportView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        if not year:
            return Response({"error": "Year parameter is required."}, status=400)

        try:
            year = int(year)
            start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
            end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid year format. Use YYYY."}, status=400)

        # Fetch data for the entire year
        user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
        user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)

        # Combine daily totals for UserEntry and UserEntry2
        daily_totals = (
            user_entries.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )

        daily_totals2 = (
            user_entries2.values('date')
            .annotate(total_sales=Sum('total_price'))
            .order_by('date')
        )

        # Merge sales data from both UserEntry and UserEntry2
        combined_sales_totals = {}
        for entry in daily_totals:
            date = entry['date']
            combined_sales_totals[date] = entry['total_sales']

        for entry in daily_totals2:
            date = entry['date']
            if date in combined_sales_totals:
                combined_sales_totals[date] += entry['total_sales']
            else:
                combined_sales_totals[date] = entry['total_sales']

        # Combine daily totals with expenses
        daily_expenses = (
            expense_entries.values('date')
            .annotate(total_expenses=Sum('expenses'))
            .order_by('date')
        )

        combined_daily_totals = []
        all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_expenses)

        for date in sorted(all_dates):
            daily_sales = combined_sales_totals.get(date, 0)
            daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
            combined_daily_totals.append({
                'date': date,
                'total_sales': daily_sales,
                'total_expenses': daily_expense,
                'profit': daily_sales - daily_expense
            })

        # Calculate monthly totals
        total_sales = sum(combined_sales_totals.values())
        total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
        profit = total_sales - total_expenses

        monthly_totals = {
            'total_sales': total_sales,
            'total_expenses': total_expenses,
            'profit': profit,
        }

        return Response({'daily_totals': combined_daily_totals, 'monthly_totals': monthly_totals})

# Add this path to your urls.py
from django.urls import path



class RestockView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_data = request.data.get('item')
        item_type = request.data.get('item_type')

        if item_type == 'StockItem':
            serializer = StockItemRestockSerializer(data=item_data)
            if serializer.is_valid():
                name = serializer.validated_data['name']
                quantity = serializer.validated_data['quantity']
                
                try:
                    stock_item = StockItem.objects.get(name=name)
                    stock_item.quantity += quantity
                    stock_item.restock_quantity = quantity
                    stock_item.last_restock_date = datetime.now().date()
                    stock_item.save()
                    return Response({'message': 'StockItem restocked successfully.'}, status=status.HTTP_200_OK)
                except StockItem.DoesNotExist:
                    return Response({'error': 'StockItem not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif item_type == 'StockItem2':
            serializer = StockItem2RestockSerializer(data=item_data)
            if serializer.is_valid():
                stock_name = serializer.validated_data['stock_name']
                area_in_square_meters = serializer.validated_data['area_in_square_meters']
                
                try:
                    stock_item2 = StockItem2.objects.get(stock_name=stock_name)
                    stock_item2.area_in_square_meters += area_in_square_meters
                    stock_item2.last_restock_date = datetime.now().date()
                    stock_item2.save()
                    return Response({'message': 'StockItem2 restocked successfully.'}, status=status.HTTP_200_OK)
                except StockItem2.DoesNotExist:
                    return Response({'error': 'StockItem2 not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)
    


class DebtEntryViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            return Response({"error": "Start date and end date parameters are required."}, status=400)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    # Ensure the user can only access their own debts, unless they are admin
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Debt.objects.all()
        return Debt.objects.filter(user=user)\

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)  

    # def partial_update(self, request, *args, **kwargs):
    #     kwargs['partial'] = True
    #     return super().update(request, *args, **kwargs)      

    def post(self, request):
        serializer = DebtSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def update_debt(request, debt_id):
    #     try:
    #         debt = Debt.objects.get(pk=debt_id)
    #     except Debt.DoesNotExist:
    #         return JsonResponse({"error": "Debt not found"}, status=404)

    #     # Update debt object based on request data
    #     # debt.status = request.data.get('status')  # Assuming 'amount' is a field in your Debt model
    #     # debt.save()

    #     return JsonResponse({"message": "Debt updated successfully"}, status=200)



class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all().values('id', 'username')
        return Response(users, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        User.objects.create(username=username, password=make_password(password))
        return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)

# Delete user
class UserDeleteView(DestroyAPIView):
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

# Change password view
class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'error': 'Old and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        notifications_list = [{"message": n.message, "created_at": n.created_at} for n in notifications]
        return JsonResponse({"notifications": notifications_list})
    return JsonResponse({"notifications": []})


@api_view(['POST'])
def update_preferences(request):
    user = request.user
    data = request.data

    # Update or create preferences for the user
    preferences, created = NotificationPreference.objects.get_or_create(user=user)
    preferences.email = data.get('email', False)
    preferences.push = data.get('push', False)
    preferences.text = data.get('text', False)
    preferences.phone_call = data.get('phone_call', False)
    preferences.save()

    return Response({"message": "Preferences updated"}, status=status.HTTP_200_OK)


def notify_user_about_stock(user):
    notification_pref = get_object_or_404(NotificationPreference, user=user)

    # Get the stock level (this is an example, adapt it to your system)
    stock = StockItem.objects.filter(user=user).first()
    
    if stock and StockItem.quantity < 10:  # If stock is low
        message = f"Hello {user.username}, your stock is running low!"

        # Send email if the user has opted in
        if notification_pref.receive_email and notification_pref.email:
            send_email(notification_pref.email, "Low Stock Alert", message)

        # Send SMS if the user has opted in
        if notification_pref.receive_sms and notification_pref.phone_number:
            send_sms(notification_pref.phone_number, message)

        # Phone call logic can be added here if needed (using Twilio for calls)
        # You can also integrate push notifications similarly.


def check_stock_view(request):
    stock_items = StockItem.objects.all()

    for stock in stock_items:
        if StockItem.quantity < 10:  # Assume 10 is the threshold for low stock
            notify_user_about_stock(stock.user)

    return render(request, 'stock_list.html', {'stock_items': stock_items})


@api_view(['GET'])
# def fetch_notifications(request):
#     user = request.user
#     notifications = Notification.objects.filter(user=user, is_read=False)
    
#     notifications_data = [
#         {
#             'id': notification.id,
#             'message': notification.message,
#             'created_at': notification.created_at,
#             'is_read': notification.is_read,
#         }
#         for notification in notifications
#     ]
    
#     return JsonResponse({'notifications': notifications_data})
def fetch_notifications(request):
    # Fetch unread notifications for the logged-in admin
    user = User.objects.get(is_superuser=True)
    notifications = Notification.objects.filter(user=user, is_read=False)  # Filter on is_read field
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'notifications': serializer.data})

@api_view(['POST'])
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return Response({'success': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)
    



