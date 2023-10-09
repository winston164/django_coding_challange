from django.contrib.auth.models import User
from django.utils import timezone
from licenses.models import Client, License, LicenseType, Package


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
        expiration_datetime=timezone.now() + timezone.timedelta(days=31 * 4),
    )
    return {lic1, lic2, lic3}


def get_clients_for(user: User):
    return [
        Client.objects.create(
            client_name=f"client{n}-{user.username}",
            poc_contact_name=f"Client{n} Example",
            poc_contact_email=f"client{n}@email.com",
            admin_poc=user,
        )
        for n in range(3)
    ]


def parse_license_from(lic: License):
    return {
        "id": lic.id,
        "type": lic.get_license_type_display(),
        "package": lic.get_package_display(),
        "expiration_date": lic.expiration_datetime.strftime("%Y-%m-%d"),
    }


def get_email_body(topic: str, username: str, client: Client, licenses: [License]):
    def license_row(lic):
        return f"""
            <tr>
                <td>{ lic.id }</td>
                <td>{ lic.get_license_type_display() }</td>
                <td>{ lic.get_package_display() }</td>
                <td>{ lic.expiration_datetime.strftime("%Y-%m-%d") }</td>
            </tr>
            """

    parsed_licenses = [license_row(lic) for lic in licenses]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Generated with the help of ChatGPT-->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ topic }</title>
</head>
<body>
    <p>Hello { username },</p>

    <p>We wanted to inform you that some of your client { str(client) } licenses are about to expire soon. Please review the following details:</p>

    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Package</th>
                <th>Expiration Date</th>
            </tr>
        </thead>
        <tbody>
            {('').join(parsed_licenses)}
        </tbody>
    </table>

    <p>Please take the necessary actions to renew or update these licenses to ensure uninterrupted service for your client.</p>

    <p>Thank you for your attention to this matter.</p>

    <p>Sincerely,<br>
    Afiniteam</p>
</body>
</html>"""
