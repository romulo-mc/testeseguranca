import easyocr
import os
import re
from datetime import datetime
from PIL import Image, ImageDraw
import cv2 as cv

path_image = "C://Users//NZ366ES//OneDrive - EY//Documents//Projeto Interno - Ciencia de Dados//EasyOCR//pictures//cnh"

PATTERN_NOME = r"(?im)NOME\s*(?P<nome>.+)\s*DOC."
PATTERN_RG = r"(?im)EMISSOR[A-Z\s]*(?P<rg>\d{6,9})\s*(?P<org_emissor>\w+)\s*CPF"
# PATTERN_CPF = r"(?im)(?P<cpf>\d{3}[\s|.]\d{3}[\s|.]\d{3}[\s|-]\d{2})"
PATTERN_CPF = r"(?im)CPF.+(?P<cpf>\d{3}[\s|.]*\d{3}[\s|.]*\d{3}[\s|-]*\d{2}).+FILIA"
PATTERN_DTNASCIMENTO = r"(?im)(?P<dt_nascimento>\d{2}/\d{2}/\d{4})\s?FILIAÇÃO"
PATTERN_FILIACAO = r"(?im)FILIAÇÃO(?P<filiacao>.+)\s?PERMISSÃO"
PATTERN_NUM_REGISTRO = r"(?im)(?P<no_registro>\d{11})"
PATTERN_CAT_HAB = r"(?im)CAT. HAB..+(?P<categoria>\bAB\b|\bA\b|\bB\b|\bC\b|\bD\b|\bE\b)\s+"
PATTERN_VALIDADE_1A_HABILITACAO = r"(?im)VALIDADE[A-Z0-9ÇÃª\s]+(?P<validade>\d{2}/\d{2}/\d{4})\s?" \
                                  r"(?P<primeirahabilitacao>\d{2}/\d{2}/\d{4})"
PATTERN_STARTS_WITH_VALIDADE = r"(?im)VALIDADE.+"

dict_campos = {}
"""
Pelos testes realizados, o EasyOCR le as imagens de cima pra baixo e de esquerda para direita


O resultado ele armazena em uma lista de palavras isoladas

O modo paragraph está ligado para que o programe agrupe em blocos de palavras. 

Em fotos de baixa resolução, o EasyOCR tem dificuldade de detectar as palavras chaves para o reconhecimento de 
campos (NOME, DOC. IDENTIDADE)

"""
def draw_boxes(image, bounds, color='red', width=5):
    """
    Desenha borda das fotos de onde ele detectou texto na cnh
    :param image:
    :param bounds:
    :param color:
    :param width:
    :return:
    """
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
    return image

def exporta_cnh_texto(texto, nome_arquivo):
    with open(f'{nome_arquivo}.txt', 'w', encoding="ISO-8859-1") as f:
        f.writelines(texto)

def ajeitar_cpf(cpf):
    #PATTERN_CPF_GROUPED = r"(?im)(?P<PtUm>\d{3})[\s|.](?P<PtDois>\d{3})[\s|.](?P<PtTres>\d{3})[\s|-](?P<digitoVerif>\d{2})"
    PATTERN_CPF_GROUPED = r"(?im)CPF.+(?P<PtUm>\d{3})[\s|.]*(?P<PtDois>\d{3})[\s|.]*(?P<PtTres>\d{3})[\s|-]*(?P<digitoVerif>\d{2}).+FILIA"
    PATTERN_CPF_FIXED = r"\g<PtUm>.\g<PtDois>.\g<PtTres>-\g<digitoVerif>"
    return re.sub(PATTERN_CPF_GROUPED, PATTERN_CPF_FIXED, cpf)

def extrair_rg_org_emissor(match):
    for key, value in match.groupdict().items():
        print(f"{key}:{value}")
        dict_campos[key] = value

def extrair_validade_1a_habilitacao(value):
    pattern_data = r"(?im)\d{2}/\d{2}/\d{4}"
    lista_datas = []

    try:
        match_iter = re.finditer(pattern_data, value)
        for match in match_iter:
            lista_datas.append(match.group(0).strip(' '))

        primeira_data = datetime.strptime(lista_datas[0], "%d/%m/%Y")
        segunda_data = datetime.strptime(lista_datas[1], "%d/%m/%Y")

        if primeira_data < segunda_data:
            print(f"validade:{lista_datas[1]}")
            print(f"primeirahabilitacao:{lista_datas[0]}")
            dict_campos["validade"] = lista_datas[1]
            dict_campos["primeirahabilitacao"] = lista_datas[0]
        else:
            print(f"validade:{lista_datas[0]}")
            print(f"primeirahabilitacao:{lista_datas[1]}")
            dict_campos["validade"] = lista_datas[0]
            dict_campos["primeirahabilitacao"] = lista_datas[1]
    except AttributeError:
        return ""

def limpa_nome(value):
    """
    :param value:
    :return: texto com letras minusculas, acentos e caracteres especiais removidos (erros de leitura do EasyOCR).
    Válido para campos que só aceita A-Z maiúsculos.
    """
    new_value = re.sub(r"[0-9a-z:;.çáéíóúâêîôû!@#$%^&*()]+", "", value)
    new_value = re.sub(r"\s{2,}", " ", new_value)
    return new_value

def scanner_carteira(texto):

    list_patterns = [PATTERN_NOME, PATTERN_RG, PATTERN_CPF,
                     PATTERN_FILIACAO, PATTERN_DTNASCIMENTO,
                     PATTERN_NUM_REGISTRO, PATTERN_CAT_HAB]

    # O código abaixo vai iterar por cada padrão representando um campo da
    # carteira de habilitação. Se encontrar match, ele vai imprimir o valor.
    for cada_pattern in list_patterns:
        match_iter = re.finditer(cada_pattern, texto)

        for match in match_iter:
            for key, value in match.groupdict().items():
                if key == "cpf":
                    print(f"{key}:{ajeitar_cpf(value)}")
                    dict_campos[key] = ajeitar_cpf(value)
                    break
                elif (key == "nome") or (key == "filiacao"):
                    print(f"{key}:{limpa_nome(value)}")
                    dict_campos[key] = limpa_nome(value)
                    break
                elif (key == "rg"):
                    extrair_rg_org_emissor(match)
                elif key in ["dt_nascimento", "no_registro", "categoria"]:
                    print(f"{key}:{value}")
                    dict_campos[key] = value
                    break

    # A funcao extrair_validade_1a_habilitacao capturar data de validade e de 1a habilitação separadamente.
    # De acordo com a leitura das carteiras de exemplo, nao havia um padrao definido de scanner
    # na hora de capturar essas duas datas a não ser que as datas vinham após a palavra VALIDADE.
    # Logo, o programa vai definir qual das duas datas após a palavra VALIDADE é a expiração da carteira
    # e qual data é a da 1a habilitação tirada.
    try:
        texto_validade = re.search(PATTERN_STARTS_WITH_VALIDADE, texto)
        extrair_validade_1a_habilitacao(texto_validade.group(0))
    except AttributeError:
        print("Validade não encontrada!")



    print("Leitura da carteira concluida!")


def converter_letras_vermelhas(path_imagem):
    """
    Este programa converte as letras escritas em vermelho para preto para melhor reconhecimento do EasyOCR
    :param path_imagem:
    :return: img - Imagem convertida com as letras pretas no lugar das vermelhas na CNH
    """
    print("Começando o processamento da carteira...")
    img = Image.open(path_imagem)
    img = img.convert("RGB")

    d = img.getdata()

    new_image = []

    # item = pixel em rgb Ex: (19,26,55)
    # d = array de pixels rgb
    for item in d:

        # change all red pixels to yellow
        # item[0] = R; item[1] = G; item[2] = B
        if (item[0] in list(range(120, 256))) and (item[1] in list(range(0, 140))) and (item[2] in list(range(0, 140))):
            new_image.append((0, 0, 0))
        else:
            new_image.append(item)

    # update image data
    img.putdata(new_image)
    img.save("imagem_tratada.jpg")
    print("Carteira convertida com sucesso!")
    return new_image

def tratamento_carteira(path_cnh):
    """
    Este programa cria uma máscara da carteira em tom de cinza, eliminando o fundo da carteira
    para deixar os textos mais limpos utilizando adaptive threshold
    :param path_imagem:
    :return: img - Imagem convertida com as letras pretas no lugar das vermelhas na CNH
    """
    print("Começando o tratamento da imagem da carteira...")
    img = cv.imread(path_cnh)

    # Extrai as letras
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (7, 7), 0)

    mask = cv.adaptiveThreshold(blurred,
                                255,
                                cv.ADAPTIVE_THRESH_MEAN_C,
                                cv.THRESH_BINARY,
                                31,
                                10)

    output_path = os.getcwd() + "\\mask.jpg"
    cv.imwrite(output_path, mask)

    print("Carteira tratada com sucesso!")
    return output_path


# i = 1
# for cada_cnh in os.listdir(path_image):
#     if cada_cnh.endswith((".jpeg", ".jpg", ".png")):
#         path = path_image + f"//{cada_cnh}"
#         img_tratada = converter_letras_vermelhas(path)
#
#         # Desenha a borda
#         reader = easyocr.Reader(["pt"])
#         borda = reader.readtext("./imagem_tratada.jpg", detail=1, paragraph=False)
#         img = Image.open("./imagem_tratada.jpg")
#         cnh_with_border = draw_boxes(img, borda)
#         cnh_with_border.show()
#
#         result = reader.readtext("./imagem_tratada.jpg", detail=0, paragraph=False) # aproveitar o resultado da borda
#         result_text = ' '.join(result)
#         print(f"Leitura da carteira:\n{result_text}")
#
#         exporta_cnh_texto(result, cada_cnh)
#
#         print(f"\nDados da carteira {i}:")
#         scanner_carteira(result_text)
#         i += 1
# print("Todas as CNHs foram lidas com sucesso")
