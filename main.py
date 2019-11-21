from graphics import *
import random
import math
import numpy as np
from bodies import *

dt = 0.020

# ################################################################################
# ####                                  JOGO                                  ####
# ################################################################################

jogo = Game()
win = jogo.window

info_txt = Text(Point(jogo.win_width/2, jogo.dd/2), '')
info_txt.setSize(14)

# # menu
while True:
    win.setBackground('black')
    inicio_txt = Text(Point(jogo.win_width / 2, jogo.win_height / 2), "Aperte qualquer tecla para iniciar\nPressione ESC para sair do jogo")
    inicio_txt.setStyle('bold')
    inicio_txt.setTextColor('white')
    inicio_txt.setSize(32)
    inicio_txt.draw(win)
    tecla = win.getKey()
    if (tecla == 'Escape'):
        break

    # comeca jogo
    jogo.reset()
    time.sleep(1)

    t_steps = 0
    t = .0
    while True:
        # movimento horizontal da barra pelas setas direita/esquerda
        tecla = win.checkKey()
        if (tecla == "Right" or tecla == 'd') and jogo.bar.pos[0] < jogo.win_width - jogo.dr - jogo.bar_length/2:
            jogo.bar.vel[0] = jogo.vel_bar
        if (tecla == "Left" or tecla == 'a') and jogo.bar.pos[0] > jogo.dl + jogo.bar_length/2:
            jogo.bar.vel[0] = -jogo.vel_bar
        if (tecla == '') or jogo.bar.pos[0] >= jogo.win_width - jogo.dr - jogo.bar_length/2 and jogo.bar.vel[0] > 0 or \
          jogo.bar.pos[0] <= jogo.dl + jogo.bar_length/2 and jogo.bar.vel[0] < 0:
            jogo.bar.vel[0] = 0
        if tecla == "Escape":  # sai do jogo
            jogo.ball.lives = -1

        jogo.update(dt)

        if jogo.ball.lives <= 0:
            fim_txt = Text(Point(jogo.win_width / 2, jogo.win_height / 2), "GAME\nOVER")
            fim_txt.setStyle('bold')
            fim_txt.setSize(32)
            fim_txt.draw(win)
            time.sleep(2)
            fim_txt.undraw()
            info_txt.undraw()
            jogo.clear()
            break

        if t_steps % 5 == 0:
            info_txt.undraw()
            info_txt.setText("Colisões: " + str(jogo.ball.n_collisions) + "\t\tVidas: " + str(jogo.ball.lives) + \
                             "\t\tVelocidade: %.2f" % np.linalg.norm(jogo.ball.vel) + "\t\tTempo: %.1f" % t)
            info_txt.draw(win)

        time.sleep(dt)
        t_steps += 1
        t += dt

win.close()
