from bodies import *
idx = 0
width = 960  # largura da tela
height = 640  # altura da tela

du = 40  # distancia da linha superior para o limite superior da tela
dd = 40  # distancia da linha inferior para o limite inferior da tela
dl = 40  # distancia da linha esquerda para o limite esquerdo da tela
dr = 40  # distancia da linha direita para o limite direito da tela
db = 60  # distancia da barra para a linha inferior

raio_bola = 10  # raio da bolinha
vidas_iniciais = 3
fill_bola = (10, 10, 200)  # cor de preenchimento da bolinha
outline_bola = (255, 255, 0)  # cor do contorno da bolinha

n_static_obstacles = 3
n_moving_obstacles = 4
obst_lives = None

comprimento_barra = 100
espessura_barra = 10
velocidade_barra = 1250.0  # velocidade horizontal da barra (pixels/segundo) a cada comando do jogador
fill_barra = (100, 10, 10)  # cor de preenchimento da barra
outline_barra = (255, 255, 0)  # cor do contorno da barra

vel_inicial = 400.0  # velocidade inicial da bolinha, em pixels/segundo
dt = 0.020  # intervalo de tempo entre dois frames do jogo, em segundos

n_obstaculos = 6

################################################################################

win = GraphWin("Bolinha com Esteroides", width, height)
win.setCoords(0, 0, width, height)
inicio_txt = Text(Point(0, 0), "{}\n{}\n{}\n".format('', '', ''))

tilt = 0
rec_menu = Rectangle(Point(0, 0), Point(0, 0))
cir_menu = Circle(Point(0, 0),0)

# barra
barra = Bar((width / 2 - comprimento_barra / 2, dd + db + espessura_barra / 2),
            (width / 2 + comprimento_barra / 2, dd + db - espessura_barra / 2),
            velocidade_barra)
barra.setFill(fill_barra)
barra.setOutline(outline_barra)
barra.setWidth(2)

# bolinha
initial_angle = (2 * random.random() - 1) * math.tau / 8 - math.tau / 4
bola = PunyBall((width / 2, height - du - 50), raio_bola, vel=(vel_inicial * math.cos(initial_angle), vel_inicial * math.sin(initial_angle)),
                 lives=vidas_iniciais, name="Bolinha")
bola.setFill(fill_bola)
bola.setOutline(outline_bola)
bola.setWidth(2)

linhaSuperior = Wall((dl + tilt, height - du), (width - dr - tilt, height - du), name="Parede_sup")
linhaSuperior.setWidth(10)
linhaSuperior.setFill((10, 100, 10))

linhaInferior = Wall((dl - tilt, dd), (width - dr + tilt, dd), name="Parede_inf")
linhaInferior.setWidth(10)
linhaInferior.setFill((10, 100, 10))
bola.add_reaper(linhaInferior)

linhaEsquerda = Wall((dl - tilt, dd), (dl + tilt, height - du), name="Parede_esq")
linhaEsquerda.setWidth(10)
linhaEsquerda.setFill((10, 100, 10))

linhaDireita = Wall((width - dr + tilt, dd), (width - dr - tilt, height - du), name="Parede_dir")
linhaDireita.setWidth(10)
linhaDireita.setFill((10, 100, 10))


# texto
info_txt = Text(Point(width / 2, 20), '')
info_txt.setSize(14)
info_txt.setTextColor('yellow')

################################################################################
####                                  JOGO                                  ####
################################################################################
imagem = Image(Point(width / 2, height / 2), "fundojogo2.png")
imagem.draw(win)

# def apagapol(rec_menu):
#     rec_menu.undraw()

def Poligonos_menu(pse, pid):
    global rec_menu,cir_menu
    rec_menu.undraw()
    cir_menu.undraw()
    rec_menu = Rectangle(pse, pid)
    cir_menu = Circle(Point(pid.getX() + 30, ((pid.getY() - pse.getY()) / 2) + pse.getY()), 10)
    rec_menu.setOutline("yellow")
    cir_menu.setOutline("yellow")
    rec_menu.setWidth(3)
    cir_menu.setWidth(3)
    rec_menu.draw(win)
    cir_menu.draw(win)




def historia():
    win.setBackground('black')
    texto = Text(Point(width / 2, height / 2), '')
    texto.setStyle('bold')
    texto.setTextColor('yellow')
    texto.setSize(26)
    lista_texto = ["No ano de 2050, um gigantesco astro\npassa perto do sistema solar.\nSua massa é tão grande que tira os\n" + \
                    "planetas de sua órbita e, ao arrastá-los,\naprisiona-os numa espécie de campo\nde força.",

                   "Não é só isso. As características \nfísico-químicas dos planetas são alteradas,\nde modo a torná-los elásticos e,\n" + \
                   "em alguns casos, divisíveis.Os planetas,\ndesgovernados, chocam-se aleatoriamente.\nPequena, a Terra está a ponto de\n" + \
                   "ser expelida do campo de força e\nperder-se para sempre no espaço infinito.",

                   "Felizmente, um grupo de cientistas \nda computação havia previsto a catástrofe.\nEles conseguiram escapar do desastre,\n" + \
                   "juntamente com alguns habitantes da Terra.\nVocê é um dos que foram salvos.",

                   "Agora, a sua missão é evitar que o\npequeno planeta azul se perca no Universo,\n" + \
                   "até que a situação se normalize,\nna esperança de um dia regressar a sua terra natal."]
    idx = 0
    while True:
        if idx >= 3:
            break
        texto.undraw()
        texto.setText(lista_texto[idx])
        texto.draw(win)
        tecla = win.getKey()
        if tecla == "Right" or tecla == "Down" or tecla == "Return":
            idx += 1
        elif (tecla == 'Left' or tecla == "Up") and idx > 0:
            idx -= 1
    texto.undraw()



def Iniciar():
    global inicio_txt
    inicio_txt.undraw()
    rec_menu.undraw()
    cir_menu.undraw()
    win.setBackground('white')
    linhaSuperior.draw(win)
    linhaInferior.draw(win)
    linhaEsquerda.draw(win)
    linhaDireita.draw(win)
    # espaco_branco.draw(win)
    barra.reset()
    barra.add_obstacle(linhaEsquerda)
    barra.add_obstacle(linhaDireita)
    bola.reset()
    bola.add_obstacle(linhaSuperior)
    bola.add_obstacle(linhaInferior)
    bola.add_obstacle(linhaEsquerda)
    bola.add_obstacle(linhaDireita)
    bola.add_obstacle(barra)
    static_obstacles = set()
    moving_obstacles = set()
    for i in range(n_static_obstacles):
        n_edges = random.randint(3, 6)
        radius = 30 * random.random() + 30
        angle = math.tau * random.random()
        center = ((width - dr - dl - 3 * radius) * random.random() + dl + 1.5 * radius,
                  (height - du - dd - db - 3 * radius) / 3 * random.random() + \
                  2 * (height - du - dd - db - 3 * radius) / 3 + dd + db + 1.5 * radius)
        obst = RegularPolygon(center, radius, n_edges, angle)
        color_r = random.randrange(0, 256)
        color_g = random.randrange(0, 256)
        color_b = random.randrange(0, 256)
        obst.setFill((color_r, color_g, color_b))
        obst.setOutline(((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
        obst.setWidth(2)
        bola.add_obstacle(obst)
        obst.add_reaper(bola)
        obst.reset()
        obst.draw(win)
        static_obstacles.add(obst)
    for i in range(n_moving_obstacles):
        radius = 30 * random.random() + 30
        center = ((width - dr - dl - 3 * radius) * random.random() + dl + 1.5 * radius,
                  (height - du - dd - db - 3 * radius) / 3 * random.random() + \
                  2 * (height - du - dd - db - 3 * radius) / 3 + dd + db + 1.5 * radius)
        vel_obst_modulus = random.gauss(90, 15)
        vel_obst_angle = random.random() * math.tau
        vel_obst = (vel_obst_modulus * math.cos(vel_obst_angle), vel_obst_modulus * math.sin(vel_obst_angle))
        obst = Ball(center, radius, vel=vel_obst, lives=obst_lives)
        color_r = random.randrange(0, 256)
        color_g = random.randrange(0, 256)
        color_b = random.randrange(0, 256)
        obst.setFill((color_r, color_g, color_b))
        obst.setOutline(((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
        obst.setWidth(2)
        obst.add_obstacle(linhaEsquerda)
        obst.add_obstacle(linhaDireita)
        obst.add_obstacle(linhaInferior)
        obst.add_obstacle(linhaSuperior)
        obst.add_reaper(bola)
        bola.add_obstacle(obst)
        for obst_2 in static_obstacles:
            obst.add_obstacle(obst_2)
        for obst_2 in moving_obstacles:
            obst.add_obstacle(obst_2)
        obst.reset()
        obst.draw(win)
        moving_obstacles.add(obst)
    bola.draw(win)
    barra.draw(win)
    time.sleep(1)

    t_steps = 0
    t = .0
    while True:
        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd') and barra.pos[0] < width - dr - comprimento_barra / 2:
            barra.vel[0] = velocidade_barra
        if (tecla == "Left" or tecla == 'a') and barra.pos[0] > dl + comprimento_barra / 2:
            barra.vel[0] = -velocidade_barra
        if (tecla == '') or barra.pos[0] >= width - dr - comprimento_barra / 2 and barra.vel[0] > 0 or barra.pos[
            0] <= dl + comprimento_barra / 2 and barra.vel[0] < 0:
            barra.vel[0] = 0
        if tecla == "Escape":  # sai do jogo
            bola.lives = -1

        bola.update(dt)
        barra.update(dt)
        for obst in moving_obstacles:
            obst.update(dt)

        if bola.lives <= 0:
            fim_txt = Text(Point(width / 2, height / 2), "Que pena!\n A Terra perdeu-se para\n sempre no espaço.")
            fim_txt.setStyle('bold')
            fim_txt.setTextColor("yellow")
            fim_txt.setSize(32)
            fim_txt.draw(win)
            time.sleep(2)
            fim_txt.undraw()
            info_txt.undraw()
            linhaInferior.undraw()
            linhaSuperior.undraw()
            linhaEsquerda.undraw()
            linhaDireita.undraw()
            for obst in static_obstacles:
                obst.undraw()
                del obst
            for obst in moving_obstacles:
                obst.undraw()
                del obst
            bola.lives = vidas_iniciais
            bola.obstacles = set()
            bola.in_contact = {}
            bola.n_collisions = 0
            # espaco_branco.undraw()
            bola.undraw()
            barra.undraw()
            break

        if t_steps % 5 == 0:
            info_txt.undraw()
            info_txt.setText("Colisões: " + str(bola.n_collisions) + "\t\tVidas: " + str(
                bola.lives) + "\t\tVelocidade: %.2f" % np.linalg.norm(bola.vel) + "\t\tTempo: %.1f" % t)
            info_txt.draw(win)

        time.sleep(dt)
        t_steps += 1
        t += dt


while True:
    historia()
    while True:
        win.setBackground('black')
        iniciar = 'INICIAR'
        ranking = 'RANKING'
        hist = 'HISTÓRIA'
        opcoes = [iniciar, ranking, hist]
        inicio_txt.undraw()
        inicio_txt = Text(Point(width / 2, height / 2), "{}\n{}\n{}\n".format(iniciar, ranking, hist))
        inicio_txt.setStyle('bold')
        inicio_txt.setTextColor('white')
        inicio_txt.setSize(32)
        inicio_txt.draw(win)
        tecla = win.getKey()
        if tecla == "Down":
            idx = (idx + 1) % len(opcoes)
        if tecla == "Up":
            idx = idx - 1 % len(opcoes)
        if idx == 0:
            Poligonos_menu((Point(width / 2 - 100, height / 2 + 55)), (Point((width / 2 + 100), (height / 2 + 105))))


        elif idx == 1:

            Poligonos_menu((Point(width / 2 - 120, height / 2 + 5)), (Point((width / 2 + 120), (height / 2 + 50))))


        elif idx == 2:

            Poligonos_menu((Point(width / 2 - 110, height / 2 - 60)), (Point((width / 2 + 110), (height / 2 + 5))))


        if tecla == "Return" and idx == 0:
            Iniciar()
        if tecla == "Return" and idx == 2:
            rec_menu.undraw()
            cir_menu.undraw()
            inicio_txt.undraw()
            historia()

        if tecla == 'Escape':
            break
    break
win.close()

