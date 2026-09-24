import math as ma
class Matriz:
    def __init__(self, matriz):
        self.matriz_atl = matriz
        self.matriz_atg = None

    def rotacao(self, angulo, ancoragem_x = 0, ancoragem_y = 0):
        self.somar(ancoragem_x*-1 , ancoragem_y*-1)
        angulo = ma.radians(angulo)
        matriz_rt = [[ma.cos(angulo), -ma.sin(angulo)], [ma.sin(angulo), ma.cos(angulo)]]
        matriz_apoio = [[0 for _ in range (len(self.matriz_atl[0]))] for _ in range(len(self.matriz_atl))]
        a, b, l= 0, 1, 1

        for i    in range(len(self.matriz_atl)):
            for j in range(len(self.matriz_atl[0])):
                matriz_apoio[i][j] = self.matriz_atl[i][j]*matriz_rt[i][a] + self.matriz_atl[i+l][j]*matriz_rt[i][b]
            a, b, l= 1, 0, -1
        self.matriz_atg = self.matriz_atg
        self.matriz_atl = matriz_apoio
        self.somar(ancoragem_x , ancoragem_y)

    def espelhamento(self, eixo):
        c = 1
        if eixo =='y':
            c = -1
        matriz_esp = [[c, 0], [0, -c]]
        matriz_apoio = [[0 for _ in range (len(self.matriz_atl[0]))] for _ in range(len(self.matriz_atl))]
        a, b, l= 0, 1, 1

        for i in range(len(self.matriz_atl)):
            for j in range(len(self.matriz_atl[0])):
                matriz_apoio[i][j] = self.matriz_atl[i][j]*matriz_esp[i][a] + self.matriz_atl[i+l][j]*matriz_esp[i][b]
            a, b, l= 1, 0, -1
        self.matriz_atg = self.matriz_atg
        self.matriz_atl = matriz_apoio

    def escalonamento(self, x = 0, y = 0, ancoragem_x = 0, ancoragem_y = 0):
        self.somar(ancoragem_x*-1 , ancoragem_y*-1)
        matriz_esc = [[x, 0], [0, y]]
        matriz_apoio = [[0 for _ in range (len(self.matriz_atl[0]))] for _ in range(len(self.matriz_atl))]
        a, b, l= 0, 1, 1

        for i in range(len(self.matriz_atl)):
            for j in range(len(self.matriz_atl[0])):
                matriz_apoio[i][j] = self.matriz_atl[i][j]*matriz_esc[i][a] + self.matriz_atl[i+l][j]*matriz_esc[i][b]
            a, b, l= 1, 0, -1
        self.matriz_atg = self.matriz_atg
        self.matriz_atl = matriz_apoio
        self.somar(ancoragem_x , ancoragem_y)


    def somar(self, x , y ):
        matriz_apoio = [[x for _ in range (len(self.matriz_atl[0]))], [y for _ in range (len(self.matriz_atl[0]))]]
        for i in range(len(self.matriz_atl)):
            for j in range(len(self.matriz_atl[0])):
                self.matriz_atl[i][j] = self.matriz_atl[i][j] + matriz_apoio[i][j]
        


matriz = Matriz([[4, 6, 4, 2], [2, 5, 4, 5]])

print(matriz.matriz_atl)
matriz.rotacao(90, 0, 0)