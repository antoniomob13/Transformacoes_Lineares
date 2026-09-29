import math as ma

class Matriz:
    def __init__(self, matriz):
        # matriz deve ter formato 2 x N (linha 0 = X, linha 1 = Y)
        self.matriz_atl = [linha[:] for linha in matriz]
        self.matriz_atg = None
        self.ancoragem_x = (min(self.matriz_atl[0]) + max(self.matriz_atl[0])) / 2
        self.ancoragem_y = (min(self.matriz_atl[1]) + max(self.matriz_atl[1])) / 2

    def _salvar_estado(self):
        #salva o estado atual da matriz antes de qualquer transformação
        self.matriz_atg = [linha[:] for linha in self.matriz_atl]



    def multiplicar(self, t):
        #faz a multiplicação da matriz atual (self.matriz_atl) pela matriz de transformação t(espelhamento, rotação ou escalonamento)
        self._salvar_estado()
        n_colunas = len(self.matriz_atl[0])
        nova_matriz = [[0.0] * n_colunas for _ in range(2)]
        for j in range(n_colunas):
            x = self.matriz_atl[0][j]
            y = self.matriz_atl[1][j]
            nova_matriz[0][j] = t[0][0] * x + t[0][1] * y
            nova_matriz[1][j] = t[1][0] * x + t[1][1] * y
        self.matriz_atl = nova_matriz

    def somar(self, dx, dy):
        #soma de deslocamento (dx, dy) a todos os pontos da matriz atual.
        self._salvar_estado()
        n_colunas = len(self.matriz_atl[0])
        for j in range(n_colunas):
            self.matriz_atl[0][j] += dx
            self.matriz_atl[1][j] += dy

    def rotacao(self, angulo, ancoragem_x=0, ancoragem_y=0):
        if ancoragem_x is None and ancoragem_y is None:
            ancoragem_x = self.ancoragem_x
            ancoragem_y = self.ancoragem_y

        rad = ma.radians(angulo)
        cos_a = round(ma.cos(rad), 8)
        sin_a = round(ma.sin(rad), 8)
        
        m_rot = [[cos_a, -sin_a],
                [sin_a,  cos_a]]
        self.somar(-ancoragem_x, -ancoragem_y)
        self.multiplicar(m_rot)
        self.somar(ancoragem_x, ancoragem_y)

    def espelhamento(self, eixo='x'):
        """Espelha em relação ao eixo informado ('x' inverte Y, 'y' inverte X)."""
        if eixo.lower() == 'y':
            m_esp = [[-1, 0], 
                     [ 0, 1]]
        else:
            m_esp = [[1,  0], 
                     [0, -1]]
        
        self.multiplicar(m_esp)

    def escalonamento(self, sx=1.0, sy=1.0, ancoragem_x=0, ancoragem_y=0):
        if ancoragem_x is None and ancoragem_y is None:
            ancoragem_x = self.ancoragem_x
            ancoragem_y = self.ancoragem_y
        m_esc = [
            [sx,  0],
            [ 0, sy]
        ]
        
        self.somar(-ancoragem_x, -ancoragem_y)
        self.multiplicar(m_esc)
        self.somar(ancoragem_x, ancoragem_y)

    def visualizar(self, rotulo="Matriz Atual"):
        """Exibe a matriz em formato tabular e os pares ordenados correspondentes."""
        print(f"\n--- {rotulo} ---")
        print("X: [ " + "  ".join(f"{v:8.2f}" for v in self.matriz_atl[0]) + " ]")
        print("Y: [ " + "  ".join(f"{v:8.2f}" for v in self.matriz_atl[1]) + " ]")
        
        pontos = [f"P{i}({self.matriz_atl[0][i]:.2f}, {self.matriz_atl[1][i]:.2f})" 
                  for i in range(len(self.matriz_atl[0]))]
        print("Pontos: " + ", ".join(pontos))







# Teste rápido: só roda ao executar este arquivo direto (py transformacoes_lineares.py),
# não quando ele é importado pela interface (app.py).
if __name__ == "__main__":
    retangulo = Matriz([[4, 6, 4, 2],
                            [2, 5, 4, 5]])

    retangulo.visualizar("Estado Inicial")

    # Rotaciona 90° em torno de (0, 0)
    retangulo.rotacao(90, 0, 0)
    retangulo.visualizar("Após Rotação de 90° em (0, 0)")

    # Escala 2x no eixo X e 2x no eixo Y mantendo o pivô em (2, 2)
    retangulo.escalonamento(sx=2, sy=2, ancoragem_x=2, ancoragem_y=2)
    retangulo.visualizar("Após Escala 2x com pivô (2, 2)")