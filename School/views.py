import os
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from School.models import Birthday, Carousel, InsideSchool, Notice, SchoolMessage, brandInformation, brandLogo, menu, menuView, subMenu, PhotoGallery, Profile
from django.core.mail import send_mail
from random import randint


def Login(request):
    if request.method == "POST":

        email = request.POST.get("email").strip()
        password = request.POST.get("password")

        user_model = get_user_model()

        try:
            user_obj = user_model.objects.get(email__iexact=email)
        except user_model.DoesNotExist:
            return render(request, "Home/index.html", {
                "error": "Invalid Email or Password"
            })

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user is None:
            return render(request, "Home/index.html", {
                "error": "Invalid Email or Password"
            })

        otp = str(randint(100000,999999))

        request.session["otp"] = otp
        request.session["user_id"] = user.id

        send_mail(
            subject="School Management System - Login OTP",
            message=f"""
            Dear User,  
            Your One-Time Password (OTP) for login is:{otp}
            This OTP is valid for 5 minutes.

            Please do not share this OTP with anyone.

            Regards,
            School Management System
            """,

            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False
        )

        return render(request, "Home/index.html", {
            "show_otp_modal": True,
            "email": email
        })

    return render(request,"Admin/login.html")

def VerifyOTP(request):

    if request.method == "POST":

        otp = request.POST.get("otp")
        session_otp = request.session.get("otp")

        if session_otp is None:
            return render(request, "Home/index.html", {
                "error": "OTP session expired. Please login again."
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
    crousels = Carousel.objects.all()
    messages_list = SchoolMessage.objects.all().order_by("-id")[:2]
    notices = Notice.objects.filter(status=True).order_by('-publish_date', '-id')[:5]
    events = InsideSchool.objects.filter(category="Events", status=True).order_by("-id")[:3]
    achievements = InsideSchool.objects.filter(category="Achievements", status=True).order_by("-id")[:3]
    awareness = InsideSchool.objects.filter(category="Social Awareness", status=True).order_by("-id")[:3]
    birthday_list = list(Birthday.objects.filter(status=True).order_by('dob', 'student_name'))
    birthday_groups = [birthday_list[i:i+4] for i in range(0, len(birthday_list), 4)]
    gallerys = PhotoGallery.objects.all()

    return render(request, 'Home/index.html', {
        'crousel_list': crousels,
        'notice_list': notices,
        'messages_list': messages_list,
        'events': events,
        'achievements': achievements,
        'awareness': awareness,
        'birthdays': birthday_list,
        'birthday_groups': birthday_groups,
        'gallery': gallerys
    })

def menu_detail(request, id):
    menus = menu.objects.all()
    menu_id = get_object_or_404(menu, id=id)
    menu_view = menuView.objects.filter(menu=menu_id).first()
    return render(request,"Home/menu_detail.html",{"menu_view": menu_view})

def submenu_detail(request, submenu_id):
    submenu = get_object_or_404(subMenu, id=submenu_id)
    menu_view = menuView.objects.filter(submenu=submenu).first()
    
    return render(request, 'Home/submenu_detail.html', {
        'menu_view': menu_view,
    })

#===================================================================
#======================== Admin views ==============================
#===================================================================
@login_required
def dashboard(request):
    total_banners = Carousel.objects.count()
    total_notices = Notice.objects.count()
    total_messages = SchoolMessage.objects.count()
    total_activities = InsideSchool.objects.count()
    total_birthdays = Birthday.objects.count()
    total_gallery_items = PhotoGallery.objects.count()
    total_profiles = Profile.objects.count()

    recent_notices = Notice.objects.order_by('-publish_date', '-id')[:6]
    recent_activities = InsideSchool.objects.order_by('-create_date', '-id')[:6]
    recent_updates_count = recent_notices.count() + recent_activities.count()

    return render(request, 'Admin/index.html', {
        'total_banners': total_banners,
        'total_notices': total_notices,
        'total_messages': total_messages,
        'total_activities': total_activities,
        'total_birthdays': total_birthdays,
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
    crousels = Carousel.objects.all()
    if request.method == "POST":
        title = request.POST.get("title")
        image = request.FILES.get("image")
        status = request.POST.get("status")

        if title and image:
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            carousel = Carousel(title=title, image=image, status=status)
            carousel.save()
            messages.success(request, 'Carousel added successfully.')
            return redirect('crousel')
    return render(request, 'Admin/crousel_list.html', {'crousel_list': crousels})

def add_menu(request):
    menus = menu.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        sequence = request.POST.get("sequence")
        menu_obj = menu(name=name, sequence=sequence)
        menu_obj.save()

    return render(request, 'Admin/menu_list.html', {'menu_list': menus})

def add_submenu(request):
    menus = menu.objects.all()
    submenus = subMenu.objects.all()
    if request.method == "POST":
        menu_id = request.POST.get("menu_id")
        name = request.POST.get("name")

        if not menu_id:
            messages.error(request, 'Please select a parent menu before adding a submenu.')
            return render(request, 'Admin/submenu_list.html', {'menu_list': menus, 'submenu_list': submenus})

        if not name:
            messages.error(request, 'Please enter a submenu name.')
            return render(request, 'Admin/submenu_list.html', {'menu_list': menus, 'submenu_list': submenus})

        submenu_obj = subMenu(menu_id=menu_id, name=name)
        submenu_obj.save()
        messages.success(request, 'Submenu added successfully.')

    return render(request, 'Admin/submenu_list.html', {'menu_list': menus, 'submenu_list': submenus})

def list_menu_view(request):
    views = menuView.objects.all()
    return render(request, 'Admin/menu_view_list.html',{'menu_views': views})

def add_menu_view(request):
    menus = menu.objects.all()
    submenus = subMenu.objects.all()
    if request.method == "POST":
        menu_id = request.POST.get("menu")
        submenu_id = request.POST.get("submenu")
        pagetitle = request.POST.get("pagetitle")
        pagecontent = request.POST.get("pagecontent")

        if not menu_id and not submenu_id:
            messages.error(request, "Please select either a menu or a submenu.")
            return redirect('add-menu-view')

        if menu_id and submenu_id:
            messages.error(request, "Please select only one: either a menu or a submenu.")
            return redirect('add-menu-view')

        menu_view_obj = menuView(
            menu_id=menu_id if menu_id else None,
            submenu_id=submenu_id if submenu_id else None,
            pagetitle=pagetitle,
            pagecontent=pagecontent
        )
        try:
            menu_view_obj.save()
            messages.success(request, "Menu view added successfully.")
            return redirect('menu-view-list')
        except ValidationError as e:
            messages.error(request, f"Error: {e.message_dict}")
    return render(request, 'Admin/add_menu_view.html', {'menus': menus, 'submenus': submenus})

# Notice List
def Notice_list(request):
    notice_list = Notice.objects.all().order_by("-id")
    return render(request, "Admin/notice_list.html", {
        "notice_list": notice_list
    })


# Add Notice
def Add_notice(request):
    if request.method == "POST":

        title = request.POST.get("title")
        image = request.FILES.get("image")
        status = True if request.POST.get("status") else False

        Notice.objects.create(
            title=title,
            image=image,
            status=status
        )

        messages.success(request, "Notice Added Successfully")

    return redirect("notice_list")


# Edit Notice
def Edit_notice(request, id):

    notice = get_object_or_404(Notice, id=id)

    if request.method == "POST":

        notice.title = request.POST.get("title")

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

def Inside_School(request):

    if request.method == "POST":

        category = request.POST.get("category")
        title = request.POST.get("title")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        read_more_link = request.POST.get("read_more_link")
        status = True if request.POST.get("status") else False

        InsideSchool.objects.create(
            category=category,
            title=title,
            image=image,
            description=description,
            read_more_link=read_more_link,
            status=status
        )

        messages.success(request, "Inside School Added Successfully")

        return redirect("inside_school")

    inside_school = InsideSchool.objects.all().order_by("-id")

    return render(
        request,
        "Admin/inside_school.html",
        {
            "inside_school": inside_school
        }
    )

def Edit_Inside_School(request, id):

    inside = get_object_or_404(InsideSchool, id=id)

    if request.method == "POST":

        inside.category = request.POST.get("category")
        inside.title = request.POST.get("title")
        inside.description = request.POST.get("description")
        inside.read_more_link = request.POST.get("read_more_link")

        if request.FILES.get("image"):
            inside.image = request.FILES.get("image")

        inside.status = True if request.POST.get("status") else False

        inside.save()

        messages.success(request, "Record Updated Successfully")

    return redirect("inside_school")

def Delete_Inside_School(request, id):

    inside = get_object_or_404(InsideSchool, id=id)

    inside.delete()

    messages.success(request, "Record Deleted Successfully")

    return redirect("inside_school")

def Birthday_View(request):

    if request.method == "POST":

        Birthday.objects.create(
            student_name=request.POST.get("student_name"),
            father_name=request.POST.get("father_name"),
            class_name=request.POST.get("class_name"),
            section=request.POST.get("section"),
            dob=request.POST.get("dob"),
            image=request.FILES.get("image"),
            status=True if request.POST.get("status") else False
        )

        messages.success(request, "Birthday Added Successfully")
        return redirect("birthday")

    birthday_list = Birthday.objects.all().order_by("-id")

    return render(
        request,
        "Admin/birthday.html",
        {
            "birthday_list": birthday_list
        }
    )


def Edit_Birthday(request, id):

    birthday = get_object_or_404(Birthday, id=id)

    if request.method == "POST":

        birthday.student_name = request.POST.get("student_name")
        birthday.father_name = request.POST.get("father_name")
        birthday.class_name = request.POST.get("class_name")
        birthday.section = request.POST.get("section")
        birthday.dob = request.POST.get("dob")

        birthday.status = True if request.POST.get("status") else False

        if request.FILES.get("image"):
            birthday.image = request.FILES.get("image")

        birthday.save()

        messages.success(request, "Birthday Updated Successfully")

        return redirect("birthday")


def Delete_Birthday(request, id):

    birthday = get_object_or_404(Birthday, id=id)

    birthday.delete()

    messages.success(request, "Birthday Deleted Successfully")

    return redirect("birthday")

def Photo_Gallery(request):

    if request.method == "POST":

        PhotoGallery.objects.create(
            title=request.POST.get("title"),
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

        gallery.title = request.POST.get("title")

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
