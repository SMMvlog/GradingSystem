from django.contrib import admin
from .models import GSpdf,GSpdf2img

@admin.register(GSpdf)
class GSpdfAdmin(admin.ModelAdmin):
    list_display = ['id','pdf']

@admin.register(GSpdf2img)
class GSpdf2imgAdmin(admin.ModelAdmin):
    list_display = ['id','pdf_2_img']