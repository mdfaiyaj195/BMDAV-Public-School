from .models import brandInformation, brandLogo, menu


def brand_info(request):
    brand = brandInformation.objects.first()
    logo = brandLogo.objects.first()
    menu_list = menu.objects.exclude(name__iexact='Home').order_by('sequence', 'id')
    return {'brand': brand, 'logo': logo, 'menu_list': menu_list}

