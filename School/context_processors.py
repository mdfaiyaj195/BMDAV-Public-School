from .models import brandInformation, brandLogo


def brand_info(request):
    brand = brandInformation.objects.first()
    logo = brandLogo.objects.first()
    return {'brand': brand, 'logo': logo}

