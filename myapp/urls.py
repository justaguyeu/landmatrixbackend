from django.urls import path
from .views import AvailableStockItemsView, AvailableStockItemsView2, ChangePasswordView, DataEntryListCreateView, DebtEntryViewSet, MonthlyReportView, MonthlyReportView2, RestockView, StockItemListCreateView, StockItemDetailView, StockItemListCreateView2, StockItemListCreateView2a, StockItemListCreateViewa, StockReportView, StockReportView2, UserDeleteView, UserEntryViewSet, UserEntryViewSet2, UserEntryViewSet2a, UserEntryViewSetExpense, UserEntryViewSetExpensea, UserEntryViewSetOutofstock, UserEntryViewSeta, UserListCreateView, WeeklyReportView, YearlyReportView, get_notifications, update_preferences
from myapp import views

urlpatterns = [
    # path('data/', DataEntryListCreateView.as_view(), name='data-entry'),
    path('data/monthly/', MonthlyReportView.as_view(), name='monthly-report'),
    path('data/weekly/', WeeklyReportView.as_view(), name='monthly-report'),
    path('data/monthly2/', MonthlyReportView2.as_view(), name='monthly-report'),
    path('api/stock/report/', StockReportView.as_view(), name='stock-report'),
    path('api/stock/report2/', StockReportView2.as_view(), name='stock-report'),
    path('api/stock/', StockItemListCreateView.as_view(), name='stock-list-create'),
    path('api/stock2/', StockItemListCreateView2.as_view(), name='stock-list-create'),

    


    path('api/notifications/', views.fetch_notifications, name='fetch_notifications'),
    path('api/notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('api/update-preferences/', update_preferences, name='update_preferences'),

    path('data/yearly/', YearlyReportView.as_view(), name='monthly-report'),

    
    path('debts/', DebtEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='debt-list-create'),
    path('debts/<int:pk>/', DebtEntryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='debt-list-create'),    
    path('api/stock/<int:pk>/', StockItemDetailView.as_view(), name='stock-detail'),
    path('api/restock/', RestockView.as_view(), name='restock'),
    path('data/', UserEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
      
    path('data2/', UserEntryViewSet2.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataa/', UserEntryViewSeta.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataa/<int:pk>/', UserEntryViewSeta.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentrya-detail'),


    path('data2a/', UserEntryViewSet2a.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataexpensea/', UserEntryViewSetExpensea.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataexpense/', UserEntryViewSetExpense.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataexpense/<int:pk>/', UserEntryViewSetExpense.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-list-create'),
    path('data/accidentalbanner', UserEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('available-stock/', AvailableStockItemsView.as_view(), name='available-stock'),
    path('available-stock2/', AvailableStockItemsView2.as_view(), name='available-stock'),


    path('dataoutofstock/', UserEntryViewSetOutofstock.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
    path('dataoutofstock/<int:pk>/', UserEntryViewSetOutofstock.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-list-create'),

    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
   
]
