# sales_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenRefreshView
from myapp import views
from myapp.views import AvailableStockItemsView, AvailableStockItemsView2, DataEntryListCreateView, CustomTokenObtainPairView, DebtEntryViewSet, MonthlyReportView, MonthlyReportView2, RestockView, StockItem2mainCreateView, StockItemDetailView, StockItemListCreateView, StockItemListCreateView2, StockItemListCreateView2a, StockItemListCreateViewa, StockReportView, StockReportView2, UserEntryViewSet, UserEntryViewSet2, UserEntryViewSet2a, UserEntryViewSetExpense, UserEntryViewSetExpensea, UserEntryViewSeta, WeeklyReportView, YearlyReportView, update_preferences


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/stock/report/', StockReportView.as_view(), name='stock-report'),
    path('api/stock/report2/', StockReportView2.as_view(), name='stock-report'),
    path('data/monthly/', MonthlyReportView.as_view(), name='monthly-report'),
    path('data/weekly/', WeeklyReportView.as_view(), name='monthly-report'),
    path('data/monthly2/', MonthlyReportView2.as_view(), name='monthly-report'),
    path('api/stock/', StockItemListCreateView.as_view(), name='stock-list-create'),

    path('api/stock2main/', StockItem2mainCreateView.as_view(), name='stock-list-create'),
    path('api/stock2main/<str:main_stock>/', views.get_substocks, name='get_substocks'),
    path('api/stock2/', StockItemListCreateView2.as_view(), name='stock-list-create'),
    
    path('api/data/<int:pk>/', UserEntryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-list-create'),
    path('api/data2/<int:pk>/', UserEntryViewSet2.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-list-create'),

    path('api/stock/<int:pk>/', StockItemDetailView.as_view(), name='stock-detail'),
    path('available-stock/', AvailableStockItemsView.as_view(), name='available-stock'),
    path('available-stock2/', AvailableStockItemsView2.as_view(), name='available-stock'),
    path('api/restock/', RestockView.as_view(), name='restock'),
    path('api/data/', UserEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('api/data2/', UserEntryViewSet2.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataexpense/', UserEntryViewSetExpense.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),

    path('data/yearly/', YearlyReportView.as_view(), name='monthly-report'),
    path('debts/', DebtEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='debt-list-create'),
    path('debts/<int:pk>/', DebtEntryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='debt-list-create'), 



    path('dataa/', UserEntryViewSeta.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('data2a/', UserEntryViewSet2a.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataexpensea/', UserEntryViewSetExpensea.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),

    path('api/stocka/', StockItemListCreateViewa.as_view(), name='stock-list-create'),
    path('api/stock2a/', StockItemListCreateView2a.as_view(), name='stock-list-create'),

    path('api/notifications/', views.fetch_notifications, name='fetch_notifications'),
    path('api/notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('api/update-preferences/', update_preferences, name='update_preferences'),

    
]


