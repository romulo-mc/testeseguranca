from PIL import Image

path = "C://Users//NZ366ES//OneDrive - EY//Documents//Projeto Interno - Ciencia de Dados//EasyOCR//pictures//cnh//cnh_teste3.jpg"

img = Image.open(path)
img = img.convert("RGB")

d = img.getdata()

new_image = []

# item = pixel em rgb Ex: (19,26,55)
# d = array de pixels rgb
for item in d:

    # change all red pixels to yellow
    # item[0] = R; item[1] = G; item[2] = B
    if (item[0] in list(range(140, 256))) and (item[1] in list(range(0, 140))) and (item[2] in list(range(0, 140))):
        new_image.append((0, 0, 0))
    else:
        new_image.append(item)

# update image data
img.putdata(new_image)

# save new image
img.save("cnh_teste4.jpg")