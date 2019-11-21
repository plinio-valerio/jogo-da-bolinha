from graphics import *
import math
import random
import numpy as np

def rotation_matrix(angle):
    return np.array([[math.cos(angle), -math.sin(angle)],
                     [math.sin(angle),  math.cos(angle)]])

class Game:
    win_width = 960
    win_height = 640
    du = 30  # distance from upper screen limit to upper wall
    dd = 50  # distance from lower screen limit to lower wall
    dl = 30  # distance from left screen limit to left wall
    dr = 30  # distance from right screen limit to right wall
    db = 60  # distance from bar to lower screen limit
    tilt = 10  # inclination of lateral walls
    wall_color = (10, 100, 10)
    wall_width = 10
    ball_radius = 10
    ball_lives = 3
    vel_ball_0 = 400.0
    bar_length = 100
    bar_height = 10
    vel_bar = 1250.0
    n_static_obstacles = 4
    n_moving_obstacles = 4
    obst_lives = 3
    def __init__(self):
        self.static_obstacles = set()
        self.moving_obstacles = set()
        self.window = GraphWin("Blue Ball", self.win_width, self.win_height)
        self.window.setCoords(0, 0, self.win_width, self.win_height)
    def clear(self):
        self.ball.undraw()
        self.bar.undraw()
        for obst in self.moving_obstacles:
            obst.undraw()
        for obst in self.static_obstacles:
            obst.undraw()
    def reset(self):
        self.t = .0
        self.window.setBackground('white')
        self.moving_obstacles = set()
        self.static_obstacles = set()
        vel_ball_angle = math.tau/4 + (2*random.random() - 1) * math.tau/8
        vel_ball = (self.vel_ball_0 * math.cos(vel_ball_angle), self.vel_ball_0 * math.sin(vel_ball_angle))
        self.ball = PunyBall((self.win_width/2, self.win_height/2), self.ball_radius, vel=vel_ball, lives=self.ball_lives, name="PunyBalll")
        self.ball.setFill((8, 8, 192))
        self.ball.setOutline((255, 255, 0))
        self.ball.setWidth(2)
        self.ball.reset()
        self.ball.draw(self.window)
        self.bar = Bar((self.win_width/2 - self.bar_length/2, self.dd + self.db + self.bar_height/2),
                       (self.win_width/2 + self.bar_length/2, self.dd + self.db - self.bar_height/2))
        self.bar.setFill((100, 10, 10))
        self.bar.setOutline((255, 255, 0))
        self.bar.setWidth(2)
        self.bar.reset()
        self.ball.add_obstacle(self.bar)
        self.bar.draw(self.window)
        p_dl = (self.dl - self.tilt, self.dd)
        p_ul = (self.dl + self.tilt, self.win_height - self.du)
        p_dr = (self.win_width - self.dr + self.tilt, self.dd)
        p_ur = (self.win_width - self.dr - self.tilt, self.win_height - self.du)
        wall_l = Wall(p_dl, p_ul, name="Left Wall")
        wall_l.setFill(self.wall_color)
        wall_l.setWidth(self.wall_width)
        self.static_obstacles.add(wall_l)
        wall_l.reset()
        self.ball.add_obstacle(wall_l)
        wall_l.draw(self.window)
        wall_d = Wall(p_dl, p_dr, name="Lower Wall")
        wall_d.setFill(self.wall_color)
        wall_d.setWidth(self.wall_width)
        self.static_obstacles.add(wall_d)
        wall_d.reset()
        self.ball.add_obstacle(wall_d)
        self.ball.add_reaper(wall_d)
        wall_d.draw(self.window)
        wall_u = Wall(p_ul, p_ur, name="Upper Wall")
        wall_u.setFill(self.wall_color)
        wall_u.setWidth(self.wall_width)
        self.static_obstacles.add(wall_u)
        wall_u.reset()
        self.ball.add_obstacle(wall_u)
        wall_u.draw(self.window)
        wall_r = Wall(p_dr, p_ur, name="Right Wall")
        wall_r.setFill(self.wall_color)
        wall_r.setWidth(self.wall_width)
        self.static_obstacles.add(wall_r)
        wall_r.reset()
        self.ball.add_obstacle(wall_r)
        wall_r.draw(self.window)
        for i in range(self.n_static_obstacles):
            n_edges = random.randint(3, 6)
            radius = 30 * random.random() + 30
            angle = math.tau * random.random()
            center = ((self.win_width - self.dr - self.dl - 3*radius) * random.random() + self.dl + 1.5*radius,
                      (self.win_height - self.du - self.dd - self.db - 3*radius) / 3 * random.random() + \
                       2 * (self.win_height - self.du - self.dd - self.db - 3*radius) / 3 + self.dd + self.db + 1.5 * radius)
            obst = RegularPolygon(center, radius, n_edges, angle)
            color_r = random.randrange(0, 256)
            color_g = random.randrange(0, 256)
            color_b = random.randrange(0, 256)
            obst.setFill((color_r, color_g, color_b))
            obst.setOutline(((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
            obst.setWidth(2)
            self.ball.add_obstacle(obst)
            obst.add_reaper(self.ball)
            obst.reset()
            obst.draw(self.window)
            self.static_obstacles.add(obst)
        for i in range(self.n_moving_obstacles):
            radius = 30 * random.random() + 30
            center = ((self.win_width - self.dr - self.dl - 3*radius) * random.random() + self.dl + 1.5*radius,
                      (self.win_height - self.du - self.dd - self.db - 3*radius) / 3 * random.random() + \
                       2 * (self.win_height - self.du - self.dd - self.db - 3*radius) / 3 + self.dd + self.db + 1.5 * radius)
            vel_obst_modulus = random.gauss(90, 15)
            vel_obst_angle = random.random() * math.tau
            vel_obst = (vel_obst_modulus * math.cos(vel_obst_angle), vel_obst_modulus * math.sin(vel_obst_angle))
            obst = Ball(center, radius, vel=vel_obst, lives=self.obst_lives)
            color_r = random.randrange(0, 256)
            color_g = random.randrange(0, 256)
            color_b = random.randrange(0, 256)
            obst.setFill((color_r, color_g, color_b))
            obst.setOutline(((color_r + 128) % 256, (color_g + 128) % 256, (color_b + 128) % 256))
            obst.setWidth(2)
            obst.add_reaper(self.ball)
            self.ball.add_obstacle(obst)
            for obst_2 in self.static_obstacles:
                obst.add_obstacle(obst_2)
            for obst_2 in self.moving_obstacles:
                obst.add_obstacle(obst_2)
            obst.reset()
            obst.draw(self.window)
            self.moving_obstacles.add(obst)
    def update(self, dt=1.0):
        self.ball.update(dt)
        self.bar.update(dt)
        next_moving_obstacles = self.moving_obstacles.copy()
        for body in self.moving_obstacles:
            ans = body.update(dt)
            if ans is not None:
                print(body.name, "died lol")
                next_moving_obstacles.remove(body)
                alpha, beta = ans
                body.undraw()
                alpha.draw(self.window)
                beta.draw(self.window)
                alpha.add_obstacle(beta)
                beta.add_obstacle(alpha)
                for obst in self.static_obstacles:
                    alpha.add_obstacle(obst)
                    beta.add_obstacle(obst)
                for obst in next_moving_obstacles:
                    alpha.add_obstacle(obst)
                    beta.add_obstacle(obst)
                next_moving_obstacles.add(alpha)
                next_moving_obstacles.add(beta)
        self.moving_obstacles = next_moving_obstacles
        self.t += dt

class Body:
    obj_idx = 0
    def __init__(self, body, mass, pos, vel, name=None, lives=None):
        assert mass >= .0
        assert lives is None or isinstance(lives, int) and lives > 0
        self.pos = np.array(pos, dtype=np.float64)
        assert self.pos.ndim == 1 and self.pos.size == 2
        self.vel = np.array(vel, dtype=np.float64)
        assert self.vel.ndim == 1 and self.vel.size == 2
        Body.obj_idx += 1
        self.repr = 'Body_' + str(Body.obj_idx)
        if name is None:
            self.name = self.repr
        else:
            self.name = name
        self.body = body
        self.mass = float(mass)
        self.pos_0 = self.pos.copy()
        self.vel_0 = self.vel.copy()
        self.next_vel = self.vel.copy()
        self.lives = lives
        self.fill = None
        self.outline = (0, 0, 0)
        self.width = 1
        self.n_collisions = 0
        self.reapers = set()
        self.victims = set()
        self.obstacles = set()
        self.in_contact = {}
        self.interactions = set()
    def reset(self):
        delta = self.pos_0 - self.pos
        self.body.move(delta[0], delta[1])
        np.copyto(self.pos, self.pos_0)
        np.copyto(self.vel, self.vel_0)
        np.copyto(self.next_vel, self.vel_0)
        for obst in self.obstacles:
            self.in_contact[obst] = True
    def update(self, dt=1.0):
        assert dt > .0
        np.copyto(self.vel, self.next_vel)
        delta = self.vel * dt
        self.pos += delta
        self.body.move(delta[0], delta[1])
        for obst in self.obstacles:
            if self.in_contact[obst]:
                collision_angle = obst.get_normal_angle(self)
                if collision_angle is None:
                    self.in_contact[obst] = False
            else:
                collision_angle = obst.get_normal_angle(self)
                if collision_angle is None:
                    continue
                self.in_contact[obst] = True
                self.n_collisions += 1
                self.on_collision(obst)
                if self.lives is not None and self.lives <= 0:
                    divide = True
                    coefficient_of_restitution = 0.25 * random.random() + 0.5
                    alpha, beta = self.collide(obst, collision_angle, coefficient_of_restitution, divide)
                    return alpha, beta
                else:
                    self.collide(obst, collision_angle)
                    return None
    def on_collision(self, body):
        assert isinstance(body, Body)
        if body in self.reapers and self.lives is not None:
            self.lives -= 1
            self.on_life_loss()
    def on_life_loss(self):
        pass
    # def on_death(self):
    #     for body in self.victims:
    #         body.remove_reaper(self)
    #     for body in self.reapers:
    #         self.remove_reaper(body)
    #     for body in self.interactions:
    #         body.remove_obstacle(self)
    #     self.undraw()
    def add_reaper(self, body):
        assert isinstance(body, Body)
        self.reapers.add(body)
        body.victims.add(self)
    def remove_reaper(self, body):
        assert isinstance(body, Body)
        self.reapers.discard(body)
        body.victims.discard(self)
    def add_obstacle(self, body):
        assert isinstance(body, Body)
        self.obstacles.add(body)
        self.in_contact[body] = True
        body.interactions.add(self)
    def remove_obstacle(self, body):
        assert isinstance(body, Body)
        self.obstacles.discard(body)
        self.in_contact.pop(body, None)
        body.interactions.discard(self)
    def get_normal_angle(self, corpo):
        raise NotImplementedError
    def draw(self, win):
        self.body.draw(win)
    def undraw(self):
        self.body.undraw()
    def setOutline(self, color):
        self.body.setOutline(color)
    def setFill(self, color):
        assert len(color) == 3
        self.fill = tuple(color)
        self.body.setFill(color_rgb(self.fill[0], self.fill[1], self.fill[2]))
    def setOutline(self, color):
        assert len(color) == 3
        self.outline = tuple(color)
        self.body.setOutline(color_rgb(self.outline[0], self.outline[1], self.outline[2]))
    def setWidth(self, width):
        assert width >= .0
        self.width = width
        self.body.setWidth(width)

################################################################################

class Ball(Body):  # only moving body
    obj_idx = 0
    def __init__(self, center, radius, mass=None, vel=(.0,.0), name=None, lives=None):
        assert radius > .0
        assert mass is None or mass >= .0
        center = np.array(center, dtype=np.float64)
        assert center.ndim == 1 and center.size == 2
        vel = np.array(vel, dtype=np.float64)
        assert vel.ndim == 1 and vel.size == 2
        Ball.obj_idx += 1
        if name is None:
            name = 'Ball_' + str(Ball.obj_idx)
        if mass is None:
            mass = math.pi * radius**2
        self.radius = float(radius)
        super().__init__(body=Circle(Point(center[0], center[1]), self.radius), mass=mass, pos=center, vel=vel, name=name, lives=lives)
    def collide(self, obstacle, collision_angle, coefficient_of_restitution=1.0, divide=False, verbose=False):
        assert isinstance(obstacle, Body)
        assert divide is False or coefficient_of_restitution < 1.0
        # collision_angle = obstacle.get_normal_angle(self)
        # if collision_angle is None:
        #     return False
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

        if m_a / m_b == .0:
            translation_vector = vel_b.copy()
        elif m_b / m_a == .0:
            translation_vector = vel_a.copy()
        else:
            translation_vector = (m_a * vel_a + m_b * vel_b) / (m_a + m_b)
        vel_a -= translation_vector
        vel_b -= translation_vector
        matrix_1     = rotation_matrix(-collision_angle)
        matrix_1_inv = rotation_matrix( collision_angle)
        vel_a = np.dot(matrix_1, vel_a)
        vel_b = np.dot(matrix_1, vel_b)
        energy = 0.5 * m_a * np.linalg.norm(vel_a)**2 + 0.5 * m_b * np.linalg.norm(vel_b)**2

        vel_a[0] *= -1.0
        vel_b[0] *= -1.0
        vel_a *= coefficient_of_restitution
        vel_b *= coefficient_of_restitution
        if divide:
            # Rotates plane so that object A's velocity has angle 0
            vel_a_angle = math.atan2(vel_a[1], vel_a[0])
            matrix_2     = rotation_matrix(-vel_a_angle)
            matrix_2_inv = rotation_matrix( vel_a_angle)
            vel_alpha = np.dot(vel_a, matrix_2)
            vel_beta = vel_alpha.copy()
            m_alpha = m_a / 2
            m_beta = m_a - m_alpha
            energy_loss = energy * (1 - coefficient_of_restitution**2)
            vel_alpha[1] += math.sqrt(energy_loss / m_alpha)
            vel_beta[1]  -= math.sqrt(energy_loss / m_beta)
            vel_alpha = np.dot(matrix_2_inv, vel_alpha)
            vel_beta  = np.dot(matrix_2_inv, vel_beta)
            vel_alpha = np.dot(matrix_1_inv, vel_alpha)
            vel_beta  = np.dot(matrix_1_inv, vel_beta)
            vel_b     = np.dot(matrix_1_inv, vel_b)
            vel_alpha += translation_vector
            vel_beta  += translation_vector
            vel_b     += translation_vector
            if verbose:
                print("\tm_a' = %.2f" % m_alpha)
                print('\tm_a" = %.2f' % m_beta)
                print("\tm_b = %.2f" % m_b)
                print("\tPost-collision velocity (A'):", vel_alpha)
                print('\tPost-collision velocity (A"):', vel_beta)
                print("\tPost-collision velocity (B):", vel_b)
                print("\t\tPost-collision total momentum:", m_alpha * vel_alpha + m_beta * vel_beta + m_b * vel_b)
                print("\t\tPost-collision total energy:", 0.5*m_alpha*np.linalg.norm(vel_alpha)**2 + 0.5*m_beta*np.linalg.norm(vel_beta)**2 + 0.5*m_b*np.linalg.norm(vel_b)**2)
                print()
            alpha = Ball(self.pos, self.radius/math.sqrt(2), vel=vel_alpha)
            alpha.setFill(self.fill)
            alpha.setOutline(self.outline)
            alpha.setWidth(self.width)
            beta = Ball(self.pos, self.radius/math.sqrt(2), vel=vel_beta)
            beta.setFill(self.fill)
            beta.setOutline(self.outline)
            beta.setWidth(self.width)
            np.copyto(obstacle.next_vel, vel_b)
            return alpha, beta
        else:
            vel_a = np.dot(matrix_1_inv, vel_a)
            vel_b = np.dot(matrix_1_inv, vel_b)
            vel_a += translation_vector
            vel_b += translation_vector
            if verbose:
                print("\tPost-collision velocity (A):", vel_a)
                print("\tPost-collision velocity (B):", vel_b)
                print("\t\tPost-collision total momentum:", m_a * vel_a + m_b * vel_b)
                print("\t\tPost-collision total energy:", 0.5 * m_a * np.linalg.norm(vel_a)**2 + 0.5 * m_b * np.linalg.norm(vel_b)**2)
                print()
            np.copyto(self.next_vel, vel_a)
            np.copyto(obstacle.next_vel, vel_b)
            return self
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Body)
        relative_position = projectile.pos - self.pos
        distance = np.linalg.norm(relative_position)
        if distance > projectile.radius + self.radius:
            return None
        return math.atan2(relative_position[1], relative_position[0])

class PunyBall(Ball):
    def on_life_loss(self):
        if self.lives > 0:
            self.reset()
            time.sleep(1)

################################################################################

class StaticBody(Body):
    obj_idx = 0
    def __init__(self, body, pos, name=None, lives=None):
        pos = np.array(pos, dtype=np.float64)
        assert pos.ndim == 1 and pos.size == 2
        StaticBody.obj_idx += 1
        if name is None:
            name = "PunyBall_" + str(StaticBody.obj_idx)
        super().__init__(body=body, mass=math.inf, pos=pos, vel=(.0,.0), name=name, lives=lives)
    def update(self, dt=1.0):
        pass

class RegularPolygon(StaticBody):
    obj_idx = 0
    def __init__(self, center, radius, n_edges, angle=.0, name=None, lives=None):
        assert radius > .0
        assert n_edges >= 3
        center = np.array(center, dtype=np.float64)
        assert center.ndim == 1 and center.size == 2
        RegularPolygon.obj_idx += 1
        if name is None:
            name = 'Poly_' + str(RegularPolygon.obj_idx)
        self.radius = float(radius)
        self.n_edges = int(n_edges)
        central_angle = math.tau / self.n_edges
        self.angle = angle % central_angle
        self.vertices = [center + self.radius * np.array([math.cos(i * central_angle + self.angle),
                                                          math.sin(i * central_angle + self.angle)]) for i in range(self.n_edges)]
        poly = Polygon([Point(v[0], v[1]) for v in self.vertices])
        super().__init__(body=poly, pos=center, name=name, lives=lives)
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Ball)
        position_relative_to_poly = projectile.pos - self.pos
        distance_to_center = np.linalg.norm(position_relative_to_poly)
        if distance_to_center > projectile.radius + self.radius:
            return None
        projectile_relative_angle = math.atan2(position_relative_to_poly[1], position_relative_to_poly[0])
        central_angle = math.tau / self.n_edges
        idx_v = math.floor(((projectile_relative_angle - self.angle) % math.tau) / central_angle)
        v1 = self.vertices[idx_v]
        v2 = self.vertices[(idx_v + 1) % self.n_edges]
        edge_length = np.linalg.norm(v2 - v1)
        edge_center = (v1 + v2) / 2
        position_relative_to_edge = projectile.pos - edge_center
        edge_normal_vector = edge_center - self.pos
        edge_normal_vector /= np.linalg.norm(edge_normal_vector)
        edge_normal_angle = math.atan2(edge_normal_vector[1], edge_normal_vector[0])
        rotated_position = np.dot(rotation_matrix(-edge_normal_angle), position_relative_to_edge)
        orthogonal_distance_to_edge = rotated_position[0]
        parallel_distance_to_edge_center = math.fabs(rotated_position[1])
        if orthogonal_distance_to_edge > projectile.radius:
            return None
        if parallel_distance_to_edge_center > edge_length / 2:
            if rotated_position[1] < 0:
                closest_vertex = v1
            else:
                closest_vertex = v2
            position_relative_to_vertex = projectile.pos - closest_vertex
            return math.atan2(position_relative_to_vertex[1], position_relative_to_vertex[0])
        return edge_normal_angle

class Wall(StaticBody):
    obj_idx = 0
    def __init__(self, p1, p2, name=None, lives=None):
        self.p1 = np.array(p1, dtype=np.float64)
        assert self.p1.ndim == 1 and self.p1.size == 2
        self.p2 = np.array(p2, dtype=np.float64)
        assert self.p2.ndim == 1 and self.p2.size == 2
        Wall.obj_idx += 1
        if name is None:
            name = 'Wall_' + str(Wall.obj_idx)
        center = (self.p1 + self.p2) / 2
        normal_vector = np.dot(rotation_matrix(math.tau/4), self.p2 - center)
        self.normal_angle = math.atan2(normal_vector[1], normal_vector[0])
        self.length = np.linalg.norm(self.p2 - self.p1)
        super().__init__(body=Line(Point(self.p1[0], self.p1[1]), Point(self.p2[0], self.p2[1])), pos=center, name=name, lives=lives)
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Ball)
        relative_position = np.dot(rotation_matrix(-self.normal_angle), projectile.pos - self.pos)
        orthogonal_distance_to_edge = math.fabs(relative_position[0])
        parallel_distance_to_center = math.fabs(relative_position[1])
        if orthogonal_distance_to_edge > projectile.radius + self.width / 2:
            return None
        if parallel_distance_to_center > self.length / 2:
            return None
        return self.normal_angle

################################################################################

class Bar(Body):
    obj_idx = 0
    def __init__(self, p1, p2, name=None):
        self.p1 = np.array(p1, dtype=np.float64)
        assert self.p1.ndim == 1 and self.p1.size == 2
        self.p2 = np.array(p2, dtype=np.float64)
        assert self.p2.ndim == 1 and self.p2.size == 2
        Bar.obj_idx += 1
        if name is None:
            name = 'Bar_' + str(Bar.obj_idx)
        center = (self.p1 + self.p2) / 2
        bar_shape = self.p2 - self.p1
        self.length = math.fabs(bar_shape[0])
        self.height = math.fabs(bar_shape[1])
        self.vel = np.array([.0, .0], dtype=np.float64)
        super().__init__(body=Rectangle(Point(self.p1[0], self.p1[1]), Point(self.p2[0], self.p2[1])), mass=math.inf, pos=center, vel=(.0,.0), name=name)
    def reset(self):
        delta = self.pos_0 - self.pos
        self.body.move(delta[0], delta[1])
        np.copyto(self.pos, self.pos_0)
    def update(self, dt=1.0):
        assert dt > .0
        delta = self.vel * dt
        self.pos += delta
        self.body.move(delta[0], delta[1])
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Ball)
        relative_position = projectile.pos - self.pos
        parallel_distance_to_center = math.fabs(relative_position[0])
        orthogonal_distance_to_edge = math.fabs(relative_position[1]) - self.height/2
        if parallel_distance_to_center > self.length / 2:
            return None
        if orthogonal_distance_to_edge > projectile.radius:
            return None
        return math.tau / 4
