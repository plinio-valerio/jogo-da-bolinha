from graphics import *
import math
import numpy as np

def rotation_matrix(angle):
    return np.array([[math.cos(angle), -math.sin(angle)],
                     [math.sin(angle),  math.cos(angle)]])

class Universe:
    def __init__(self, window):
        assert isinstance(window, GraphWin)
        self.window = window
        self.static_bodies = set()
        self.moving_bodies = set(
    def update(self, dt=1.0):
        for body in self.moving_bodies:
            body.update(dt=dt)
        raise NotImplementedError

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
        self.lives = lives
        self.width = 1
        self.n_collisions = 0
        self.reapers = set()
        self.victims = set()
        self.interactions = set()
    def reset(self):
        delta = self.pos_0 - self.pos
        self.body.move(delta[0], delta[1])
        np.copyto(self.pos, self.pos_0)
        np.copyto(self.vel, self.vel_0)
    def add_reaper(self, body):
        assert isinstance(body, Body)
        self.reapers.add(body)
        body.victims.add(self)
    def remove_reaper(self, body):
        assert isinstance(body, Body)
        self.reapers.discard(body)
        body.victims.discard(self)
    def update(self, dt=1.0):
        raise NotImplementedError
    def get_normal_angle(self, corpo):
        raise NotImplementedError
    def on_collision(self, body):
        assert isinstance(body, Body)
        self.n_collisions += 1
        if body in self.reapers and self.lives is not None:
            self.lives -= 1
            if self.lives <= 0:
                self.on_death
    def on_life_loss(self):
        pass
    def on_death(self):
        for body in self.victims:
            body.remove_reaper(self)
        for body in self.reapers:
            self.remove_reaper(body)
        for body in self.interactions:
            body.remove_obstacle(self)
        self.undraw()
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
        self.obstacles = set()
        self.in_contact = {}
        super().__init__(body=Circle(Point(center[0], center[1]), self.radius), mass=mass, pos=center, vel=vel, name=name, lives=lives)
    def update(self, dt=1.0):
        assert dt > .0
        delta = self.vel * dt
        self.pos += delta
        self.body.move(delta[0], delta[1])
        for obst in self.obstacles:
            if self.in_contact[obst]:
                collision_angle = obst.get_normal_angle(self)
                if collision_angle is None:
                    self.in_contact[obst] = False
                    if isinstance(obst, Ball):
                        obst.in_contact[self] = False
            else:
                touched = self.collide(obst)
                if touched:
                    self.in_contact[obst] = True
                    if isinstance(obst, Ball):
                        obst.in_contact[self] = True
                    self.on_collision(obst)
                    obst.on_collision(self)
    def collide(self, obstacle, coefficient_of_restitution=1.0, verbose=False):
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

        if m_a / m_b == .0:
            translation_vector = vel_b.copy()
        elif m_b / m_a == .0:
            translation_vector = vel_a.copy()
        else:
            translation_vector = (m_a * vel_a + m_b * vel_b) / (m_a + m_b)
        vel_a -= translation_vector
        vel_b -= translation_vector
        rot_matrix     = rotation_matrix(-collision_angle)
        rot_matrix_inv = rotation_matrix( collision_angle)
        vel_a = np.dot(rot_matrix, vel_a)
        vel_b = np.dot(rot_matrix, vel_b)

        vel_a[0] *= -1.0
        vel_b[0] *= -1.0
        vel_a *= coefficient_of_restitution
        vel_b *= coefficient_of_restitution

        vel_a = np.dot(rot_matrix_inv, vel_a)
        vel_b = np.dot(rot_matrix_inv, vel_b)
        vel_a += translation_vector
        vel_b += translation_vector
        if verbose:
            print("\tPost-collision velocity (A):", vel_a)
            print("\tPost-collision velocity (B):", vel_b)
            print("\t\tPost-collision total momentum:", m_a * vel_a + m_b * vel_b)
            print("\t\tPost-collision total energy:", 0.5 * m_a * np.linalg.norm(vel_a)**2 + 0.5 * m_b * np.linalg.norm(vel_b)**2)
            print()
        np.copyto(self.vel, vel_a)
        np.copyto(obstacle.vel, vel_b)
        return True
    def add_obstacle(self, body):
        assert isinstance(body, Body)
        self.obstacles.add(body)
        self.in_contact[body] = False
        body.interactions.add(self)
    def remove_obstacle(self, body):
        assert isinstance(body, Body)
        self.obstacles.discard(body)
        self.in_contact.pop(body, None)
        body.interactions.discard(self)
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Body)
        relative_position = projectile.pos - self.pos
        distance = np.linalg.norm(relative_position)
        if distance > projectile.radius + self.radius:
            return None
        return math.atan2(relative_position[1], relative_position[0])

class PunyBall(Ball):
    def on_life_loss(self):
        self.reset()

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
