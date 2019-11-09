from graphics import *
import random
import math

width = 800  # largura da tela
height = 600  # altura da tela

du = 40  # distancia da linha superior para o limite superior da tela
dd = 50  # distancia da linha inferior para o limite inferior da tela
db = 30  # distancia da barra para a linha inferior

col = .0
lin = .0
raio = 10  # raio da bolinha
spawn_point = Point(width/2, height/2)  # ponto de spawn da bolinha
fill_bola = color_rgb(10, 10, 100)  # cor de preenchimento da bolinha
outline_bola = color_rgb(255, 255, 0)  # cor do contorno da bolinha

passo_barra = 25  # passo horizontal da barra a cada comando do jogador
fill_barra = color_rgb(100, 10, 10)  # cor de preenchimento da barra
outline_barra = color_rgb(255, 255, 0)  # cor do contorno da barra
comprimento_barra = 100
espessura_barra = 10
colIni = width/2 - comprimento_barra/2  # coordenada x do inicio (esquerda) da barra

pontos_por_fase = 3  # quantidade de pontos necessaria para acelerar a bolinha
vel_inicial = 6.0  # velocidade inicial da bolinha
vel_x = .0
vel_y = .0
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

def distance(p1, p2):
    return math.sqrt((p1.getX() - p2.getX())**2 + (p1.getY() - p2.getY())**2)

win = GraphWin("Bolinha...", width, height)
win.setCoords(0, 0, width, height)

linhaSuperior = Line(Point(0, height - du), Point(width, height - du))
linhaSuperior.setWidth(10)
linhaSuperior.setFill(color_rgb(10, 100, 10))

linhaInferior = Line(Point(0, dd), Point(width, dd))
linhaInferior.setWidth(3)
linhaInferior.setFill(color_rgb(10, 100, 10))

espaco_branco = Rectangle(Point(0, dd - 2), Point(width, 0))
espaco_branco.setFill('white')
espaco_branco.setOutline('white')

# bolinha
bola = Circle(spawn_point, raio)
bola.setFill(fill_bola)
bola.setOutline(outline_bola)
bola.setWidth(2)
def reseta_bola():
    bola.undraw()
    posicao = bola.getCenter()
    pos_x = posicao.getX()
    pos_y = posicao.getY()
    bola.move(spawn_point.getX() - pos_x, spawn_point.getY() - pos_y)
    bola.draw(win)

# texto
info_txt = Text(Point(width / 2, 25), '')
info_txt.setSize(14)
def atualiza_texto():
    info_txt.undraw()
    info_txt.setText("Pontos: " + str(pontos) + "\t\tVidas: " + str(vidas) + "\t\tVelocidade: %.2f" % math.sqrt(vel_x**2 + vel_y**2))
    info_txt.draw(win)

# barra
barra = Rectangle(Point(colIni, dd + db + espessura_barra),
                  Point(colIni + comprimento_barra, dd + db))
barra.setFill(fill_barra)
barra.setOutline(outline_barra)
barra.setWidth(2)
def reseta_barra():
    barra.undraw()
    posicao = barra.getP1().getX() + comprimento_barra/2
    barra.move(width/2 - posicao, 0)
    barra.draw(win)

# calcula nova velocidade da bolinha apos colisao com plano de angulo normal especificado em radianos
def colisao(vel_x, vel_y, angulo_normal):
    vel_mod = math.sqrt(vel_x**2 + vel_y**2)
    vel_ang = math.atan2(vel_y, vel_x)
    # angulo_novo = -(vel_ang + math.tau/4 - angulo_normal) - (math.tau/4 - angulo_normal)
    angulo_novo = 2*angulo_normal - vel_ang - math.pi
    vel_x_nova = vel_mod * math.cos(angulo_novo)
    vel_y_nova = vel_mod * math.sin(angulo_novo)
    return vel_x_nova, vel_y_nova

def colisao_aleatoria(vel_x, vel_y, angulo_normal=math.tau/4, std=math.tau/24):
    vel_mod = math.sqrt(vel_x**2 + vel_y**2)
    vel_ang = math.atan2(vel_y, vel_x)
    angulo_novo = 2*angulo_normal - vel_ang - math.pi
    incremento_aleatorio = random.gauss(0, std)
    angulo_novo_com_incremento = angulo_novo + incremento_aleatorio
    print("Angulo novo:", angulo_novo)
    print("Incremento:", incremento_aleatorio)
    print("Angulo novo com incremento:", angulo_novo_com_incremento - angulo_normal)
    # garante que o angulo novo nao faz a bola atravessar a parede ou mudar de direcao:
    if math.fabs(angulo_novo_com_incremento - angulo_normal) < math.tau/4 and sign(angulo_novo_com_incremento - angulo_normal) == sign(angulo_novo - angulo_normal):
        angulo_novo = angulo_novo_com_incremento
    vel_x_nova = vel_mod * math.cos(angulo_novo)
    vel_y_nova = vel_mod * math.sin(angulo_novo)
    return vel_x_nova, vel_y_nova

def gera_poligono(n_lados, raio_poligono=40):
    centro = Point( width * random.random(),
                    (height - dd - db - du) / 3 * random.random() + 2 * (height - dd - db - du) / 3 + dd + db)
    angulo_poligono = random.random() * math.tau / n_lados
    vertices = [Point(centro.getX() + raio_poligono * math.cos(angulo_poligono + i * math.tau / n_lados),
                      centro.getY() + raio_poligono * math.sin(angulo_poligono + i * math.tau / n_lados)) for i in range(n_lados)]
    poli = Polygon(vertices)
    color_r = random.randrange(0, 256)
    color_g = random.randrange(0, 256)
    color_b = random.randrange(0, 256)
    poli.setFill(color_rgb(color_r, color_g, color_b))
    poli.setOutline(color_rgb((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
    poli.setWidth(2)
    return poli

def computa_colisao(poligono_regular, vel_x, vel_y):
    vertices = poligono_regular.getPoints()
    # calcula centro e raio do poligono
    centro_x = .0
    centro_y = .0
    for p in vertices:
        centro_x += p.getX()
        centro_y += p.getY()
    centro_x /= len(vertices)
    centro_y /= len(vertices)
    raio_poligono = math.sqrt((vertices[0].getX() - centro_x)**2 + (vertices[0].getY() - centro_y)**2)
    if math.sqrt((col - centro_x)**2 + (lin - centro_y)**2) - raio > raio_poligono:
        return vel_x, vel_y
    for idx, p1 in enumerate(vertices):
        p2 = vertices[(idx + 1) % len(vertices)]
        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (col - p1.getX()) + b * (lin - p1.getY())) / math.sqrt(a**2 + b**2)
        if distancia_bola_para_aresta < raio:
            return colisao(vel_x, vel_y, math.atan(-a/b) + math.tau/4)
    return vel_x, vel_y

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
    espaco_branco.draw(win)
    vel_ang = math.tau/4 + math.tau/8 * (2*random.random() - 1)
    vel_x = vel_inicial * math.cos(vel_ang)
    vel_y = vel_inicial * math.sin(vel_ang)
    ainda_nao_somou_ponto = True  # evita que se somem varios pontos quando a barra acerta a bolinha de lado
    reseta_barra()
    reseta_bola()
    atualiza_texto()
    poligonos = [gera_poligono(i+3) for i in range(n_obstaculos)]
    for poli in poligonos:
        poli.draw(win)
    time.sleep(1)

    while True:
        bola.move(vel_x, vel_y)
        centro_bola = bola.getCenter()
        lin = centro_bola.getY()
        col = centro_bola.getX()
        colIni = barra.getP1().getX()

        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd') and colIni + comprimento_barra + passo_barra <= width:
            barra.move(passo_barra, 0)
        if (tecla == "Left" or tecla == 'a') and colIni - passo_barra >= 0:
            barra.move(-passo_barra, 0)

        # sair do jogo
        if tecla == "Escape":
            game_over()
            break

        # nao deixar a bolinha sair da tela
        for poli in poligonos:
            vel_x, vel_y = computa_colisao(poli, vel_x, vel_y)
        if col < raio or col > width - raio:  # bateu nas paredes laterais
            vel_x, vel_y = colisao(vel_x, vel_y, 0)
        if lin > height - du - raio - 10:  # bateu na linha de cima
            vel_x, vel_y = colisao(vel_x, vel_y, math.tau/4)
        if col > colIni and col < colIni + comprimento_barra and lin < barra.getP1().getY() + raio and lin > barra.getP2().getY():  # bateu na barra
            if ainda_nao_somou_ponto:
                vel_x, vel_y = colisao_aleatoria(vel_x, vel_y)
                pontos += 1
                if pontos % pontos_por_fase == 0:
                    win.setBackground(color_rgb(random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256)))
                    vel_x *= 1.2
                    vel_y *= 1.2
                atualiza_texto()
                ainda_nao_somou_ponto = False
        else:  # bola nao esta em contato com a barra
            ainda_nao_somou_ponto = True
        if lin < dd + raio:  # bateu na linha de baixo (morreu)
            vidas -= 1
            if vidas == 0:
                game_over()
                break
            vel_mod = math.sqrt(vel_x**2 + vel_y**2)
            vel_ang = math.tau/4 + math.tau/8 * (2*random.random() - 1)
            vel_x = (vel_inicial + vel_mod) / 2 * math.cos(vel_ang)
            vel_y = (vel_inicial + vel_mod) / 2 * math.sin(vel_ang)
            reseta_bola()
            reseta_barra()
            atualiza_texto()
            time.sleep(1)

        time.sleep(dt)

win.close()
