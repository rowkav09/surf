from panda3d.core import Vec3

GRAVITY          = 800.0
MAX_VELOCITY     = 3500.0
SV_AIRACCELERATE = 150.0
AIR_SPEED_CAP    = 30.0
SV_FRICTION      = 4.0
SV_ACCELERATE    = 10.0
PLAYER_SPEED     = 250.0
STOP_SPEED       = 100.0
STEP_HEIGHT      = 18.0
PLAYER_HEIGHT    = 72.0
PLAYER_RADIUS    = 16.0


def clip_velocity(velocity, normal, overbounce=1.0):
    backoff = velocity.dot(normal) * overbounce
    result = Vec3(velocity)
    result -= normal * backoff
    for i in range(3):
        if abs(result[i]) < 1/32:
            result[i] = 0.0
    return result


def air_accelerate(velocity, wishdir, wishspeed, dt):
    if wishdir.length() < 0.001:
        return Vec3(velocity)
    capped = min(wishspeed, AIR_SPEED_CAP)
    current_speed = velocity.dot(wishdir)
    add_speed = capped - current_speed
    if add_speed <= 0:
        return Vec3(velocity)
    accel_speed = min(SV_AIRACCELERATE * wishspeed * dt, add_speed)
    result = Vec3(velocity)
    result += wishdir * accel_speed
    return result


def ground_accelerate(velocity, wishdir, wishspeed, dt):
    if wishdir.length() < 0.001:
        return Vec3(velocity)
    current_speed = velocity.dot(wishdir)
    add_speed = wishspeed - current_speed
    if add_speed <= 0:
        return Vec3(velocity)
    accel_speed = min(SV_ACCELERATE * wishspeed * dt, add_speed)
    result = Vec3(velocity)
    result += wishdir * accel_speed
    return result


def apply_friction(velocity, dt):
    speed = velocity.length()
    if speed < 0.1:
        return Vec3(0, 0, 0)
    control = max(speed, STOP_SPEED)
    drop = control * SV_FRICTION * dt
    new_speed = max(speed - drop, 0.0)
    result = Vec3(velocity)
    result *= new_speed / speed
    return result


def apply_gravity(velocity, dt):
    result = Vec3(velocity)
    result.z -= GRAVITY * dt
    return result


def classify_normal(normal):
    if normal.z > 0.7:
        return 'ground'
    elif normal.z > 0.1:
        return 'ramp'
    else:
        return 'wall'


def build_wish_vector(forward_vec, right_vec, move_forward, move_right):
    wish = Vec3(forward_vec) * move_forward + Vec3(right_vec) * move_right
    wish.z = 0
    wishspeed = wish.length()
    if wishspeed > 0.001:
        wishdir = wish / wishspeed
    else:
        wishdir = Vec3(0, 0, 0)
        wishspeed = 0.0
    return wishdir, min(wishspeed, PLAYER_SPEED)


class SurfPhysics:
    def __init__(self):
        self.velocity      = Vec3(0, 0, 0)
        self.position      = Vec3(0, 0, 500)
        self.on_ground     = False
        self.on_ramp       = False
        self.ramp_normal   = Vec3(0, 0, 1)
        self.contact_normals = []

    def tick(self, wishdir, wishspeed, dt):
        dt = min(dt, 0.05)

        self.velocity = apply_gravity(self.velocity, dt)

        self.on_ground = False
        self.on_ramp   = False
        best_normal    = None

        for normal in self.contact_normals:
            kind = classify_normal(normal)
            if kind == 'ground':
                self.on_ground = True
                best_normal = normal
            elif kind == 'ramp':
                self.on_ramp = True
                self.ramp_normal = Vec3(normal)
                best_normal = normal
            elif kind == 'wall':
                self.velocity = clip_velocity(self.velocity, normal, 1.001)

        if self.on_ramp:
            self.velocity = clip_velocity(self.velocity, self.ramp_normal)
            self.velocity = air_accelerate(self.velocity, wishdir, wishspeed, dt)
        elif self.on_ground:
            if best_normal is not None:
                self.velocity = clip_velocity(self.velocity, best_normal)
            self.velocity = apply_friction(self.velocity, dt)
            self.velocity = ground_accelerate(self.velocity, wishdir, wishspeed, dt)
        else:
            self.velocity = air_accelerate(self.velocity, wishdir, wishspeed, dt)

        speed = self.velocity.length()
        if speed > MAX_VELOCITY:
            self.velocity *= MAX_VELOCITY / speed

        self.position += self.velocity * dt
        self.contact_normals = []

    def add_contact(self, normal):
        self.contact_normals.append(Vec3(normal))

    def push_out(self, displacement):
        self.position += displacement
