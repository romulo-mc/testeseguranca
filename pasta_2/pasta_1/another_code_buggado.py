import os
import sys

def exemplo_funcao(var1, var2):
    resultado = var1 + var2
    return resultado

# Uso de variáveis globais
variavel_global = 10

def calculo_inadequado():
    for i in range(10):
        resultado = i + variavel_global
    print(resultado)

def leitura_arquivo():
    # Abertura de arquivo sem gerenciamento de contexto
    arquivo = open('arquivo_inexistente.txt', 'r')
    linhas = arquivo.readlines()
    print(linhas)
    arquivo.close()

def main():
    exemplo_funcao(5, '10')  # Erro de tipo
    calculo_inadequado()
    leitura_arquivo()

if __name__ == "__main__":
    main()
