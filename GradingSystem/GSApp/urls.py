from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import home,plaigiarism,pdf_to_img,modified_omr

urlpatterns =[
    path('',home.home,name='home'),
    path('plaigiarism/',plaigiarism.plaigiarism,name='plaigiarism'),
    path('pdf2img/',pdf_to_img.pdf_to_img,name='pdf2img'),
    path('modified/',modified_omr.modified,name='modified'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)