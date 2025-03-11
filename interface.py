import easyocr
from PyQt6.QtWidgets import QApplication, QPushButton, QProgressBar, QLineEdit, QWidget, QFileDialog, QMessageBox
from PyQt6 import uic, QtWidgets
from PIL import Image, ImageDraw
import os
import leitor_cnh_versao2 as func_cnh

###### QFileDialog em https://www.tutorialspoint.com/pyqt/pyqt_qfiledialog_widget.htm

import sys

class UI(QWidget):
    def __init__(self):
        super().__init__()

        self.path_foto = ""

        # Carregando a interface
        uic.loadUi("interface.ui", self)

        self.pathPhoto = self.findChild(QLineEdit, "pathPhoto")
        self.buttonCarregarPhoto = self.findChild(QPushButton, "pushButton")
        self.nome = self.findChild(QLineEdit, "lineEdit_nome")
        self.identidade = self.findChild(QLineEdit, "lineEdit_identidade")
        self.cpf = self.findChild(QLineEdit, "lineEdit_cpf")
        self.dtNascimento = self.findChild(QLineEdit, "lineEdit_dtNascimento")
        self.filiacao = self.findChild(QLineEdit, "lineEdit_filiacao")
        self.categoria = self.findChild(QLineEdit, "lineEdit_categoria")
        self.registo = self.findChild(QLineEdit, "lineEdit_numeroRegistro")
        self.validade = self.findChild(QLineEdit, "lineEdit_validade")
        self.primeiraHabilitacao = self.findChild(QLineEdit, "lineEdit_1ahabilitacao")
        self.barraProgresso = self.findChild(QProgressBar, "progressBar")

        self.interfaceInicial()

        # Conectando aos botões:
        self.buttonCarregarPhoto.clicked.connect(self.carregarFoto)
        self.pathPhoto.returnPressed.connect(self.carregarFotoLineEdit)

    def interfaceInicial(self):
        self.nome.setEnabled(False)
        self.identidade.setEnabled(False)
        self.cpf.setEnabled(False)
        self.dtNascimento.setEnabled(False)
        self.filiacao.setEnabled(False)
        self.categoria.setEnabled(False)
        self.registo.setEnabled(False)
        self.validade.setEnabled(False)
        self.primeiraHabilitacao.setEnabled(False)
        self.barraProgresso.setVisible(False)

    def carregarFoto(self):
        self.path_foto = QFileDialog.getOpenFileName(self, 'Abrir arquivo',
                                    os.getcwd(),"Image files (*.jpg *.gif *.png)")
        self.pathPhoto.setText(self.path_foto[0])
        self.barraProgresso.setVisible(True)
        self.lerCarteira(self.path_foto[0])

    def carregarFotoLineEdit(self):
        if os.path.exists(self.pathPhoto.text()):
            self.path_foto = self.pathPhoto.text()
            self.barraProgresso.setVisible(True)
            self.lerCarteira(self.path_foto)
        else:
            QMessageBox.warning(self, "Atenção", "Diretório inválido")
            self.path_foto = ""
            self.pathPhoto.setText("")

    def lerCarteira(self, path):
        # Zerar algum campo previamente preenchido
        self.nome.setText("")
        self.identidade.setText("")
        self.cpf.setText("")
        self.dtNascimento.setText("")
        self.filiacao.setText("")
        self.categoria.setText("")
        self.registo.setText("")
        self.validade.setText("")
        self.primeiraHabilitacao.setText("")
        self.barraProgresso.setValue(20)

        # Tratando a imagem
        img_tratada = func_cnh.tratamento_carteira(path)
        self.barraProgresso.setValue(25)

        # Desenha a borda
        reader = easyocr.Reader(["pt"])
        # borda = reader.readtext("./imagem_tratada.jpg", detail=1, paragraph=False)
        # img = Image.open("./imagem_tratada.jpg")
        print("Delimitando os campos da carteira...")
        borda = reader.readtext(img_tratada, detail=1, paragraph=False)
        self.barraProgresso.setValue(30)
        img = Image.open(img_tratada)
        self.barraProgresso.setValue(35)
        cnh_with_border = func_cnh.draw_boxes(img, borda)
        self.barraProgresso.setValue(40)
        cnh_with_border.show()
        self.barraProgresso.setValue(50)

        # Transformar em texto continuo o texto lido pelo easyOCR
        print("Convertendo imagem a carteira para texto...")
        # result = reader.readtext("./imagem_tratada.jpg", detail=0, paragraph=False)
        result = reader.readtext(path, detail=0, paragraph=False)
        self.barraProgresso.setValue(60)
        result_text = ' '.join(result)
        self.barraProgresso.setValue(70)

        # exporta o resultado da leitura em texto
        print("Exportando a carteira em texto no arquivo output.txt...")
        self.barraProgresso.setValue(75)
        func_cnh.exporta_cnh_texto(result_text, "output")
        self.barraProgresso.setValue(80)

        # Fazer o scanner dos dados
        print("Escaneando campos da carteira...")
        func_cnh.scanner_carteira(result_text)
        self.barraProgresso.setValue(90)

        # Registrar os campos no campo texto de cada categoria
        self.nome.setText(func_cnh.dict_campos.get("nome"))
        self.identidade.setText(f"{str(func_cnh.dict_campos.get('rg'))} {func_cnh.dict_campos.get('org_emissor')}")
        self.cpf.setText(func_cnh.dict_campos.get("cpf"))
        self.dtNascimento.setText(func_cnh.dict_campos.get("dt_nascimento"))
        self.filiacao.setText(func_cnh.dict_campos.get("filiacao"))
        self.categoria.setText(func_cnh.dict_campos.get("categoria"))
        self.registo.setText(str(func_cnh.dict_campos.get("no_registro")))
        self.validade.setText(func_cnh.dict_campos.get("validade"))
        self.primeiraHabilitacao.setText(func_cnh.dict_campos.get("primeirahabilitacao"))
        self.barraProgresso.setValue(100)

        # Mostrar mensagem que a carteira foi lida com sucesso
        QMessageBox.information(self, "Parabéns", "Carteira lida com sucesso")

        # Zerar a barra de progresso e remover a visibilidade da barra de progresso
        self.barraProgresso.setValue(0)
        self.barraProgresso.setVisible(False)

# Código básico para executar a janela
app = QApplication(sys.argv)
window = UI()
window.show()
sys.exit(app.exec())
