Django Coding Challenge
=======================

This challenge is designed to test your Django and Python skills.

Requirements
============

- Completed using Python v3.10 and all code must be annotated with type hints from the standard library `typing` module.
- Runs on docker and the application can be started with a single command `docker-compose up`
- The running application can be reached in the browser at *[docker host]:8080*
- The application is delivered with a sufficient admin reachable at *[docker host]:8080/admin*
- Change the database to use mariadb instead of postgress
- Make the django endpoints using https://www.django-rest-framework.org/ and explain why you use the path you choose.
- Delivered as a public fork of this GitHub repository
- **Show us your work** through your commit history
- Unit test the django endpoints.
- Add the sample data you use.

Scenario
========

You are implementing part of an SDK licensing application used to permit clients to download the company's proprietary software. The sales team needs a feature which automatically notifies them when one of their client's licenses will expire (and thus prevent the client from using the associated package).

Task
====

A bare bones Django project is provided in the *license_portal* directory. Within the `licenses` application implement an email sending mechanism to notify the admin point of contact `licenses.Client.admin_poc` of their clients license `licenses.License` expiration times. The message must be sent to a clients admin point of contact only if the following conditions are met:

1) The client has licenses which expire in exactly 4 months
2) The client has licenses which expire within a month and today is monday
3) The client has licenses which expire within a week
4) All of the above

The email body must consist of a list of all a client's licenses which meet the above conditions and emails must only include details for a single client (e.g. a separate email for each client). The expiring licenses in the email body must include:

- license id
- license type
- name of the package
- expiration date
- poc information of the client (name and email address)

This job must be trigger-able via a REST API request without authentication or csrf validation and must include a summary of notifications sent since the application started on the homepage.

Implement a logging mechanism that logs whenever an email is sent. This should have its own table and must log:
- When the email was sent
- License id

Add a endpoint that shows the most recent X emails sent where x is the provided number.



_Tip:_ Use django's builtin `django.core.mail.backends.locmem.EmailBackend`

_Bonus:_ Make a simple react frontend that shows the licenes and the logs. Using celery would also be a plus.

Restrictions
============

None! Use whatever tools / third party libraries you feel are necessary to complete the task.

Fork of: https://github.com/castlabs/django-coding-challenge

Guides
======

To create the root user run `docker-compose` as follows: 
```
docker-compose run license-server python manage.py createsuperuser
```
