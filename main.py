from graphics import *
import random
import math
import numpy as np
from bodies import *

width = 960  # largura da tela
height = 640  # altura da tela

du = 40  # distancia da linha superior para o limite superior da tela
dd = 40  # distancia da linha inferior para o limite inferior da tela
dl = 40  # distancia da linha esquerda para o limite esquerdo da tela
dr = 40  # distancia da linha direita para o limite direito da tela
db = 60  # distancia da barra para a linha inferior

raio_bola = 10  # raio da bolinha
vidas_iniciais = 3
fill_bola = color_rgb(10, 10, 100)  # cor de preenchimento da bolinha
outline_bola = color_rgb(255, 255, 0)  # cor do contorno da bolinha

comprimento_barra = 100
espessura_barra = 10
velocidade_barra = 1000.0  # velocidade horizontal da barra (pixels/segundo) a cada comando do jogador
fill_barra = color_rgb(100, 10, 10)  # cor de preenchimento da barra
outline_barra = color_rgb(255, 255, 0)  # cor do contorno da barra


pontos_por_fase = 3  # quantidade de pontos necessaria para acelerar a bolinha
vel_inicial = 400.0  # velocidade inicial da bolinha, em pixels/segundo
dt = 0.020  # intervalo de tempo entre dois frames do jogo, em segundos

n_obstaculos = 6

################################################################################

win = GraphWin("Bolinha com Esteroides", width, height)
win.setCoords(0, 0, width, height)

tilt = 0

linhaSuperior = Wall((dl + tilt, height - du), (width - dr - tilt, height - du), name="Parede_sup")
linhaSuperior.setWidth(10)
linhaSuperior.setFill(color_rgb(10, 100, 10))

linhaInferior = Wall((dl - tilt, dd), (width - dr + tilt, dd), name="Parede_inf")
linhaInferior.setWidth(10)
linhaInferior.setFill(color_rgb(10, 100, 10))

linhaEsquerda = Wall((dl - tilt, dd), (dl + tilt, height - du), name="Parede_esq")
linhaEsquerda.setWidth(10)
linhaEsquerda.setFill(color_rgb(10, 100, 10))

linhaDireita = Wall((width - dr + tilt, dd), (width - dr - tilt, height - du), name="Parede_dir")
linhaDireita.setWidth(10)
linhaDireita.setFill(color_rgb(10, 100, 10))

espaco_branco = Rectangle(Point(0, dd - 2), Point(width, 0))
espaco_branco.setFill('white')
espaco_branco.setOutline('white')

# texto
info_txt = Text(Point(width / 2, 25), '')
info_txt.setSize(14)

# barra
barra = Bar((width/2 - comprimento_barra/2, dd + db + espessura_barra/2),
            (width/2 + comprimento_barra/2, dd + db - espessura_barra/2))
barra.setFill(fill_barra)
barra.setOutline(outline_barra)
barra.setWidth(2)

# bolinha
initial_angle = (2*random.random() - 1) * math.tau / 8 + math.tau / 4
bola = PunyBall((width/2, height/2), raio_bola, vel=(vel_inicial*math.cos(initial_angle), vel_inicial*math.sin(initial_angle)), lives=vidas_iniciais, name="Bolinha")
bola.setFill(fill_bola)
bola.setOutline(outline_bola)
bola.setWidth(2)

################################################################################
####                                  JOGO                                  ####
################################################################################

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
    barra.reset()
    # barra.add_obstacle(linhaEsquerda)
    # barra.add_obstacle(linhaDireita)
    bola.reset()
    bola.add_obstacle(linhaSuperior)
    bola.add_obstacle(linhaInferior)
    bola.add_obstacle(linhaEsquerda)
    bola.add_obstacle(linhaDireita)
    bola.add_obstacle(barra)
    bola.add_reaper(linhaInferior)
    obstaculos = []
    for i in range(n_obstaculos):  # cria obstaculos
        radius = random.random() * 30 + 30
        center = ((width - dr - dl - 3*radius) * random.random() + dl + 1.5*radius,
                  (height - du - dd - db - 3*radius) / 3 * random.random() + 2 * (height - du - dd - db - 3*radius) / 3 + dd + db + 1.5 * radius)
        if random.random() < 0.5:  # probabilidade de obstaculo ser um circulo
            vel_x = random.gauss(0, 100)
            vel_y = random.gauss(0, 50)
            obst = Ball(center, radius, vel=(vel_x, vel_y), lives=3)
            obst.add_obstacle(linhaSuperior)
            obst.add_obstacle(linhaInferior)
            obst.add_obstacle(linhaEsquerda)
            obst.add_obstacle(linhaDireita)
            for obst_2 in obstaculos:
                obst.add_obstacle(obst_2)
        else:
            n_lados = random.randint(3, 8)
            angulo = random.random() * math.tau / n_lados
            obst = RegularPolygon(center, radius, n_lados, angulo, lives=3)
        color_r = random.randrange(0, 256)
        color_g = random.randrange(0, 256)
        color_b = random.randrange(0, 256)
        obst.setFill(color_rgb(color_r, color_g, color_b))
        obst.setOutline(color_rgb((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
        obst.setWidth(2)
        bola.add_obstacle(obst)
        obst.add_reaper(bola)
        obst.draw(win)
        obstaculos.append(obst)
    bola.draw(win)
    barra.draw(win)
    time.sleep(1)

    t_steps = 0
    t = .0
    while True:
        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd') and barra.pos[0] < width - dr - comprimento_barra/2:
            barra.vel[0] = velocidade_barra
        if (tecla == "Left" or tecla == 'a') and barra.pos[0] > dl + comprimento_barra/2:
            barra.vel[0] = -velocidade_barra
        if (tecla == '') or barra.pos[0] >= width - dr - comprimento_barra/2 and barra.vel[0] > 0 or barra.pos[0] <= dl + comprimento_barra/2 and barra.vel[0] < 0:
            barra.vel[0] = 0
        if tecla == "Escape":  # sai do jogo
            bola.lives = -1

        bola.update(dt)
        barra.update(dt)
        for obst in obstaculos:
            obst.update(dt)

        if bola.lives <= 0:
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
            info_txt.setText("Colisões: " + str(bola.n_collisions) + "\t\tVidas: " + str(bola.lives) + "\t\tVelocidade: %.2f" % np.linalg.norm(bola.vel) + "\t\tTempo: %.1f" % t)
            info_txt.draw(win)

        time.sleep(dt)
        t_steps += 1
        t += dt

win.close()
