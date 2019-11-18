from graphics import *
import math
import numpy as np

def rotation_matrix(angle):
    return np.array([[math.cos(angle), -math.sin(angle)],
                     [math.sin(angle),  math.cos(angle)]])

class Body:
    obj_idx = 0
    def __init__(self, body, mass, pos_x, pos_y, name=None, lives=None):
        assert mass >= .0
        assert lives is None or isinstance(lives, int) and lives > 0
        Body.obj_idx += 1
        self.repr = 'Body_' + str(Body.obj_idx)
        if name is None:
            self.name = self.repr
        else:
            self.name = name
        self.body = body
        self.pos = np.array([pos_x, pos_y], dtype=np.float64)
        self.pos_0 = self.pos.copy()
        self.lives = lives
        self.mass = mass
        self.width = 1.0
        self.n_collisions = 0
        self.reapers = set()
        self.victims = set()
        self.interactions = set()
    def update(self, dt=1.0):
        pass
    def add_reaper(self, body):
        assert isinstance(body, Body)
        self.reapers.add(body)
        body.victims.add(self)
    def remove_reaper(self, body):
        assert isinstance(body, Body)
        self.reapers.discard(body)
        body.victims.discard(self)
    def get_normal_angle(self, corpo):
        raise NotImplementedError
    def on_collision(self, body):
        assert isinstance(body, Body)
        self.n_collisions += 1
        if body in self.reapers and self.lives is not None:
            self.lives -= 1
            if self.lives <= 0:
                self.on_death
    def on_death(self):
        for body in self.victims:
            body.remove_reaper(self)
        for body in self.reapers:
            self.remove_reaper(body)
        for body in self.interactions:
            body.remove_obstacle(self)
        self.undraw()
        self.update = lambda a,b: None
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

class Ball(Body):  # only moving body
    obj_idx = 0
    def __init__(self, center, radius, vel_x=.0, vel_y=.0, name=None, mass=None, lives=None):
        assert isinstance(center, Point)
        assert radius > .0
        assert mass is None or mass >= .0
        Ball.obj_idx += 1
        if name is None:
            name = 'Ball_' + str(Ball.obj_idx)
        if mass is None:
            mass = math.pi * radius**2
        self.radius = float(radius)
        self.vel = np.array([vel_x, vel_y], dtype=np.float64)
        self.vel_0 = self.vel.copy()
        self.obstacles = set()
        self.in_contact = {}
        Body.__init__(self, body=Circle(center, radius), mass=mass, pos_x=center.getX(), pos_y=center.getY(), name=name, lives=lives)
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
        matrix_0     = rotation_matrix(-collision_angle)
        matrix_0_inv = rotation_matrix( collision_angle)
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

        matrix_1 = np.array([[math.sqrt(m_a), .0],
                             [.0, math.sqrt(m_b)]])
        matrix_1_inv = np.array([[1.0/math.sqrt(m_a), .0],
                                 [.0, 1.0/math.sqrt(m_b)]])
        solution = np.dot(matrix_1, solution)

        # STEP 2: rotate coordinate system so that conservation of momentum yields a line parallel to the x axis
        # Conservation of momentum:  ²m_a * x  + ²m_b * y  = m_a * vel_a_x
        # Conservation of energy:    x² + y² = m_a * vel_a_x²
        line_angle = math.atan(-math.sqrt(m_a/m_b))
        matrix_2     = rotation_matrix(-line_angle)
        matrix_2_inv = rotation_matrix( line_angle)
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

class RegularPolygon(Body):
    obj_idx = 0
    def __init__(self, center, radius, n_edges, angle=.0, name=None, lives=None):
        assert isinstance(center, Point)
        assert radius > .0
        assert n_edges >= 3
        RegularPolygon.obj_idx += 1
        if name is None:
            name = 'Poly_' + str(RegularPolygon.obj_idx)
        self.vel = np.array([.0, .0], dtype=np.float64)
        self.radius = float(radius)
        self.n_edges = int(n_edges)
        central_angle = math.tau / self.n_edges
        self.angle = angle % central_angle
        center_vector = np.array([center.getX(), center.getY()])
        self.vertices = [center_vector + radius * np.array([math.cos(i * central_angle + self.angle),
                                                            math.sin(i * central_angle + self.angle)]) for i in range(self.n_edges)]
        poly = Polygon([Point(v[0], v[1]) for v in self.vertices])
        Body.__init__(self, body=poly, mass=math.inf, pos_x=center_vector[0], pos_y=center_vector[1], name=name, lives=lives)
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Ball)
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
    def __init__(self, p1, p2, name=None):
        assert isinstance(p1, Point)
        assert isinstance(p2, Point)
        Bar.obj_idx += 1
        if name is None:
            name = 'Bar_' + str(Bar.obj_idx)
        pos_x = (p1.getX() + p2.getX()) / 2
        pos_y = (p1.getY() + p2.getY()) / 2
        self.height = math.fabs(p2.getY() - p1.getY())
        self.length = math.fabs(p2.getX() - p1.getX())
        self.vel = np.array([.0, .0], dtype=np.float64)
        Body.__init__(self, body=Rectangle(p1, p2), mass=math.inf, pos_x=pos_x, pos_y=pos_y, name=name)
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

class Wall(Body):
    obj_idx = 0
    def __init__(self, p1, p2, name=None, lives=None):
        assert isinstance(p1, Point)
        assert isinstance(p2, Point)
        Wall.obj_idx += 1
        if name is None:
            name = 'Wall_' + str(Wall.obj_idx)
        self.vel = np.array([.0, .0], dtype=np.float64)
        self.p1 = np.array([p1.getX(), p1.getY()])
        self.p2 = np.array([p2.getX(), p2.getY()])
        center = (self.p1 + self.p2) / 2
        normal_vector = np.dot(rotation_matrix(math.tau/4), self.p2 - center)
        self.normal_angle = math.atan2(normal_vector[1], normal_vector[0])
        self.radius = np.linalg.norm(self.p2 - self.p1) / 2
        Body.__init__(self, body=Line(p1, p2), mass=math.inf, pos_x=center[0], pos_y=center[1], name=name, lives=lives)
    def get_normal_angle(self, projectile):
        assert isinstance(projectile, Ball)
        relative_position = np.dot(rotation_matrix(-self.normal_angle), projectile.pos - self.pos)
        orthogonal_distance_to_edge = math.fabs(relative_position[0])
        parallel_distance_to_center = math.fabs(relative_position[1])
        if orthogonal_distance_to_edge > projectile.radius + self.width / 2:
            return None
        if parallel_distance_to_center > self.radius:
            return None
        return self.normal_angle
