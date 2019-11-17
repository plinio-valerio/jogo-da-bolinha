from graphics import *
import random
import math
import numpy as np

width = 960  # largura da tela
height = 640  # altura da tela

du = 40  # distancia da linha superior para o limite superior da tela
dd = 40  # distancia da linha inferior para o limite inferior da tela
dl = 40  # distancia da linha esquerda para o limite esquerdo da tela
dr = 40  # distancia da linha direita para o limite direito da tela
db = 60  # distancia da barra para a linha inferior

raio_bola = 12  # raio da bolinha
vidas_iniciais = 3
fill_bola = color_rgb(10, 10, 100)  # cor de preenchimento da bolinha
outline_bola = color_rgb(255, 255, 0)  # cor do contorno da bolinha

comprimento_barra = 100
espessura_barra = 10
velocidade_barra = 20.0  # passo horizontal da barra a cada comando do jogador
fill_barra = color_rgb(100, 10, 10)  # cor de preenchimento da barra
outline_barra = color_rgb(255, 255, 0)  # cor do contorno da barra


pontos_por_fase = 3  # quantidade de pontos necessaria para acelerar a bolinha
vel_inicial = 6.0  # velocidade inicial da bolinha
dt = 0.020  # intervalo de tempo entre dois frames do jogo

n_obstaculos = 5

###################

class Body:
    obj_idx = 0
    def __init__(self, body, mass, radius, pos_x, pos_y, vel_x=.0, vel_y=.0, name=None, lives=3, kill=False):
        Body.obj_idx += 1
        self.repr = 'Body_' + str(Body.obj_idx)
        if name is None:
            self.name = self.repr
        else:
            self.name = name
        self.body = body
        self.pos = np.array([pos_x, pos_y])
        self.pos_0 = self.pos.copy()
        self.vel = np.array([vel_x, vel_y])
        self.vel_0 = self.vel.copy()
        self.lives = lives
        self.kill = kill
        self.mass = mass
        self.radius = radius
        self.obstacles = set()
        self.in_contact = {}
        self.width = 1
        self.n_collisions = 0
    def reset(self):
        delta = self.pos_0 - self.pos
        self.body.move(delta[0], delta[1])
        np.copyto(self.pos, self.pos_0)
        np.copyto(self.vel, self.vel_0)
    def update(self, dt=1):
        delta = self.vel * dt
        self.pos += delta
        self.body.move(delta[0], delta[1])
        for obst in enumerate(self.obstacles):
            if self.in_contact[obst.repr]:
                collision_angle = obstacle.get_normal_angle(self)
                if collision_angle is None:
                    self.in_contact[obst.repr] = False
                    obst.in_contact[self.repr] = False
            else:
                touched = self.collide(obst)
                if touched:
                    self.n_collisions += 1
                    obst.n_collisions += 1
                self.in_contact[obst.repr] = touched
                obst.in_contact[self.repr] = touched
    def collide(self, obstacle):
        collision_angle = obstacle.get_normal_angle(self)
        if collision_angle is None:
            return False
        m_a = self.mass
        m_b = obstacle.mass
        vel_a = self.vel.copy()
        vel_b = obstacle.vel.copy()

        # STEP 0: change reference frame so that obstacle has velocity 0
        #         and its post-collision vel_y is zero (i.e. rotate space so that the collision angle is 0)
        translation_vector = vel_b.copy()
        matrix_0 = np.array([[math.cos(-collision_angle), -math.sin(-collision_angle)],
                             [math.sin(-collision_angle),  math.cos(-collision_angle)]])
        matrix_0_inv = np.array([[math.cos(collision_angle), -math.sin(collision_angle)],
                                 [math.sin(collision_angle),  math.cos(collision_angle)]])
        vel_a -= translation_vector
        vel_b -= translation_vector  # == [.0, .0]
        vel_a = np.dot(matrix_0, vel_a)

        if m_a / m_b == .0:
            vel_a[0] *= -1.0
            vel_a = np.dot(matrix_0_inv, vel_a)
            vel_a += translation_vector
            self.vel = vel_a.copy()
            return True
        if m_b / m_a == .0:
            # changes reference frame temporarily so that body A is standing still
            vel_b -= vel_a
            vel_b[0] *= -1.0  # collision angle is still 0
            vel_b += vel_a
            vel_b = np.dot(matrix_0_inv, vel_b)
            vel_b += translation_vector
            obstacle.vel = vel_b.copy()
            return True

        # STEP 1: adopt coordinate system in which the x and y axes represent the post-collision velocities of bodies A and B, respectively;
        #         scale coordinate system (by the square root of the masses) so that conservation of energy yields a circumference.

        # Conservation of momentum:  m_a * x  + m_b * y  = m_a * vel_a_x
        # Conservation of energy:    m_a * x² + m_b * y² = m_a * vel_a_x²
        solution = np.array([vel_a[0], .0])  # pre-collision solution

        matrix_1 = np.array([[1.0/math.sqrt(m_a), .0],
                             [.0, 1.0/math.sqrt(m_b)]])
        matrix_1_inv = np.array([[math.sqrt(m_a), .0],
                                 [.0, math.sqrt(m_b)]])
        solution = np.dot(matrix_1, solution)

        # STEP 2: rotate coordinate system so that conservation of momentum yields a line parallel to the x axis
        line_angle = math.atan(-sqrt(m_a/m_b))
        matrix_2 = np.array([[math.cos(-line_angle), -math.sin(-line_angle)],
                             [math.sin(-line_angle),  math.sin(-line_angle)]])
        matrix_2_inv = np.array([[math.cos(line_angle), -math.sin(line_angle)],
                                 [math.sin(line_angle),  math.sin(line_angle)]])
        solution = np.dot(matrix_2, solution)

        # Under the new coordinate system, the 2 solutions to the conservation equations are symmetric wrt y axis

        solution[0] *= -1.0  # post-collision solution
        solution = np.dot(matrix_2_inv, solution)
        solution = np.dot(matrix_1_inv, solution)

        vel_a[0] = solution[0]
        vel_b[0] = solution[1]
        vel_a = np.dot(matrix_0_inv, vel_a)
        vel_b = np.dot(matrix_0_inv, vel_b)
        vel_a += translation_vector
        vel_b += translation_vector
        self.vel = vel_a.copy()
        obstacle.vel = vel_b.copy()
        return True
    def within_collision_distance(self, obstacle):
        distance = np.norm(self.pos - obstacle.pos)
        if distance > obstacle.radius + self.radius:
            return False
        return True
    def get_normal_angle(self, corpo):
        raise NotImplementedError
    def add_obstacle(self, body):
        self.obstacles.add(body)
        body.obstacles.add(self)
        self.in_contact[body.repr] = False
        body.in_contact[self.repr] = False
    def on_collision(self, projetil):
        if self.kill:
            projetil.vidas -= 1
            projetil.on_death()
    def on_death(self):
        self.reset()
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
    def __init__(self, center, radius, vel_x=.0, vel_y=.0, name=None, mass=None, lives=1, kill=False):
        Ball.obj_idx += 1
        if name is None:
            name = 'Ball_' + str(Ball.obj_idx)
        if mass is None:
            mass = math.pi * radius**2
        Body.__init__(self, body=Circle(center, radius), mass=mass, radius=radius, pos_x=center.getX(), pos_y=center.getY(), vel_x=vel_x, vel_y=vel_y, name=name, lives=lives, kill=kill)
    def get_normal_angle(self, projectile):
        return math.atan2(projectile.pos_y - self.pos_y, projectile.pos_x - self.pos_x)

class RegularPolygon(Body):
    obj_idx = 0
    def __init__(self, center, radius, n_edges, angle=.0, name=None, lives=1, kill=False):
        RegularPolygon.obj_idx += 1
        if name is None:
            name = 'Poly_' + str(RegularPolygon.obj_idx)
        self.n_edges = int(n_edges)
        self.angle = angle % (math.tau / self.n_edges)
        self.vertices = [Point(center.getX() + radius * math.cos(self.angle + i * math.tau / self.n_edges),
                               center.getY() + radius * math.sin(self.angle + i * math.tau / self.n_edges)) for i in range(self.n_edges)]
        poly = Polygon(self.vertices)
        Body.__init__(self, body=poly, mass=math.inf, radius=radius, pos_x=center.getX(), pos_y=center.getY(), name=name, lives=lives, kill=kill)
    def get_normal_angle(self, projectile, verbose=False):
        if not self.is_in_collision_zone(projectile):
            return None
        angulo_entre_vertices = math.tau / self.n_lados
        angulo = math.atan2(projetil.pos_y - self.pos_y, projetil.pos_x - self.pos_x) - self.angle
        idx_v = int(angulo // angulo_entre_vertices)
        p1 = self.vertices[idx_v]
        p2 = self.vertices[(idx_v - 1) % self.n_lados]

        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projectile.pos_x - p1.getX()) + b * (projectile.pos_y - p1.getY())) / math.sqrt(a**2 + b**2)

        if verbose:
            print("Evento: possivel colisao")
            print("\tProjetil:", projectile.name, "\t== (%d, %d)" % (projectile.pos_x, projectile.pos_y))
            print("\tObstaculo:", self.name)
            print("\tAngulo do poligono: %d" % int(self.angle / math.tau * 360))
            print("\tAngulo do projetil: %d" % int(angulo / math.tau * 360))
            print("\tVertices:  ", [(int(v.getX()), int(v.getY())) for v in self.vertices])
            print("\tDistancias:", ["  %.2f" % math.sqrt((projectile.pos_x - v.getX())**2 + (projectile.pos_y - v.getY())**2) for v in self.vertices])
            print("\tp1: (%d, %d)" % (p1.getX(), p1.getY()))
            print("\tp2: (%d, %d)" % (p2.getX(), p2.getY()))
            print("\ta = %.2f" % a)
            print("\tb = %.2f" % b)
            print("\tdist = %.2f" % distancia_bola_para_aresta)

        if distancia_bola_para_aresta > projectile.radius:
            return None
        # return math.atan(-a/b) + math.tau/4
        return angulo // angulo_entre_vertices * angulo_entre_vertices + self.angle + angulo_entre_vertices / 2
        # angulo_entre_vertices = math.tau / self.n_lados
        # angulo = math.atan2(y, x) - self.angle
        # return angulo // angulo_entre_vertices * angulo_entre_vertices + angulo_entre_vertices / 2

class Bar(Body):
    obj_idx = 0
    def __init__(self, p1, p2, passo, name=None):
        Bar.obj_idx += 1
        if name is None:
            name = 'Bar_' + str(Bar.obj_idx)
        pos_x = (p1.getX() + p2.getX()) / 2
        pos_y = (p1.getY() + p2.getY()) / 2
        self.height = math.fabs(p2.getY() - p1.getY())
        self.length = math.fabs(p2.getX() - p1.getX())
        radius = math.sqrt((p2.getX() - p1.getX())**2 + (p2.getY() - p1.getY())**2) / 2
        self.normal_angle = math.tau / 4
        Body.__init__(self, body=Rectangle(p1, p2), mass=math.inf, radius=radius, pos_x=pos_x, pos_y=pos_y, name=name)
    def get_normal_angle(self, projectile):
        if not self.is_in_collision_zone(projectile):
            return None
        ball_to_edge_distance = math.fabs(projectile.pos_y - self.pos_y + self.height / 2)
        if ball_to_edge_distance > projectile.radius:
            return None
        return self.normal_angle

class Wall(Body):
    obj_idx = 0
    def __init__(self, p1, p2, name=None, lives=1, kill=False):
        Wall.obj_idx += 1
        if name is None:
            name = 'Wall_' + str(Wall.obj_idx)
        pos_x = (p2.getX() + p1.getX()) / 2
        pos_y = (p2.getY() + p1.getY()) / 2
        radius = math.sqrt((p2.getX() - p1.getX())**2 + (p2.getY() - p1.getY())**2) / 2
        self.normal_angle = math.atan2(p2.getY() - p1.getY(), p2.getX() - p1.getX()) + math.tau / 4
        Body.__init__(self, body=Line(p1, p2), mass=math.inf, radius=radius, pos_x=pos_x, pos_y=pos_y, name=name, lives=lives, kill=kill)
    def get_normal_angle(self, projectile):
        p1 = self.body.getP1()
        p2 = self.body.getP2()
        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projectile.pos_x - p1.getX()) + b * (projectile.pos_y - p1.getY())) / math.sqrt(a**2 + b**2)
        if distancia_bola_para_aresta > projectile.radius + self.width:
            return None
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

tilt = 0

linhaSuperior = Wall(Point(dl + tilt, height - du), Point(width - dr - tilt, height - du), name="Parede_sup")
linhaSuperior.setWidth(10)
linhaSuperior.setFill(color_rgb(10, 100, 10))

linhaInferior = Wall(Point(dl - tilt, dd), Point(width - dr + tilt, dd), name="Parede_inf", kill=True)
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
            velocidade_barra)
barra.setFill(fill_barra)
barra.setOutline(outline_barra)
barra.setWidth(2)

# bolinha
initial_angle = (2*random.random() - 1) * math.tau / 4 + math.tau / 4
bola = Ball(Point(width/2, height/2), raio_bola, vel_x=vel_inicial*math.cos(initial_angle), vel_y=vel_inicial*math.sin(initial_angle), lives=vidas_iniciais, name="Bolinha")
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
        if random.random() < 0.8:  # probabilidade de obstaculo ser um circulo
            vel_x = random.gauss(0, 2)
            vel_y = random.gauss(0, 1)
            obst = Ball(center, radius, vel_x=vel_x, vel_y=vel_y)
        else:
            n_lados = random.randint(3, 8)
            angulo = random.random() * math.tau / n_lados
            obst = RegularPolygon(center, radius, n_lados, angulo)
        color_r = random.randrange(0, 256)
        color_g = random.randrange(0, 256)
        color_b = random.randrange(0, 256)
        obst.setFill(color_rgb(color_r, color_g, color_b))
        obst.setOutline(color_rgb((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
        obst.setWidth(2)
        obst.draw(win)
        obst.add_obstacle(bola)
        obst.add_obstacle(linhaSuperior)
        obst.add_obstacle(linhaInferior)
        obst.add_obstacle(linhaEsquerda)
        obst.add_obstacle(linhaDireita)
        for obst_2 in obstaculos:
            obst.add_obstacle(obst_2)
        obstaculos.append(obst)
    time.sleep(1)

    t_steps = 0
    t = .0
    while True:
        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd') and barra.pos_x < width - dr - comprimento_barra/2:
            barra.vel[0] = velocidade_barra
        if (tecla == "Left" or tecla == 'a') and barra.pos_x > dl + comprimento_barra/2:
            barra.vel[0] = -velocidade_barra
        if (tecla == '') or barra.pos_x >= width - dr - comprimento_barra/2 and barra.vel_x > 0 or barra.pos_x <= dl + comprimento_barra/2 and barra.vel_x < 0:
            barra.vel[0] = 0
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
            bola.lives = vidas_iniciais
            bola.obstacles = set()
            bola.in_contact = {}
            bola.n_collisions = 0
            espaco_branco.undraw()
            bola.undraw()
            barra.undraw()
            break

        if t_steps % 5 == 0:
            info_txt.undraw()
            info_txt.setText("Colisões: " + str(bola.n_collisions) + "\t\tVidas: " + str(bola.lives) + "\t\tVelocidade: %.2f" % np.norm(bola.vel) + "\t\tTempo: %.1f" % t)
            info_txt.draw(win)

        time.sleep(dt)
        t_steps += 1
        t += dt

win.close()
