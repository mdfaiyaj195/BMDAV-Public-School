from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=100, default="admin")
    status = models.CharField(max_length=50, default="Active")
    profile = models.ImageField(upload_to="admin_profile/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class brandInformation(models.Model):
    brand_name = models.CharField(max_length=255,default="")
    about_brand = models.TextField()
    primary_phone = models.BigIntegerField(default=0)
    secondary_phone = models.BigIntegerField(default=0)
    email = models.EmailField(default="")
    address = models.TextField(default="")
    fb_link = models.TextField(default="")
    yt_link = models.TextField(default="")
    inst_link = models.TextField(default="")
    twitter_link = models.TextField(default="")
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name 
     
class brandLogo(models.Model):   #Done
    logo = models.ImageField(upload_to="Brand_Logo",default="")
    favicon = models.ImageField(upload_to="Brand_Logo",default="")
    create_date = models.DateTimeField(auto_now_add=True)


class Carousel(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="crousel",default="")
    status = models.CharField(max_length=50, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)

class Notice(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.FileField(upload_to="notices/", blank=True, null=True)
    publish_date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class SchoolMessage(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="messages/")
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Event(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="inside_school/")
    description = models.TextField()
    read_more_link = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)

    
class PhotoGallery(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="gallery/")
    status = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title