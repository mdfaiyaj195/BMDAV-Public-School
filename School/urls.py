from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', TemplateView.as_view(template_name='Home/Menus/about.html'), name='about-school'),
    path('academics/', TemplateView.as_view(template_name='Home/Menus/academics.html'), name='academics'),
    path('admissions/', TemplateView.as_view(template_name='Home/Menus/admissions.html'), name='admissions'),
    path('facilities/', TemplateView.as_view(template_name='Home/Menus/facilities.html'), name='facilities'),
    path('student-life/', TemplateView.as_view(template_name='Home/Menus/student-life.html'), name='student-life'),
    path('gallery/', TemplateView.as_view(template_name='Home/Menus/media-gallery.html'), name='media-gallery'),
    path('information-centre/', TemplateView.as_view(template_name='Home/Menus/information-centre.html'), name='information-centre'),
    path('public-disclosure/', TemplateView.as_view(template_name='Home/Menus/public-disclosure.html'), name='public-disclosure'),
    path('contact/', views.contact, name='contact'),
    
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
    path('crousel/delete/<int:crousel_id>/', views.delete_crousel, name='delete_crousel'),

    path('school-message-list/', views.list_school_message, name='school-message-list'),
    path('school-message/', views.add_school_message, name='school-message'),
    path('school-message/delete/<int:id>/', views.delete_school_message, name='delete-school-message'),

    path("event-school/",views.Event_School,name="event_school"),
    path("event-school/edit/<int:id>/",views.Edit_Event_School,name="edit_event_school"),
    path("event-school/delete/<int:id>/",views.Delete_Event_School,name="delete_event_school"),

    path("photo-gallery/",views.Photo_Gallery, name="photo_gallery"),
    path("photo-gallery/edit/<int:id>/",views.Edit_Gallery,name="edit_gallery"),
    path("photo-gallery/delete/<int:id>/",views.Delete_Gallery,name="delete_gallery"),

]