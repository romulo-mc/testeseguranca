import easyocr
import numpy
import os
import cv2
from PIL import Image, ImageDraw, ImageFont

"""
De acordo com esse teste, a cor vermelha clara na Categoria de Habilitação atrapalha a leitura do 
EasyOCR. Na outra imagem na qual eu substitui a cor para preto no Gimp naquela região, fez com que
reconhecesse facilmente a categoria de habilitação. 

"""

def draw_boxes(image, bounds, color='yellow', width=2):
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
    return image

path_image = "C://Users//NZ366ES//OneDrive - EY//Documents//Projeto Interno - Ciencia de Dados//EasyOCR//pictures//outros"

i = 1
for picture in os.listdir(path_image):
    if picture.endswith((".jpeg", ".jpg", ".png")):
        path = path_image + f"//{picture}"
        reader = easyocr.Reader(["pt"])

        # Desenha a borda da imagem
        im = Image.open(path)
        border = reader.readtext(path, detail=1, paragraph=False)
        image_with_border = draw_boxes(im, border)
        image_with_border.show()

        # Transformo a imagem em escala de cinza para oferecer um maior contraste
        #img_grayscale = cv2.imread(path, 0) # The 0 flag is cv2.CV_LOAD_IMAGE_GRAYSCALE
        result = reader.readtext(path, detail=0, paragraph=False)
        print(f"Leitura da imagem {i}:\n{result}")
        i += 1

