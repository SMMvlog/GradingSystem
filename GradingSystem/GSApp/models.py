from django.db import models

class GSpdf(models.Model):
    pdf = models.FileField(upload_to='pdf')

class GSpdf2img(models.Model):
    pdf_2_img = models.FileField(upload_to='pdf2img')
    img = models.FileField(upload_to='pdf2img/images',null=True, blank=True)

    

