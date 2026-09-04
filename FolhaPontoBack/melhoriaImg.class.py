import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Img:
    def __init__(self):
        self.__CAMINHO = self.__caminha()
        self.obj = self.__carregadorImagem()
        # self.nome = ""
        self.__arquivo = "teste"
        self.cor = "colorado"
        self.xy = 0
        self.ab = [0, 0]
        self.x = 0

    def buscarImagem(self):
        imagens = list(self.__CAMINHO.glob("*.png"))
        print("Manda a imagem patrão")
        for i, imagem in enumerate(imagens):
            print(f"{i} - {imagem.name}")
        var = int(input())
        option = imagens[var]
        self.__arquivo = str(option)
        return option
    
    def __caminha(self):
        return BASE_DIR / "imgs" / "originais"

    def __carregadorImagem(self):
        return cv2.imread(str(self.__CAMINHO / self.buscarImagem()))
    
    def img(self):
        self.x = str(input("1 - Ampliar a imagem \n2 - alterar o brilho/contraste \n3 - alterar a cor da imagem \n" \
        "5 - limiarizar"))
        match self.x:
            case '1':
                try:
                    self.xy = float(input("\nGrau de ampliação? "))
                    imagem_maior = cv2.resize(
                                self.obj,
                                None,
                                fx=self.xy,
                                fy=self.xy,
                                interpolation=cv2.INTER_CUBIC
                            )
                    self.obj = imagem_maior
                    print("Ampliado")
                except Exception as erro:
                    print(erro)
                finally: 
                    self.img()
            case '2':
                try:
                    self.ab[0] = float(input("\nQual a alfa? "))
                    self.ab[1] = float(input("\nQual o beta? "))
                    imagem_contraste = cv2.convertScaleAbs(
                        self.obj,
                        alpha = 1 + self.ab[0]/10,
                        beta = self.ab[1], 
                    )
                    self.obj = imagem_contraste
                    print("Contrastado")
                except Exception as erro:
                    print(erro)
                finally: 
                    self.img()

            case '3':
                try:
                    self.cor = "descolorado"
                    imagem_cor = cv2.cvtColor(self.obj, cv2.COLOR_BGR2GRAY)
                    self.obj = imagem_cor
                    print("Colorado")
                except Exception as erro:
                    print(erro)
                finally: 
                    self.img()
            case '4':
                try:
                    obj = []
                    # kernel = np.ones((5,5), np.uint8)
                    cinzado = cv2.cvtColor(self.obj, cv2.COLOR_BGR2GRAY)

                    imagem_desfocada = cv2.blur(cinzado,(3,3))
                    obj.append(imagem_desfocada)
# 
                    imagem_desfocada_gaussiana = cv2.GaussianBlur(cinzado,(3,3),0)
                    obj.append(imagem_desfocada_gaussiana)

                    # imagem_coisada_dentro = cv2.morphologyEx(cinzado, cv2.MORPH_CLOSE, kernel)
                    # obj.append(imagem_coisada_dentro)
                    
                    # imagem_coisada_fora = cv2.morphologyEx (imagem_coisada_dentro, cv2.MORPH_OPEN, kernel)
                    # obj.append(imagem_coisada_fora)

                    for i,imagem in enumerate(obj):
                        caminho_saida = BASE_DIR / "imgs" / "editadas" / f"{self.__arquivo}_coisado_{i}.png"
                        cv2.imwrite(str(caminho_saida), imagem)

                    # self.obj = imagem_coisada_fora
                except Exception as erro:
                    print(erro)
                # finally: 
                #     self.img()
            case '5':
                try:
                    obj = []

                    _, imagem_limiarisada = cv2.threshold(cv2.cvtColor(self.obj, cv2.COLOR_BGR2GRAY),0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    obj.append(imagem_limiarisada)

                    # imagem_limiarisada_coisada = cv2.adaptiveThreshold(cv2.cvtColor(self.obj, cv2.COLOR_BGR2GRAY),255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,0)
                    # obj.append(imagem_limiarisada_coisada)

                    # imagem_limiarisada_coisada_gausiana = cv2.adaptiveThreshold(cv2.cvtColor(self.obj, cv2.COLOR_BGR2GRAY),255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,0)
                    # obj.append(imagem_limiarisada_coisada_gausiana)

                    # for i,imagem in enumerate(obj):
                    #     caminho_saida = BASE_DIR / "imgs" / "editadas" / f"{self.__arquivo}_limiarisada_{i}.png"
                    #     cv2.imwrite(str(caminho_saida), imagem)

                except Exception as erro:
                    print(erro)
                finally: 
                    self.img()
            case _:
                print("Passou nada paizão!")

    def execute(self):
        self.img()
        if self.xy != 0:
            self.__arquivo += f"_x{float(self.xy)}"
        if self.ab[0]!=0 or self.ab[1] !=0 :
            self.__arquivo += f"_ab{float(self.ab[0])}_{float(self.ab[1])}"
        if self.cor != "colorado":
            self.__arquivo += f"_{self.cor}"

        caminho_saida = BASE_DIR / "imgs" / "editadas" / f"{self.__arquivo}.png"
        cv2.imwrite(str(caminho_saida), self.obj)

obj = Img()
obj.execute()