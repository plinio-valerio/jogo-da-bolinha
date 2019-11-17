from graphics import *
import math
import numpy as np

class Body:
    obj_idx = 0
    def __init__(self, body, mass, radius, pos_x, pos_y, vel_x=.0, vel_y=.0, name=None, lives=3, kill=False):
        assert mass >= .0
        assert radius > .0
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
    def update(self, dt=1.0):
        assert dt > .0
        delta = self.vel * dt
        self.pos += delta
        self.body.move(delta[0], delta[1])
        for obst in self.obstacles:
            if self.in_contact[obst.repr]:
                collision_angle = obst.get_normal_angle(self)
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
    def collide(self, obstacle, verbose=False):
        assert isinstance(obstacle, Body)
        collision_angle = obstacle.get_normal_angle(self)
        if collision_angle is None:
            return False
        m_a = self.mass
        m_b = obstacle.mass
        vel_a = self.vel.copy()
        vel_b = obstacle.vel.copy()
        if verbose:
            print("EVENT: collision")
            print("\tBody A:", self.name)
            print("\tBody B:", obstacle.name)
            print("\tCollision angle: %.4f" % collision_angle)
            print("\tm_a = %.2f" % m_a)
            print("\tm_b = %.2f" % m_b)
            print("\tPre-collision velocity (A):", vel_a)
            print("\tPre-collision velocity (B):", vel_b)
            print("\t\tPre-collision total momentum:", m_a * vel_a + m_b * vel_b)
            print("\t\tPre-collision total energy:", 0.5 * m_a * np.linalg.norm(vel_a)**2 + 0.5 * m_b * np.linalg.norm(vel_b)**2)

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

        matrix_1 = np.array([[math.sqrt(m_a),        .0      ],
                             [     .0,         math.sqrt(m_b)]])
        matrix_1_inv = np.array([[1.0/math.sqrt(m_a),           .0        ],
                                 [       .0,            1.0/math.sqrt(m_b)]])
        solution = np.dot(matrix_1, solution)

        # STEP 2: rotate coordinate system so that conservation of momentum yields a line parallel to the x axis
        # Conservation of momentum:  ²m_a * x  + ²m_b * y  = m_a * vel_a_x
        # Conservation of energy:    x² + y² = m_a * vel_a_x²
        line_angle = math.atan(-math.sqrt(m_a/m_b))
        matrix_2 = np.array([[math.cos(-line_angle), -math.sin(-line_angle)],
                             [math.sin(-line_angle),  math.cos(-line_angle)]])
        matrix_2_inv = np.array([[math.cos(line_angle), -math.sin(line_angle)],
                                 [math.sin(line_angle),  math.cos(line_angle)]])
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
        if verbose:
            print("\tPost-collision velocity (A):", vel_a)
            print("\tPost-collision velocity (B):", vel_b)
            print("\t\tPost-collision total momentum:", m_a * vel_a + m_b * vel_b)
            print("\t\tPost-collision total energy:", 0.5 * m_a * np.linalg.norm(vel_a)**2 + 0.5 * m_b * np.linalg.norm(vel_b)**2)
            print()
        self.vel = vel_a.copy()
        obstacle.vel = vel_b.copy()
        return True
    def within_collision_distance(self, obstacle):
        assert isinstance(obstacle, Body)
        distance = np.linalg.norm(self.pos - obstacle.pos)
        if distance > obstacle.radius + self.radius:
            return False
        return True
    def get_normal_angle(self, corpo):
        raise NotImplementedError
    def add_obstacle(self, body):
        assert isinstance(body, Body)
        self.obstacles.add(body)
        body.obstacles.add(self)
        self.in_contact[body.repr] = False
        body.in_contact[self.repr] = False
    def on_collision(self, projectile):
        assert isinstance(projectile, Body)
        if self.kill:
            projetil.lives -= 1
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
        assert isinstance(projectile, Body)
        relative_position = projectile.pos - self.pos
        distance = np.linalg.norm(relative_position)
        if distance > projectile.radius + self.radius:
            return None
        return math.atan2(relative_position[1], relative_position[0])

class RegularPolygon(Body):
    obj_idx = 0
    def __init__(self, center, radius, n_edges, angle=.0, name=None, lives=1, kill=False):
        RegularPolygon.obj_idx += 1
        if name is None:
            name = 'Poly_' + str(RegularPolygon.obj_idx)
        assert isinstance(center, Point)
        assert radius > .0
        assert n_edges >= 3
        self.n_edges = int(n_edges)
        central_angle = math.tau / self.n_edges
        self.angle = angle % central_angle
        center_vector = np.array([center.getX(), center.getY()])
        self.vertices = [center_vector + radius * np.array([math.cos(i * central_angle + self.angle),
                                                            math.sin(i * central_angle + self.angle)]) for i in range(self.n_edges)]
        poly = Polygon([Point(v[0], v[1]) for v in self.vertices])
        Body.__init__(self, body=poly, mass=math.inf, radius=radius, pos_x=center_vector[0], pos_y=center_vector[1], name=name, lives=lives, kill=kill)
    def update(self, dt=1.0):
        pass
    def get_normal_angle(self, projectile, verbose=False):
        assert isinstance(projectile, Body)
        position_relative_to_center = projectile.pos - self.pos
        distance_to_center = np.linalg.norm(position_relative_to_center)
        if distance_to_center > projectile.radius + self.radius:
            return None
        projectile_relative_angle = math.atan2(position_relative_to_center[1], position_relative_to_center[0]) % math.tau
        central_angle = math.tau / self.n_edges
        idx_v = math.floor(((projectile_relative_angle - self.angle) % math.tau) / central_angle)
        v1 = self.vertices[idx_v] - self.pos
        v2 = self.vertices[(idx_v + 1) % self.n_edges] - self.pos
        edge_center = (v1 + v2) / 2
        position_relative_to_edge = position_relative_to_center - edge_center
        normal_vector = edge_center / np.linalg.norm(edge_center)
        distance_to_edge = np.dot(position_relative_to_edge, normal_vector)
        if distance_to_edge > projectile.radius:
            return None
        return math.atan2(normal_vector[1], normal_vector[0])

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
    def update(self, dt=1.0):
        assert dt > .0
        delta = self.vel * dt
        self.pos += delta
        self.body.move(delta[0], delta[1])
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Body)
        if not self.within_collision_distance(projectile):
            return None
        ball_to_edge_distance = math.fabs(projectile.pos[1] - self.pos[1] + self.height / 2)
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
    def update(self, dt=1.0):
        pass
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Body)
        p1 = self.body.getP1()
        p2 = self.body.getP2()
        # parametros da equacao da reta (aresta do poligono)
        a = p1.getY() - p2.getY()
        b = p2.getX() - p1.getX()
        distancia_bola_para_aresta = math.fabs(a * (projectile.pos[0] - p1.getX()) + b * (projectile.pos[1] - p1.getY())) / math.sqrt(a**2 + b**2)
        if distancia_bola_para_aresta > projectile.radius + self.width:
            return None
        if not self.within_collision_distance(projectile):
            return None
        return self.normal_angle
    def on_collision(self, projetil):
        if self.kill:
            projetil.lives -= 1
            if projetil.lives <= 0:
                return
            projetil.reset()
            time.sleep(1)
