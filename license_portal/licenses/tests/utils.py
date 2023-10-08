from django.utils import timezone
from licenses.models import (
    Client,
    Package,
    LicenseType,
    License
)

def get_expiring_licenses_for(client: Client):
        lic1 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
        )
        lic2 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=30),
        )
        lic3 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=31*4),
        )
        return {lic1, lic2, lic3}

def parse_license_from(lic: License):
    return {
        "id": lic.id,
        "type": lic.get_license_type_display(),
        "package": lic.get_package_display(),
        "expiration_date": lic.expiration_datetime.strftime("%Y-%m-%d"),
    }

