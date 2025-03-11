import easyocr
import numpy
import os
import cv2

path_image = "C://Users//NZ366ES//OneDrive - EY//Documents//Projeto Interno - Ciencia de Dados//EasyOCR//pictures//cnh"

"""
Pelos testes realizados, o EasyOCR le as imagens de cima pra baixo e de esquerda para direita


O resultado ele armazena em uma lista de palavras isoladas

O modo paragraph está ligado para que o programe agrupe em blocos de palavras. 

Em fotos de baixa resolução, o EasyOCR tem dificuldade de detectar as palavras chaves para o reconhecimento de 
campos (NOME, DOC. IDENTIDADE)

"""

def exporta_cnh_texto(texto, nome_arquivo):
    with open(f'{nome_arquivo}.txt', 'w', encoding="utf-8") as f:
        f.writelines(texto)



i = 1
for cada_cnh in os.listdir(path_image):
    if cada_cnh.endswith((".jpeg", ".jpg", ".png")):
        path = path_image + f"//{cada_cnh}"
        reader = easyocr.Reader(["pt"])

        # Transformo a imagem em escala de cinza para oferecer um maior contraste
        #img_grayscale = cv2.imread(path, 0) # The 0 flag is cv2.CV_LOAD_IMAGE_GRAYSCALE
        result = reader.readtext(path, detail=0, paragraph=True)
        print(f"Leitura da carteira:\n{result}")

        exporta_cnh_texto(result, cada_cnh)

        print(f"\nDados da carteira {i}:")
        # Delimitando os campos
        for cada_pedaco in result:
            if "NOME" in cada_pedaco:
                nome = cada_pedaco[4:].rsplit("DOC.")[0].strip()
                # Caso ele detecte apenas 'NOME' no pedaço, significa que o EasyOCR separou o texto nome do
                # nome da pessoa quando dividiu os parágrafos. Neste caso, o nome do dono da carteira está no
                # próximo parágrafo de result.
                if (len(nome) == 0):
                    index_nome = result.index(cada_pedaco) + 1
                    nome = result[index_nome].rsplit("DOC.")[0].strip()
                print(f"Nome: {nome}")
            if "IDENTIDADE" in cada_pedaco:
                # A palavra que tem a identidade contém digitos e o órgao no formato
                # 123456789EMISSOR (começa com digitos e termina com letra)
                palavras = cada_pedaco.split(" ")
                for cada_palavra in palavras:
                    # Irei testar aqui se o primeiro caracter é digito e o último caracter é uma letra
                    if cada_palavra[0].isdigit() and cada_palavra[-1].isalpha():
                        digitos_identidade = "".join(filter(lambda x: x.isdigit(), cada_palavra))
                        orgao_emissor = "".join(filter(lambda x: x.isalpha(), cada_palavra))
                        print(f"Identidade: {digitos_identidade}\nÓrgão emissor: {orgao_emissor}")
            if ("DATA" in cada_pedaco) or ("NASCIMENTO" in cada_pedaco):
                palavras = cada_pedaco.split(" ")
                for cada_palavra in palavras:
                    if "/" in cada_palavra:
                        data_nascimento = cada_palavra
                        break
                print(f"Data de nascimento: {data_nascimento}")
            if "FILIAÇÃO" in cada_pedaco:
                filiacao = cada_pedaco[8:].strip().rsplit("PERMISSÃO")[0]
                print(f"Filiação: {filiacao}")
            if "REGISTRO" in cada_pedaco:
                palavras = cada_pedaco.split(" ")
                for cada_palavra in palavras:
                    if len(cada_palavra) == 11: # O número de registro da carteira de habilitacao tem 11 digitos
                        digitos_registro = "".join(filter(lambda x: x.isdigit(), cada_palavra))
                if len(digitos_registro) > 0:
                    print(f"Registro: {digitos_registro}")
            if "VALIDADE" in cada_pedaco:
                data_validade_texto = cada_pedaco.rsplit("VALIDADE")[1].split()[-2]
                print(f"Validade: {data_validade_texto}")
                data_1a_habilitacao = cada_pedaco.rsplit("VALIDADE")[1].split()[-1]
                print(f"1a Habilitação: {data_1a_habilitacao}")
            if "CPF" in cada_pedaco:
                cpf_texto = cada_pedaco.rsplit("CPF")[1].split()
                # Como ele não reconhece o ponto, o software le como trecho de 3 digitos em ordem
                # ou ele reconhece o traço final do cpf no conjunto de 6 digitos (exemplo 012-34)
                # irei remover o ponto porque as vezes ele reconhece o ponto no cpf. As vezes não reconhece.
                # O campo CPF nao pode ter mais do que 14 caracteres, considerando pontos e traços '000.000.000-00'
                cpf = ""
                for cada_palavra in cpf_texto:
                    if (len(cpf) >= 12): #cpf já preenchido com 000000000-00, nao precisa verificar mais nada.
                        break
                    cond1 = (len(cada_palavra.split()) <= 14)
                    cond2 = "." in cada_palavra
                    if cond2:
                        cada_palavra = cada_palavra.replace(".", "")
                    cond3 = (len(cada_palavra) == 3) and (cada_palavra.isdigit())
                    cond4 = ('-' in cada_palavra)
                    if cond1 and (cond2 or cond3 or cond4):
                        cpf += cada_palavra
                print(f"CPF: {cpf}")

        i += 1

