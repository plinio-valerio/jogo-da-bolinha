from graphics import *
import random
import math

width = 960  # largura da tela
height = 640  # altura da tela

du = 40  # distancia da linha superior para o limite superior da tela
dd = 40  # distancia da linha inferior para o limite inferior da tela
dl = 40  # distancia da linha esquerda para o limite esquerdo da tela
dr = 40  # distancia da linha direita para o limite direito da tela
db = 60  # distancia da barra para a linha inferior

raio_bola = 15  # raio da bolinha
vidas_iniciais = 3
fill_bola = color_rgb(10, 10, 100)  # cor de preenchimento da bolinha
outline_bola = color_rgb(255, 255, 0)  # cor do contorno da bolinha

comprimento_barra = 100
espessura_barra = 10
velocidade_barra = 20.0  # passo horizontal da barra a cada comando do jogador
atrito_barra = 0.2  # numero entre 0 e 1
fill_barra = color_rgb(100, 10, 10)  # cor de preenchimento da barra
outline_barra = color_rgb(255, 255, 0)  # cor do contorno da barra


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
    obj_idx = 0
    def __init__(self, body, pos_x=None, pos_y=None, vel_x=.0, vel_y=.0, vidas=3, name=None, radius=None, kill=False, atrito=.0):
        Body.obj_idx += 1
        if name is None:
            self.name = 'Body_' + str(Body.obj_idx)
        else:
            self.name = name
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
        self.vidas_iniciais = vidas
        self.vidas = self.vidas_iniciais
        self.kill = kill
        if radius is not None:
            self.radius = radius
        self.atrito = atrito
        self.obstacles = []
        self.nao_colidiu = []
        self.width = 1
        self.n_colisoes = 0
    def reset(self):
        self.body.move(self.pos_x_0 - self.pos_x, self.pos_y_0 - self.pos_y)
        self.pos_x = self.pos_x_0
        self.pos_y = self.pos_y_0
        self.vel_x = self.vel_x_0
        self.vel_y = self.vel_y_0
        self.vel_modulo = math.sqrt(self.vel_x**2 + self.vel_y**2)
        self.vel_angulo = math.atan2(self.vel_y, self.vel_x)
    def update(self, dt=1):
        dx = self.vel_x * dt
        dy = self.vel_y * dt
        self.pos_x += dx
        self.pos_y += dy
        self.body.move(dx, dy)
        for idx, obst in enumerate(self.obstacles):
            em_contato = self.collide(obst, self.nao_colidiu[idx])
            self.nao_colidiu[idx] = not em_contato
    def add_obstacle(self, corpo):
        self.obstacles.append(corpo)
        self.nao_colidiu.append(True)
    def is_in_collision_zone(self, corpo):  # retorna True caso corpo esteja em distancia de colisao. Nao significa que os objetos estejam em contato
        p_colisao_x = corpo.pos_x - self.pos_x
        p_colisao_y = corpo.pos_y - self.pos_y
        distancia = math.sqrt(p_colisao_x**2 + p_colisao_y**2)
        if distancia > corpo.radius + self.radius:
            return False
        return True
    def collide(self, obstacle, modify, verbose=False):  # retorna True caso o objeto esteja em contato com o obstaculo
        angulo_normal = obstacle.get_normal_angle(self)
        if angulo_normal is None:  # objeto nao esta em contato com obstaculo
            return False
        if modify:
            vel_proj_norm = self.vel_modulo * math.cos(self.vel_angulo - angulo_normal)
            vel_proj_perp = self.vel_modulo * math.sin(self.vel_angulo - angulo_normal)
            vel_obst_norm = obstacle.vel_modulo * math.cos(obstacle.vel_angulo - angulo_normal)
            vel_obst_perp = obstacle.vel_modulo * math.sin(obstacle.vel_angulo - angulo_normal)
            vel_diff_norm = vel_proj_norm - vel_obst_norm
            vel_diff_perp = vel_proj_perp - vel_obst_perp
            nova_vel_diff_norm = -vel_diff_norm
            nova_vel_diff_perp = vel_diff_perp * (1 - obstacle.atrito)
            nova_vel_proj_norm = nova_vel_diff_norm + vel_obst_norm
            nova_vel_proj_perp = nova_vel_diff_perp + vel_obst_perp
            if verbose:  # gera relatorio para debbug
                print("Evento: colisao")
                print("\tProjetil:", self.name)
                print("\tObstaculo:", obstacle.name)
                print("\tangulo_normal = %d" % int(angulo_normal / math.tau * 360))
                print("\tvel_proj_norm = %.2f" % vel_proj_norm)
                print("\tvel_obst_norm = %.2f" % vel_obst_norm)
                print("\tvel_diff_norm = %.2f" % vel_diff_norm)
                print("\tnova_vel_diff_norm = %.2f" % nova_vel_diff_norm)
                print("\tnova_vel_proj_norm = %.2f" % nova_vel_proj_norm)
                print("\tvel_proj_perp = %.2f" % vel_proj_perp)
                print("\tvel_obst_perp = %.2f" % vel_obst_perp)
                print("\tvel_diff_perp = %.2f" % vel_diff_perp)
                print("\tnova_vel_diff_perp = %.2f" % nova_vel_diff_perp)
                print("\tnova_vel_proj_perp = %.2f" % nova_vel_proj_perp)
                print()
            self.vel_modulo = math.sqrt(nova_vel_proj_norm**2 + nova_vel_proj_perp**2)
            self.vel_angulo = math.atan2(nova_vel_proj_perp, nova_vel_proj_norm) + angulo_normal
            self.vel_x = self.vel_modulo * math.cos(self.vel_angulo)
            self.vel_y = self.vel_modulo * math.sin(self.vel_angulo)
            self.n_colisoes += 1
            obstacle.on_collision(self)
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
    def on_collision(self, projetil):
        if self.kill:
            projetil.vidas -= 1
            projetil.on_death()
    def on_death(self):
        self.reset()
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
        self.width = width
        self.body.setWidth(width)

class Ball(Body):
    obj_idx = 0
    def __init__(self, centro, raio, vel_x=.0, vel_y=.0, vidas=1, name=None, kill=False):
        Ball.obj_idx += 1
        if name is None:
            name = 'Ball_' + str(Ball.obj_idx)
        self.radius = raio
        self.vidas = vidas
        Body.__init__(self, Circle(centro, raio), centro.getX(), centro.getY(), vel_x, vel_y, name=name, vidas=vidas, kill=kill)
    def get_normal_angle(self, projetil):
        if self.is_in_collision_zone(projetil):
            return math.atan2(projetil.pos_y - self.pos_y, projetil.pos_x - self.pos_x)
        return None

class RegularPolygon(Body):
    obj_idx = 0
    def __init__(self, centro, raio, n_lados, angulo=.0, vel_x=.0, vel_y=.0, name=None, kill=False):
        RegularPolygon.obj_idx += 1
        if name is None:
            name = 'Poly_' + str(RegularPolygon.obj_idx)
        self.radius = raio
        self.n_lados = n_lados
        self.angle = angulo % (math.tau / n_lados)
        self.vertices = [Point(centro.getX() + raio * math.cos(self.angle + i * math.tau / n_lados),
                               centro.getY() + raio * math.sin(self.angle + i * math.tau / n_lados)) for i in range(n_lados)]
        poly = Polygon(self.vertices)
        Body.__init__(self, poly, centro.getX(), centro.getY(), vel_x, vel_y, name=name, kill=kill)
    def get_normal_angle(self, projetil, verbose=False):
        if not self.is_in_collision_zone(projetil):
            return None
        angulo_entre_vertices = math.tau / self.n_lados
        angulo = math.atan2(projetil.pos_y - self.pos_y, projetil.pos_x - self.pos_x) - self.angle
        idx_v = int(angulo // angulo_entre_vertices)
        p1 = self.vertices[idx_v]
        p2 = self.vertices[(idx_v - 1) % self.n_lados]

        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projetil.pos_x - p1.getX()) + b * (projetil.pos_y - p1.getY())) / math.sqrt(a**2 + b**2)

        if verbose:
            print("Evento: possivel colisao")
            print("\tProjetil:", projetil.name, "\t== (%d, %d)" % (projetil.pos_x, projetil.pos_y))
            print("\tObstaculo:", self.name)
            print("\tAngulo do poligono: %d" % int(self.angle / math.tau * 360))
            print("\tAngulo do projetil: %d" % int(angulo / math.tau * 360))
            print("\tVertices:  ", [(int(v.getX()), int(v.getY())) for v in self.vertices])
            print("\tDistancias:", ["  %.2f" % math.sqrt((projetil.pos_x - v.getX())**2 + (projetil.pos_y - v.getY())**2) for v in self.vertices])
            print("\tp1: (%d, %d)" % (p1.getX(), p1.getY()))
            print("\tp2: (%d, %d)" % (p2.getX(), p2.getY()))
            print("\ta = %.2f" % a)
            print("\tb = %.2f" % b)
            print("\tdist = %.2f" % distancia_bola_para_aresta)

        if distancia_bola_para_aresta > projetil.radius:
            return None
        # return math.atan(-a/b) + math.tau/4
        return angulo // angulo_entre_vertices * angulo_entre_vertices + self.angle + angulo_entre_vertices / 2
        # angulo_entre_vertices = math.tau / self.n_lados
        # angulo = math.atan2(y, x) - self.angle
        # return angulo // angulo_entre_vertices * angulo_entre_vertices + angulo_entre_vertices / 2

class Bar(Body):
    obj_idx = 0
    def __init__(self, p1, p2, passo, atrito, vel_x_0=.0, name=None, kill=False):
        Bar.obj_idx += 1
        if name is None:
            name = 'Bar_' + str(Bar.obj_idx)
        pos_x = (p1.getX() + p2.getX()) / 2
        pos_y = (p1.getY() + p2.getY()) / 2
        self.height = math.fabs(p2.getY() - p1.getY())
        self.length = math.fabs(p2.getX() - p1.getX())
        self.radius = math.sqrt((p2.getX() - p1.getX())**2 + (p2.getY() - p1.getY())**2) / 2
        self.normal_angle = math.tau / 4
        Body.__init__(self, Rectangle(p1, p2), pos_x, pos_y, vel_x_0, .0, name=name, atrito=atrito, kill=kill)
    def get_normal_angle(self, projetil):
        if not self.is_in_collision_zone(projetil):
            return None
        distancia_bola_para_aresta = math.fabs(projetil.pos_y - self.pos_y + self.height / 2)
        if distancia_bola_para_aresta > projetil.radius:
            return None
        return self.normal_angle

class Wall(Body):
    obj_idx = 0
    def __init__(self, p1, p2, name=None, kill=False):
        Wall.obj_idx += 1
        if name is None:
            name = 'Wall_' + str(Wall.obj_idx)
        pos_x = (p2.getX() + p1.getX()) / 2
        pos_y = (p2.getY() + p1.getY()) / 2
        self.radius = math.sqrt((p2.getX() - p1.getX())**2 + (p2.getY() - p1.getY())**2) / 2
        self.normal_angle = math.atan2(p2.getY() - p1.getY(), p2.getX() - p1.getX()) + math.tau / 4
        Body.__init__(self, Line(p1, p2), pos_x, pos_y, name=name, kill=kill)
    def get_normal_angle(self, projetil):
        p1 = self.body.getP1()
        p2 = self.body.getP2()
        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projetil.pos_x - p1.getX()) + b * (projetil.pos_y - p1.getY())) / math.sqrt(a**2 + b**2)
        if distancia_bola_para_aresta > projetil.radius + self.width:
            return None
        # return math.atan(-a/b) + math.tau/4
        return self.normal_angle
    def on_collision(self, projetil):
        if self.kill:
            projetil.vidas -= 1
            if projetil.vidas <= 0:
                return
            projetil.reset()
            time.sleep(1)

################################################################################
####                                  JOGO                                  ####
################################################################################

win = GraphWin("Bolinha com Esteroides", width, height)
win.setCoords(0, 0, width, height)

tilt = 15

linhaSuperior = Wall(Point(dl, height - du), Point(width - dr, height - du), name="Parede_sup")
linhaSuperior.setWidth(10)
linhaSuperior.setFill(color_rgb(10, 100, 10))

linhaInferior = Wall(Point(dl, dd), Point(width - dr, dd), name="Parede_inf", kill=True)
linhaInferior.setWidth(10)
linhaInferior.setFill(color_rgb(10, 100, 10))

linhaEsquerda = Wall(Point(dl - tilt, dd), Point(dl + tilt, height - du), name="Parede_esq")
linhaEsquerda.setWidth(10)
linhaEsquerda.setFill(color_rgb(10, 100, 10))

linhaDireita = Wall(Point(width - dr + tilt, dd), Point(width - dr - tilt, height - du), name="Parede_dir")
linhaDireita.setWidth(10)
linhaDireita.setFill(color_rgb(10, 100, 10))

espaco_branco = Rectangle(Point(0, dd - 2), Point(width, 0))
espaco_branco.setFill('white')
espaco_branco.setOutline('white')

# texto
info_txt = Text(Point(width / 2, 25), '')
info_txt.setSize(14)

# barra
barra = Bar(Point(width/2 - comprimento_barra/2, dd + db + espessura_barra/2),
            Point(width/2 + comprimento_barra/2, dd + db - espessura_barra/2),
            velocidade_barra, atrito=atrito_barra)
barra.setFill(fill_barra)
barra.setOutline(outline_barra)
barra.setWidth(2)

# bolinha
bola = Ball(Point(width/2, height/2), raio_bola, vel_y=vel_inicial, vidas=vidas_iniciais, name="Bolinha")
bola.setFill(fill_bola)
bola.setOutline(outline_bola)
bola.setWidth(2)

# menu
while True:
    win.setBackground('black')
    inicio_txt = Text(Point(width / 2, height / 2), "Aperte qualquer tecla para iniciar\nPressione ESC para sair do jogo")
    inicio_txt.setStyle('bold')
    inicio_txt.setTextColor('white')
    inicio_txt.setSize(32)
    inicio_txt.draw(win)
    tecla = win.getKey()
    if (tecla == 'Escape'):
        break

    # comeca jogo
    win.setBackground('white')
    linhaSuperior.draw(win)
    linhaInferior.draw(win)
    linhaEsquerda.draw(win)
    linhaDireita.draw(win)
    espaco_branco.draw(win)
    bola.draw(win)
    barra.draw(win)
    barra.reset()
    barra.add_obstacle(linhaEsquerda)
    barra.add_obstacle(linhaDireita)
    bola.reset()
    bola.add_obstacle(linhaSuperior)
    bola.add_obstacle(linhaInferior)
    bola.add_obstacle(linhaEsquerda)
    bola.add_obstacle(linhaDireita)
    bola.add_obstacle(barra)
    obstaculos = []
    for i in range(n_obstaculos):  # cria obstaculos
        radius = random.random() * 25 + 25
        center = Point((width - dr - dl - 3*radius) * random.random() + dl + 1.5*radius,
                       (height - du - dd - db - 3*radius) / 3 * random.random() + 2 * (height - du - dd - db - 3*radius) / 3 + dd + db + 1.5 * radius)
        vel_x = random.gauss(0, 2)
        if random.random() < 1.0:  # probabilidade de obstaculo ser um circulo
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
        # obst.add_obstacle(bola)
        obst.add_obstacle(linhaSuperior)
        obst.add_obstacle(linhaInferior)
        obst.add_obstacle(linhaEsquerda)
        obst.add_obstacle(linhaDireita)
        bola.add_obstacle(obst)
        obstaculos.append(obst)
    for obst in obstaculos:
        for obst_2 in obstaculos:
            obst.add_obstacle(obst_2)
    time.sleep(1)

    t_steps = 0
    t = .0
    while True:
        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd') and barra.pos_x < width - dr - comprimento_barra/2:
            barra.vel_x = velocidade_barra
            barra.vel_modulo = velocidade_barra
            barra.vel_angulo = 0
        if (tecla == "Left" or tecla == 'a') and barra.pos_x > dl + comprimento_barra/2:
            barra.vel_x = -velocidade_barra
            barra.vel_modulo = velocidade_barra
            barra.vel_angulo = math.pi
        if (tecla == '') or barra.pos_x >= width - dr - comprimento_barra/2 and barra.vel_x > 0 or barra.pos_x <= dl + comprimento_barra/2 and barra.vel_x < 0:
            barra.vel_x = 0
            barra.vel_modulo = 0
            barra.vel_angulo = 0
        if tecla == "Escape":  # sai do jogo
            bola.vidas = -1

        bola.update()
        barra.update()
        for obst in obstaculos:
            obst.update()

        if bola.vidas <= 0:
            fim_txt = Text(Point(width / 2, height / 2), "GAME\nOVER")
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
            for obst in obstaculos:
                obst.undraw()
                del obst
            bola.vidas = vidas_iniciais
            bola.obstacles = []
            bola.nao_colidiu = []
            bola.n_colisoes = 0
            espaco_branco.undraw()
            bola.undraw()
            barra.undraw()
            break

        if t_steps % 5 == 0:
            info_txt.undraw()
            info_txt.setText("Colisões: " + str(bola.n_colisoes) + "\t\tVidas: " + str(bola.vidas) + "\t\tVelocidade: %.2f" % bola.vel_modulo + "\t\tTempo: %.1f" % t)
            info_txt.draw(win)

        time.sleep(dt)
        t_steps += 1
        t += dt

win.close()
