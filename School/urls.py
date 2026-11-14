from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("menu/<int:id>/", views.menu_detail, name="menu_detail"),
    path('submenu/<int:submenu_id>/', views.submenu_detail, name='submenu_detail'),
    
    #=============== Start Admin data urls =========================
    path('login/', views.Login, name='login'),
    path("verify-otp/", views.VerifyOTP, name="verify_otp"),
    path('logout/', views.Logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('brand-info/', views.Brand_info, name='brand-info'),

    path('brand-logo/', views.Brand_logo, name='brand-logo'),
    path('brand-logos/delete/<int:logo_id>/', views.delete_brand_logo, name='delete_brand_logo'),

    path("notice/", views.Notice_list, name="notice_list"),
    path("add-notice/", views.Add_notice, name="add_notice"),
    path("edit-notice/<int:id>/", views.Edit_notice, name="edit_notice"),
    path("delete-notice/<int:id>/", views.Delete_notice, name="delete_notice"),
    path("download-notice/<int:notice_id>/", views.download_notice, name="download_notice"),
    
    path('crousel/', views.add_crousel, name='crousel'),
    path('menu/', views.add_menu, name='menu'),
    path('submenu/', views.add_submenu, name='submenu'),

    path('school-message-list/', views.list_school_message, name='school-message-list'),
    path('school-message/', views.add_school_message, name='school-message'),
    path('school-message/delete/<int:id>/', views.delete_school_message, name='delete-school-message'),

    path("inside-school/",views.Inside_School,name="inside_school"),
    path("inside-school/edit/<int:id>/",views.Edit_Inside_School,name="edit_inside_school"),
    path("inside-school/delete/<int:id>/",views.Delete_Inside_School,name="delete_inside_school"),

    path("birthday/",views.Birthday_View,name="birthday"),
    path("birthday/edit/<int:id>/",views.Edit_Birthday,name="edit_birthday"),
    path("birthday/delete/<int:id>/",views.Delete_Birthday,name="delete_birthday"),

    path("photo-gallery/",views.Photo_Gallery, name="photo_gallery"),
    path("photo-gallery/edit/<int:id>/",views.Edit_Gallery,name="edit_gallery"),
    path("photo-gallery/delete/<int:id>/",views.Delete_Gallery,name="delete_gallery"),

    path('menu-view-list/', views.list_menu_view, name='menu-view-list'),
    path('add-menu-view/', views.add_menu_view, name='add-menu-view'),

]