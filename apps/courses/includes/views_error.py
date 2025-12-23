from django.shortcuts import render


# Custom error views
def custom_page_not_found(request, exception):
    context = {
        'error_code': 404,
        'error_title': 'Page Not Found',
        'error_message': 'Sorry, the page you are looking for does not exist or may have been moved.'
    }
    return render(request, 'error.html', context, status=404)


def custom_server_error(request):
    context = {
        'error_code': 500,
        'error_title': 'Server Error',
        'error_message': 'Sorry, something went wrong on our end. Please try again later.'
    }
    return render(request, 'error.html', context, status=500)


def custom_permission_denied(request, exception):
    context = {
        'error_code': 403,
        'error_title': 'Permission Denied',
        'error_message': 'Sorry, you do not have permission to access this page.'
    }
    return render(request, 'error.html', context, status=403)


def custom_bad_request(request, exception):
    context = {
        'error_code': 400,
        'error_title': 'Bad Request',
        'error_message': 'Sorry, your request could not be processed due to invalid syntax.'
    }
    return render(request, 'error.html', context, status=400)


def custom_method_not_allowed(request, exception):
    context = {
        'error_code': 405,
        'error_title': 'Method Not Allowed',
        'error_message': 'Sorry, the HTTP method used is not allowed for this URL.'
    }
    return render(request, 'error.html', context, status=405)


def custom_request_timeout(request, exception):
    context = {
        'error_code': 408,
        'error_title': 'Request Timeout',
        'error_message': 'Sorry, the server did not receive your request in time.'
    }
    return render(request, 'error.html', context, status=408)


def custom_too_many_requests(request, exception):
    context = {
        'error_code': 429,
        'error_title': 'Too Many Requests',
        'error_message': 'Sorry, you have sent too many requests in a short period of time. Please try again later.'
    }
    return render(request, 'error.html', context, status=429)


def custom_bad_gateway(request, exception):
    context = {
        'error_code': 502,
        'error_title': 'Bad Gateway',
        'error_message': 'Sorry, we received an invalid response from the upstream server.'
    }
    return render(request, 'error.html', context, status=502)


def custom_service_unavailable(request, exception):
    context = {
        'error_code': 503,
        'error_title': 'Service Unavailable',
        'error_message': 'Sorry, the server is temporarily unable to handle your request. Please try again later.'
    }
    return render(request, 'error.html', context, status=503)


def custom_gateway_timeout(request, exception):
    context = {
        'error_code': 504,
        'error_title': 'Gateway Timeout',
        'error_message': 'Sorry, the upstream server did not respond in time.'
    }
    return render(request, 'error.html', context, status=504)