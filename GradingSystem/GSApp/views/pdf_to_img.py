from django.shortcuts import render
from GSApp.models import GSpdf2img
from pdf2image import convert_from_path
from django.conf import settings
from django.templatetags.static import static
import os
from PIL import Image

def pdf_to_img(request):
    if request.method == 'POST':
        pdf = request.FILES['pdf']
        pdf2img = GSpdf2img(pdf_2_img=pdf)
        a = pdf2img.pdf_2_img
        pdf2img.save()
        path = settings.MEDIA_ROOT
        images = convert_from_path(f"{path}/{a}")
        
        for i in range(len(images)):
          # with open(f"C:\\Users\\MEHBOOB\\Desktop\\GradingSytem1\\GradingSystem\\GSApp\\static\\images\\ {'page'+ str(i)+ '.jpg','JPEG'}","ab") as f :
            # f.write(images[i])
        # Save pages as images in the pdf
          # img_name = 
          # path = "..//static//images//"
          path1 = ".//media//images"
          # images[i].save(f"C:\\Users\\MEHBOOB\\Desktop\\GradingSytem1\\GradingSystem\\GSApp\\static\\images\\{aaa} ", "JPEG")
          images[i].save(f"{path1}//{'page'+ str(i) +'.jpg'} ", "JPEG")

          # f"C:\\Users\\MEHBOOB\\Desktop\\GradingSytem1\\GradingSystem\\GSApp\\static\\images\\{ images[i] 'page'+ str(i)+ '.jpg','JPEG'}"
    return render(request,'pdf_to_img.html')