import os
import logging
from smtplib import SMTPException
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError
from django.core.validators import EmailValidator
from School.models import Carousel, Event, Notice, SchoolMessage, brandInformation, brandLogo, PhotoGallery, Profile
from django.core.mail import send_mail
from random import randint

logger = logging.getLogger(__name__)


def Login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            return render(request, "Home/index.html", {
                "error": "Please enter your email and password.",
                "show_login_modal": True,
            })

        user_model = get_user_model()

        try:
            user_obj = user_model.objects.get(email__iexact=email)
        except user_model.DoesNotExist:
            return render(request, "Home/index.html", {
                "error": "Invalid Email or Password",
                "show_login_modal": True,
            })

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user is None:
            return render(request, "Home/index.html", {
                "error": "Invalid Email or Password",
                "show_login_modal": True,
            })

        otp = str(randint(100000,999999))

        request.session["otp"] = otp
        request.session["user_id"] = user.id

        # send_mail(
        #     subject="School Management System - Login OTP",
        #     message=f"""
        #     Dear User,  
        #     Your One-Time Password (OTP) for login is:{otp}
        #     This OTP is valid for 5 minutes.

        #     Please do not share this OTP with anyone.

        #     Regards,
        #     School Management System
        #     """,

        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[user.email],
        #     fail_silently=False
        # )

        return render(request, "Home/index.html", {
            "show_otp_modal": True,
            "show_otp": otp,
            "email": email
        })

    return render(request,"Admin/login.html")

def VerifyOTP(request):

    if request.method == "POST":

        otp = request.POST.get("otp")
        session_otp = request.session.get("otp")

        if session_otp is None:
            return render(request, "Home/index.html", {
                "error": "OTP session expired. Please login again.",
                "show_login_modal": True,
            })

        if otp == session_otp:

            user = get_user_model().objects.get(
                id=request.session.get("user_id")
            )

            login(request, user)

            request.session["username"] = user.username
            request.session["name"] = user.username
            request.session["email"] = user.email

            request.session.pop("otp", None)
            request.session.pop("user_id", None)

            return redirect("dashboard")

        return render(request, "Home/index.html", {
            "show_otp_modal": True,
            "error": "Invalid OTP"
        })

    return redirect("index")

def Logout(request):
    # clear session variables
    request.session.flush()
    return redirect('index')

#===================================================================
#======================== Home views ==============================
#===================================================================
def index(request):
    crousels = Carousel.objects.all().order_by("-id")[:6]
    messages_list = SchoolMessage.objects.all().order_by("-id")
    notices = Notice.objects.filter(status=True, category="notice").order_by('-publish_date', '-id')[:8]
    news = Notice.objects.filter(status=True, category="news").order_by('-publish_date', '-id')[:5]
    events = Event.objects.filter(status=True).order_by("-id")
    gallerys = PhotoGallery.objects.all()

    return render(request, 'Home/index.html', {
        'crousel_list': crousels,
        'notice_list': notices,
        'news_list': news,
        'messages_list': messages_list,
        'events': events,
        'gallery': gallerys
    })


def contact(request):
    contact_form = {
        "name": "",
        "email": "",
        "phone": "",
        "subject": "",
        "message": "",
    }

    if request.method == "POST":
        contact_form = {
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "subject": request.POST.get("subject", "").strip(),
            "message": request.POST.get("message", "").strip(),
        }
        if not contact_form["name"] or not contact_form["email"] or not contact_form["subject"] or not contact_form["message"]:
            messages.error(request, "Please complete all required fields.")
            return render(request, "Home/Menus/contact.html", {"contact_form": contact_form}, status=400)

        try:
            EmailValidator()(contact_form["email"])
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, "Home/Menus/contact.html", {"contact_form": contact_form}, status=400)

        if len(contact_form["name"]) > 150 or len(contact_form["email"]) > 254 or len(contact_form["subject"]) > 150 or len(contact_form["phone"]) > 30:
            messages.error(request, "Please check the length of the information entered.")
            return render(request, "Home/Menus/contact.html", {"contact_form": contact_form}, status=400)

        brand = brandInformation.objects.first()
        if not brand or not brand.email:
            messages.error(request, "The school email address is not available. Please contact the school by phone.")
            return render(request, "Home/Menus/contact.html", {"contact_form": contact_form}, status=503)

        email_body = "\n".join((
            f"Name: {contact_form['name']}",
            f"Email: {contact_form['email']}",
            f"Phone: {contact_form['phone'] or 'Not provided'}",
            f"Subject: {contact_form['subject']}",
            "",
            contact_form["message"],
        ))
        try:
            sent_count = send_mail(
                subject=f"Website enquiry: {contact_form['subject']}",
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[brand.email],
                fail_silently=False,
            )
        except (BadHeaderError, SMTPException, OSError):
            logger.exception("Unable to send a website contact enquiry.")
            messages.error(request, "Your enquiry could not be sent right now. Please contact the school by phone or email.")
            return render(request, "Home/Menus/contact.html", {"contact_form": contact_form}, status=503)

        if sent_count != 1:
            logger.error("The email backend did not send the website contact enquiry.")
            messages.error(request, "Your enquiry could not be sent right now. Please contact the school by phone or email.")
            return render(request, "Home/Menus/contact.html", {"contact_form": contact_form}, status=503)

        messages.success(request, "Thank you. Your enquiry has been sent to the school.")
        return redirect("contact")

    return render(request, "Home/Menus/contact.html", {"contact_form": contact_form})



#===================================================================
#======================== Admin views ==============================
#===================================================================
@login_required
def dashboard(request):
    total_banners = Carousel.objects.count()
    total_notices = Notice.objects.count()
    total_messages = SchoolMessage.objects.count()
    total_activities = Event.objects.count()
    total_gallery_items = PhotoGallery.objects.count()
    total_profiles = Profile.objects.count()

    recent_notices = Notice.objects.order_by('-publish_date', '-id')[:6]
    recent_activities = Event.objects.order_by('-create_date', '-id')[:6]
    recent_updates_count = recent_notices.count() + recent_activities.count()

    return render(request, 'Admin/index.html', {
        'total_banners': total_banners,
        'total_notices': total_notices,
        'total_messages': total_messages,
        'total_activities': total_activities,
        'total_gallery_items': total_gallery_items,
        'total_profiles': total_profiles,
        'recent_notices': recent_notices,
        'recent_activities': recent_activities,
        'recent_updates_count': recent_updates_count,
    })

def Brand_info(request):

    if request.method == "POST":
        brand_name = request.POST.get("brand_name")
        about_brand = request.POST.get("about_brand")
        primary_phone = request.POST.get("primary_phone")
        secondary_phone = request.POST.get("secondary_phone")
        email = request.POST.get("email")
        address = request.POST.get("address")
        fb_link = request.POST.get("fb_link")
        yt_link = request.POST.get("yt_link")
        inst_link = request.POST.get("inst_link")
        twitter_link = request.POST.get("twitter_link")

        # Create a new brandInformation object and save it to the database
        brand_info = brandInformation(
            brand_name=brand_name,
            about_brand=about_brand,
            primary_phone=primary_phone,
            secondary_phone=secondary_phone,
            email=email,
            address=address,
            fb_link=fb_link,
            yt_link=yt_link,
            inst_link=inst_link,
            twitter_link=twitter_link
        )
        brand_info.save()
    return render(request, 'Admin/add_brand_information.html')

def Brand_logo(request):

    if request.method == "POST":
        logo = request.FILES.get("logo")
        favicon = request.FILES.get("favicon")

        if logo is not None or favicon is not None:
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            brand_logo = brandLogo()
            if logo is not None:
                brand_logo.logo = logo
            if favicon is not None:
                brand_logo.favicon = favicon
            brand_logo.save()
            messages.success(request, 'Brand logo uploaded successfully.')
            return redirect('brand-logo')

    brand = brandLogo.objects.all().order_by('-create_date')
    return render(request, 'Admin/brand_logo.html', {'brand_logo': brand})

def delete_brand_logo(request, logo_id):
    try:
        brand_logo = brandLogo.objects.get(id=logo_id)
        brand_logo.delete()
    except brandLogo.DoesNotExist:
        pass  # Handle the case where the logo does not exist

    return redirect('brand-logo')

def add_crousel(request):
    crousels = Carousel.objects.all().order_by("-created_at")
    if request.method == "POST":
        title = request.POST.get("title", '').strip()
        image = request.FILES.get("image")
        status = request.POST.get("status", "Active")

        if len(title) > 100:
            messages.error(request, "Title must be 100 characters or fewer.")
        elif not image:
            messages.error(request, "Please select an image for the banner.")
        elif status not in ("Active", "Inactive"):
            messages.error(request, "Please select a valid banner status.")
        else:
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            Carousel.objects.create(
                title=title,
                image=image,
                status=status,
            )
            messages.success(request, 'Carousel added successfully.')
            return redirect('crousel')
    return render(request, 'Admin/crousel_list.html', {'crousel_list': crousels})

def delete_crousel(request, crousel_id):
    try:
        crousel = Carousel.objects.filter(id=crousel_id).first()
        if crousel:
            crousel.delete()
            messages.success(request, "Crousel delete Successfully")
            return redirect('crousel')
    except Carousel.DoesNotExist:
        messages.error(request, "Crousel not found.")
        return redirect('crousel')

# Notice List
def Notice_list(request):
    notice_list = Notice.objects.all().order_by("-id")
    return render(request, "Admin/notice_list.html", {
        "notice_list": notice_list
    })

# Add Notice
def Add_notice(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "notice")
        image = request.FILES.get("image")
        status = True if request.POST.get("status") else False

        if len(title) > 255:
            messages.error(request, "Title must be 255 characters or fewer.")
        elif category not in dict(Notice.CATEGORY_CHOICES):
            messages.error(request, "Please select a valid notice category.")
        else:
            Notice.objects.create(
                title=title or None,
                description=description,
                category=category,
                image=image,
                status=status
            )

            messages.success(request, "Notice Added Successfully")

    return redirect("notice_list")


# Edit Notice
def Edit_notice(request, id):

    notice = get_object_or_404(Notice, id=id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "notice")

        if len(title) > 255:
            messages.error(request, "Title must be 255 characters or fewer.")
            return redirect("notice_list")
        if category not in dict(Notice.CATEGORY_CHOICES):
            messages.error(request, "Please select a valid notice category.")
            return redirect("notice_list")

        notice.title = title or None
        notice.description = request.POST.get("description", "").strip()
        notice.category = category

        if request.FILES.get("image"):
            notice.image = request.FILES.get("image")

        notice.status = True if request.POST.get("status") else False

        notice.save()

        messages.success(request, "Notice Updated Successfully")

    return redirect("notice_list")


# Delete Notice
def Delete_notice(request, id):

    notice = get_object_or_404(Notice, id=id)

    notice.delete()

    messages.success(request, "Notice Deleted Successfully")

    return redirect("notice_list")


def download_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    if not notice.image:
        raise Http404("Notice file not found")

    response = FileResponse(notice.image.open('rb'), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(notice.image.name)}"'
    return response

def list_school_message(request):
    messages_list = SchoolMessage.objects.all().order_by('-create_date')
    return render(request, 'Admin/Schoolmessage.html', {'messages_list': messages_list})

def add_school_message(request):
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")
        message = request.POST.get("message")
        link = request.POST.get("link")

        SchoolMessage.objects.create(
            name=name,
            image=image,
            message=message,
            link=link
        )

        messages.success(request, "School Message Added Successfully")

    return redirect("school-message-list")

def delete_school_message(request, id):
    school_message = get_object_or_404(SchoolMessage, id=id)
    school_message.delete()
    messages.success(request, "School Message Deleted Successfully")
    return redirect("school-message-list")

def Event_School(request):
    if request.method == "POST":
        title = request.POST.get("title")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        read_more_link = request.POST.get("read_more_link")
        status = True if request.POST.get("status") else False

        Event.objects.create(
            title=title,
            image=image,
            description=description,
            read_more_link=read_more_link,
            status=status
        )

        messages.success(request, "Event Added Successfully")

        return redirect("event_school")

    inside_school = Event.objects.all().order_by("-id")

    return render(
        request,
        "Admin/inside_school.html",
        {
            "inside_school": inside_school
        }
    )

def Edit_Event_School(request, id):

    event = get_object_or_404(Event, id=id)

    if request.method == "POST":
        event.title = request.POST.get("title")
        event.description = request.POST.get("description")
        event.read_more_link = request.POST.get("read_more_link")

        if request.FILES.get("image"):
            event.image = request.FILES.get("image")

        event.status = True if request.POST.get("status") else False

        event.save()

        messages.success(request, "Record Updated Successfully")

    return redirect("event_school")

def Delete_Event_School(request, id):

    event = get_object_or_404(Event, id=id)

    event.delete()

    messages.success(request, "Record Deleted Successfully")

    return redirect("event_school")

def Photo_Gallery(request):

    if request.method == "POST":

        PhotoGallery.objects.create(
            title=request.POST.get("title", ''),
            image=request.FILES.get("image"),
            status=True if request.POST.get("status") else False
        )

        messages.success(request, "Photo Added Successfully")
        return redirect("photo_gallery")

    gallery_list = PhotoGallery.objects.all().order_by("-id")

    return render(
        request,
        "Admin/photo_gallery.html",
        {
            "gallery_list": gallery_list
        }
    )


def Edit_Gallery(request, id):

    gallery = get_object_or_404(PhotoGallery, id=id)

    if request.method == "POST":

        gallery.title = request.POST.get("title", '')

        gallery.status = True if request.POST.get("status") else False

        if request.FILES.get("image"):
            gallery.image = request.FILES.get("image")

        gallery.save()

        messages.success(request, "Gallery Updated Successfully")

        return redirect("photo_gallery")


def Delete_Gallery(request, id):

    gallery = get_object_or_404(PhotoGallery, id=id)

    gallery.delete()

    messages.success(request, "Gallery Deleted Successfully")

    return redirect("photo_gallery")
