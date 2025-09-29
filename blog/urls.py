"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import render
from django.conf.urls import handler400, handler403, handler404, handler500
from post.sitemaps import PostSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'posts': PostSitemap,
}


def error_view(request, exception=None, code=500, message="Server error"):
    return render(request, 'errors/error_page.html', {'code': code, 'message': message}, status=code)


def error_400(request, exception):
    return error_view(request, exception, 400, "Bad Request")


def error_403(request, exception):
    return error_view(request, exception, 403, "Forbidden")


def error_404(request, exception):
    return error_view(request, exception, 404, "Page not found")


def error_500(request):
    return error_view(request, None, 500, "Server error")


urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('post.urls')),
                  path('accounts/', include('accounts.urls')),
                  path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
                  path('__debug__/', include('debug_toolbar.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500
