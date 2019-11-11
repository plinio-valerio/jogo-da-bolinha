from graphics import *
import random
import math

width = 800  # largura da tela
height = 600  # altura da tela

du = 40  # distancia da linha superior para o limite superior da tela
dd = 40  # distancia da linha inferior para o limite inferior da tela
dl = 40  # distancia da linha esquerda para o limite esquerdo da tela
dr = 40  # distancia da linha direita para o limite direito da tela
db = 30  # distancia da barra para a linha inferior

raio_bola = 10  # raio da bolinha
fill_bola = color_rgb(10, 10, 100)  # cor de preenchimento da bolinha
outline_bola = color_rgb(255, 255, 0)  # cor do contorno da bolinha

velocidade_barra = 9.0  # passo horizontal da barra a cada comando do jogador
fill_barra = color_rgb(100, 10, 10)  # cor de preenchimento da barra
outline_barra = color_rgb(255, 255, 0)  # cor do contorno da barra
comprimento_barra = 100
espessura_barra = 10

pontos_por_fase = 3  # quantidade de pontos necessaria para acelerar a bolinha
vel_inicial = 6.0  # velocidade inicial da bolinha
dt = 0.020  # intervalo de tempo entre dois frames do jogo

n_obstaculos = 5

###################

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0

class Body:
    def __init__(self, body, pos_x=None, pos_y=None, vel_x=.0, vel_y=.0):
        self.body = body
        self.pos_x_0 = pos_x
        self.pos_y_0 = pos_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vel_x_0 = vel_x
        self.vel_y_0 = vel_y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.vel_modulo = math.sqrt(self.vel_x**2 + self.vel_y**2)
        self.vel_angulo = math.atan2(self.vel_y, self.vel_x)
        self.obstacles = []
        self.nao_colidiu = []
    def reset(self):
        self.body.move(self.pos_x_0 - self.pos_x, self.pos_y_0 - self.pos_y)
        self.pos_x = self.pos_x_0
        self.pos_y = self.pos_y_0
        self.vel_x = self.vel_x_0
        self.vel_y = self.vel_y_0
        self.vel_modulo = math.sqrt(self.vel_x**2 + self.vel_y**2)
        self.vel_angulo = math.atan2(self.vel_y, self.vel_x)
    def update(self, dt=1):
        self.pos_x = self.pos_x + self.vel_x * dt
        self.pos_y = self.pos_y + self.vel_y * dt
        self.body.move(self.vel_x * dt, self.vel_y * dt)
        for idx, obst in enumerate(self.obstacles):
            em_contato = self.collide(obst, self.nao_colidiu[idx])
            self.nao_colidiu[idx] = not em_contato
    def add_obstacle(self, corpo):
        self.obstacles.append(corpo)
        self.nao_colidiu.append(True)
    def is_in_collision_zone(self, corpo):
        p_colisao_x = corpo.pos_x - self.pos_x
        p_colisao_y = corpo.pos_y - self.pos_y
        distancia = math.sqrt(p_colisao_x**2 + p_colisao_y**2)
        if distancia > corpo.radius + self.radius:
            return False
        return True
    def collide(self, obstacle, modify):
        angulo_normal = obstacle.get_normal_angle(self)
        if angulo_normal is None:
            return False
        if modify:
            novo_angulo = math.pi + 2*angulo_normal - self.vel_angulo  # == math.pi - (self.vel_angulo - angulo_normal) + angulo_normal
            self.vel_x = self.vel_modulo * math.cos(novo_angulo)
            self.vel_y = self.vel_modulo * math.sin(novo_angulo)
            self.vel_x += obstacle.vel_x
            self.vel_y += obstacle.vel_y
            self.vel_modulo = math.sqrt(self.vel_x**2 + self.vel_y**2)
            self.vel_angulo = math.atan2(self.vel_y, self.vel_x)
        return True
    def random_collide(self, obstacle, modify, mean=.0, std=math.tau/32):
        angulo_normal = obstacle.get_normal_angle(self)
        if angulo_normal is None:
            return False
        if modify:
            self.collide(obstacle, modify)
            incremento_aleatorio = random.gauss(mean, std)
            novo_angulo = self.vel_angulo + incremento_aleatorio
            if math.sin(novo_angulo - angulo_normal) * math.sin(self.vel_angulo - angulo_normal) >= 0 and \
              math.cos(novo_angulo - angulo_normal) * math.cos(self.vel_angulo - angulo_normal) >= 0:
                self.vel_angulo = novo_angulo
                self.vel_x = self.vel_modulo * math.cos(self.vel_angulo)
                self.vel_y = self.vel_modulo * math.sin(self.vel_angulo)
        return True
    def get_normal_angle(self, corpo):
        raise NotImplementedError
    def draw(self, win):
        self.body.draw(win)
    def undraw(self):
        self.body.undraw()
    def setFill(self, color):
        self.body.setFill(color)
    def setOutline(self, color):
        self.body.setOutline(color)
    def setWidth(self, width):
        self.body.setWidth(width)

class Ball(Body):
    def __init__(self, centro, raio, vel_x=.0, vel_y=.0):
        self.radius = raio
        Body.__init__(self, Circle(centro, raio), centro.getX(), centro.getY(), vel_x, vel_y)
    def get_normal_angle(self, projetil):
        if self.is_in_collision_zone(projetil):
            return math.atan2(projetil.pos_y - self.pos_y, projetil.pos_x - self.pos_x)
        return None

class RegularPolygon(Body):
    def __init__(self, centro, raio, n_lados, angulo=.0, vel_x=.0, vel_y=.0):
        self.radius = raio
        self.n_lados = n_lados
        self.angle = angulo % (math.tau / n_lados)
        self.vertices = [Point(centro.getX() + raio * math.cos(self.angle + i * math.tau / n_lados),
                               centro.getY() + raio * math.sin(self.angle + i * math.tau / n_lados)) for i in range(n_lados)]
        poly = Polygon(self.vertices)
        Body.__init__(self, poly, centro.getX(), centro.getY(), vel_x, vel_y)
    def get_normal_angle(self, projetil):
        if not self.is_in_collision_zone(projetil):
            return None
        vertices_ordenados = sorted(self.vertices, key = lambda p: math.sqrt((p.getX() - projetil.pos_x)**2 + (p.getY() - projetil.pos_y)**2))
        p1 = vertices_ordenados[0]
        p2 = vertices_ordenados[1]
        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projetil.pos_x - p1.getX()) + b * (projetil.pos_y - p1.getY())) / math.sqrt(a**2 + b**2)
        if distancia_bola_para_aresta > projetil.radius:
            return None
        return math.atan(-a/b) + math.tau/4
        # angulo_entre_vertices = math.tau / self.n_lados
        # angulo = math.atan2(y, x) - self.angle
        # return angulo // angulo_entre_vertices * angulo_entre_vertices + angulo_entre_vertices / 2

class Bar(Body):
    def __init__(self, p1, p2, vel_x=.0, vel_y=.0):
        pos_x = (p1.getX() + p2.getX()) / 2
        pos_y = (p1.getY() + p2.getY()) / 2
        self.height = math.fabs(p2.getY() - p1.getY())
        self.length = math.fabs(p2.getX() - p1.getX())
        self.radius = math.sqrt((p2.getX() - p1.getX())**2 + (p2.getY() - p1.getY())**2) / 2
        self.normal_angle = math.tau / 4
        Body.__init__(self, Rectangle(p1, p2), pos_x, pos_y, vel_x, vel_y)
    def get_normal_angle(self, projetil):
        if not self.is_in_collision_zone(projetil):
            return None
        distancia_bola_para_aresta = math.fabs(projetil.pos_y - self.pos_y + self.height / 2)
        if distancia_bola_para_aresta > projetil.radius:
            return None
        return self.normal_angle

class Wall(Body):
    def __init__(self, p1, p2):
        pos_x = (p2.getX() + p1.getX()) / 2
        pos_y = (p2.getY() + p1.getY()) / 2
        self.radius = math.sqrt((p2.getX() - p1.getX())**2 + (p2.getY() - p1.getY())**2) / 2
        self.normal_angle = math.atan2(p2.getY() - p1.getY(), p2.getX() - p1.getX()) + math.tau / 4
        Body.__init__(self, Line(p1, p2), pos_x, pos_y)
    def get_normal_angle(self, projetil):
        p1 = self.body.getP1()
        p2 = self.body.getP2()
        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projetil.pos_x - p1.getX()) + b * (projetil.pos_y - p1.getY())) / math.sqrt(a**2 + b**2)
        if distancia_bola_para_aresta > projetil.radius:
            return None
        # return math.atan(-a/b) + math.tau/4
        return self.normal_angle

win = GraphWin("Bolinha com Esteroides", width, height)
win.setCoords(0, 0, width, height)

linhaSuperior = Wall(Point(dl, height - du), Point(width - dr, height - du))
linhaSuperior.setWidth(10)
linhaSuperior.setFill(color_rgb(10, 100, 10))

linhaInferior = Wall(Point(dl, dd), Point(width - dr, dd))
linhaInferior.setWidth(3)
linhaInferior.setFill(color_rgb(10, 100, 10))

linhaEsquerda = Wall(Point(dl, dd), Point(dl, height - du))
linhaEsquerda.setWidth(10)
linhaEsquerda.setFill(color_rgb(10, 100, 10))

linhaDireita = Wall(Point(width - dr, dd), Point(width - dr, height - du))
linhaDireita.setWidth(10)
linhaDireita.setFill(color_rgb(10, 100, 10))

espaco_branco = Rectangle(Point(0, dd - 2), Point(width, 0))
espaco_branco.setFill('white')
espaco_branco.setOutline('white')

# texto
info_txt = Text(Point(width / 2, 25), '')
info_txt.setSize(14)
def atualiza_texto():
    info_txt.undraw()
    info_txt.setText("Pontos: " + str(pontos) + "\t\tVidas: " + str(vidas) + "\t\tVelocidade: %.2f" % bola.vel_modulo)
    info_txt.draw(win)

# barra
barra = Bar(Point(width/2 - comprimento_barra/2, dd + db + espessura_barra/2),
            Point(width/2 + comprimento_barra/2, dd + db - espessura_barra/2))
barra.setFill(fill_barra)
barra.setOutline(outline_barra)
barra.setWidth(2)
barra.add_obstacle(linhaEsquerda)
barra.add_obstacle(linhaDireita)

# bolinha
bola = Ball(Point(width/2, height/2), raio_bola, vel_y=vel_inicial)
bola.setFill(fill_bola)
bola.setOutline(outline_bola)
bola.setWidth(2)
bola.add_obstacle(linhaSuperior)
bola.add_obstacle(linhaInferior)
bola.add_obstacle(linhaEsquerda)
bola.add_obstacle(linhaDireita)
bola.add_obstacle(barra)

# def computa_colisao(poligono_regular, vel_x, vel_y):
#     vertices = poligono_regular.getPoints()
#     # calcula centro e raio do poligono
#     centro_x = .0
#     centro_y = .0
#     for p in vertices:
#         centro_x += p.getX()
#         centro_y += p.getY()
#     centro_x /= len(vertices)
#     centro_y /= len(vertices)
#     raio_poligono = math.sqrt((vertices[0].getX() - centro_x)**2 + (vertices[0].getY() - centro_y)**2)
#     if math.sqrt((col - centro_x)**2 + (lin - centro_y)**2) - raio > raio_poligono:
#         return vel_x, vel_y
#     for idx, p1 in enumerate(vertices):
#         p2 = vertices[(idx + 1) % len(vertices)]
#         # parametros da equacao da reta (aresta do poligono)
#         a = p1.getY() - p2.getY()
#         b = p2.getX() - p1.getX()
#         distancia_bola_para_aresta = math.fabs(a * (col - p1.getX()) + b * (lin - p1.getY())) / math.sqrt(a**2 + b**2)
#         if distancia_bola_para_aresta < raio:
#             return colisao(vel_x, vel_y, math.atan(-a/b) + math.tau/4)
#     return vel_x, vel_y

def game_over():
    win.setBackground('white')
    fim_txt = Text(Point(width/2, height/2), "GAME\nOVER")
    fim_txt.setStyle('bold')
    fim_txt.setSize(32)
    fim_txt.draw(win)
    time.sleep(2)
    fim_txt.undraw()
    info_txt.undraw()
    linhaInferior.undraw()
    linhaSuperior.undraw()
    linhaEsquerda.undraw()
    linhaDireita.undraw()
    espaco_branco.undraw()
    bola.undraw()
    barra.undraw()

# menu
for temp in range(1):
    # menu_txt = Text(Point(width/2, heigth/2), '')
    # menu_txt.setText('''
    #                  Novo jogo\n
    #                  \n
    #                  Placar
    #                  ''')



    # comeca jogo
    vidas = 3
    pontos = 0
    linhaSuperior.draw(win)
    linhaInferior.draw(win)
    linhaEsquerda.draw(win)
    linhaDireita.draw(win)
    espaco_branco.draw(win)
    bola.draw(win)
    barra.draw(win)
    obstaculos = []
    for i in range(n_obstaculos):  # cria obstaculos
        center = Point( (width - dr - dl) * random.random(),
                        (height - du - dd - db) / 3 * random.random() + 2 * (height - du - dd - db) / 3 + dd + db )
        radius = random.random() * 25 + 25
        vel_x = random.gauss(0, 2)
        if random.random() < .33:  # probabilidade de obstaculo ser um circulo
            obst = Ball(center, radius, vel_x=vel_x)
        else:
            n_lados = random.randint(3, 8)
            angulo = random.random() * math.tau / n_lados
            obst = RegularPolygon(center, radius, n_lados, angulo, vel_x=vel_x)
        color_r = random.randrange(0, 256)
        color_g = random.randrange(0, 256)
        color_b = random.randrange(0, 256)
        obst.setFill(color_rgb(color_r, color_g, color_b))
        obst.setOutline(color_rgb((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
        obst.setWidth(2)
        obst.draw(win)
        obst.add_obstacle(linhaEsquerda)
        obst.add_obstacle(linhaDireita)
        bola.add_obstacle(obst)
        obstaculos.append(obst)
    barra.reset()
    bola.reset()
    atualiza_texto()
    time.sleep(1)

    while True:
        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd'):
            barra.vel_x += velocidade_barra
        if (tecla == "Left" or tecla == 'a'):
            barra.vel_x -= velocidade_barra
        # sair do jogo
        if tecla == "Escape":
            game_over()
            break

        bola.update()
        barra.update()
        for obst in obstaculos:
            obst.update()

        # if col > colIni and col < colIni + comprimento_barra and lin < barra.getP1().getY() + raio_bola and lin > barra.getP2().getY():  # bateu na barra
        #     if bola_ainda_nao_colidiu_com_barra:
        #         vel_x, vel_y = colisao_aleatoria(vel_x, vel_y)
        #         pontos += 1
        #         if pontos % pontos_por_fase == 0:
        #             win.setBackground(color_rgb(random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256)))
        #             vel_x *= 1.2
        #             vel_y *= 1.2
        #         atualiza_texto()
        #         bola_ainda_nao_colidiu_com_barra = False
        # else:  # bola nao esta em contato com a barra
        #     bola_ainda_nao_colidiu_com_barra = True
        # if lin < dd + raio_bola:  # bateu na linha de baixo (morreu)
        #     vidas -= 1
        #     if vidas == 0:
        #         game_over()
        #         break
        #     vel_mod = math.sqrt(vel_x**2 + vel_y**2)
        #     vel_ang = math.tau/4 + math.tau/8 * (2*random.random() - 1)
        #     vel_x = (vel_inicial + vel_mod) / 2 * math.cos(vel_ang)
        #     vel_y = (vel_inicial + vel_mod) / 2 * math.sin(vel_ang)
        #     reseta_bola()
        #     reseta_barra()
        #     atualiza_texto()
        #     time.sleep(1)

        time.sleep(dt)

win.close()
