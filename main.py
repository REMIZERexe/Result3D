import pygame
import math
import sys
pygame.init()

screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

def update_screen_dimensions():
    global width
    global height
    global centerX
    global centerY
    global center
    width, height = screen.get_width(), screen.get_height()
    centerX, centerY = width // 2, height // 2
    center = [centerX, centerY]

update_screen_dimensions()

fullscreen = True
pygame.display.set_caption("Result [pre-alpha]")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHTBLUE = (135, 206, 235)

screen.fill(WHITE)

camera_position = [0, 0, -500]
yaw = 0  # Поворот по горизонтали
pitch = 0  # Поворот по вертикали
fov = 400

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Текстуры
# texture = pygame.image.load('texture.jpg')

def rotate_around_camera(x, y, z):
    global yaw, pitch

    # Преобразование углов в радианы
    cos_yaw = math.cos(math.radians(yaw))
    sin_yaw = math.sin(math.radians(yaw))
    cos_pitch = math.cos(math.radians(pitch))
    sin_pitch = math.sin(math.radians(pitch))

    # Вращение вокруг оси Y (yaw)
    xz_rotatedX = x * cos_yaw - z * sin_yaw
    xz_rotatedZ = x * sin_yaw + z * cos_yaw

    # Вращение вокруг оси X (pitch)
    yz_rotatedY = y * cos_pitch - xz_rotatedZ * sin_pitch
    yz_rotatedZ = y * sin_pitch + xz_rotatedZ * cos_pitch

    return xz_rotatedX, yz_rotatedY, yz_rotatedZ

def project_point(x, y, z):
    # Смещение точки относительно позиции камеры
    x -= camera_position[0]
    y -= camera_position[1]
    z -= camera_position[2]

    x, y, z = rotate_around_camera(x, y, z)

    if z > 0:
        x_screen = int(x * (fov / z) + centerX)
        y_screen = int(y * (fov / z) + centerY)
        return (x_screen, y_screen)
    return None

def draw_line(start, end):
    if start and end:
        pygame.draw.line(screen, BLACK, start, end, 1)

def rotate_y(x, y, z, angle):
    cos_theta = math.cos(math.radians(angle))
    sin_theta = math.sin(math.radians(angle))

    x_rotated = x * cos_theta - z * sin_theta
    z_rotated = x * sin_theta + z * cos_theta

    return x_rotated, y, z_rotated

cube_rotation_angle = 0
def create_cube():
    global cube_rotation_angle

    cube_points = [
        (-100, -100, -100), (100, -100, -100), (100, 100, -100), (-100, 100, -100),
        (-100, -100, 100), (100, -100, 100), (100, 100, 100), (-100, 100, 100)
    ]

    cube_rotation_angle += 1
    if cube_rotation_angle >= 360:
        cube_rotation_angle -= 360

    cube_points_onScreen = [
        project_point(*rotate_y(*cube_points[0], cube_rotation_angle)), project_point(*rotate_y(*cube_points[1], cube_rotation_angle)), project_point(*rotate_y(*cube_points[2], cube_rotation_angle)),
        project_point(*rotate_y(*cube_points[3], cube_rotation_angle)), project_point(*rotate_y(*cube_points[4], cube_rotation_angle)), project_point(*rotate_y(*cube_points[5], cube_rotation_angle)),
        project_point(*rotate_y(*cube_points[6], cube_rotation_angle)), project_point(*rotate_y(*cube_points[7], cube_rotation_angle))
    ]

    rotated_points = [rotate_y(x, y, z, cube_rotation_angle) for x, y, z in cube_points]

    projected_points = [project_point(x, y, z) for x, y, z in rotated_points]

    # Ребра куба
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Задняя грань
        (4, 5), (5, 6), (6, 7), (7, 4),  # Передняя грань
        (0, 4), (1, 5), (2, 6), (3, 7)   # Соединяющие линии
    ]

    for edge in edges:
        start_point = projected_points[edge[0]]
        end_point = projected_points[edge[1]]
        
        if start_point and end_point:
            if is_panel_open:
                if start_point[0] > panel_width and end_point[0] > panel_width:
                    draw_line(start_point, end_point)
            else:
                for edge in edges:
                    draw_line(projected_points[edge[0]], projected_points[edge[1]])
    
    pygame.draw.polygon(screen, GRAY, [
    cube_points_onScreen[0],
    cube_points_onScreen[1],
    cube_points_onScreen[5],
    cube_points_onScreen[4]
])
    pygame.draw.polygon(screen, GRAY, [
    cube_points_onScreen[2],
    cube_points_onScreen[3],
    cube_points_onScreen[7],
    cube_points_onScreen[6]
])
    pygame.draw.polygon(screen, GRAY, [
    cube_points_onScreen[0],
    cube_points_onScreen[1],
    cube_points_onScreen[2],
    cube_points_onScreen[3]
])

def handle_camera_movement():
    keys = pygame.key.get_pressed()
    move_speed = 2
    movement = [0, 0, 0]

    if keys[pygame.K_z]:  # Вперед
        camera_position[2] += move_speed * math.cos(math.radians(yaw))
        camera_position[0] += move_speed * math.sin(math.radians(yaw))
        movement[2] += move_speed * math.cos(math.radians(yaw))
        movement[0] += move_speed * math.sin(math.radians(yaw))
    if keys[pygame.K_s]:  # Назад
        camera_position[2] -= move_speed * math.cos(math.radians(yaw))
        camera_position[0] -= move_speed * math.sin(math.radians(yaw))
        movement[2] -= move_speed * math.cos(math.radians(yaw))
        movement[0] -= move_speed * math.sin(math.radians(yaw))
    if keys[pygame.K_q]:  # Влево
        camera_position[0] -= move_speed * math.cos(math.radians(yaw))
        camera_position[2] += move_speed * math.sin(math.radians(yaw))
        movement[0] -= move_speed * math.cos(math.radians(yaw))
        movement[2] += move_speed * math.sin(math.radians(yaw))
    if keys[pygame.K_d]:  # Вправо
        camera_position[0] += move_speed * math.cos(math.radians(yaw))
        camera_position[2] -= move_speed * math.sin(math.radians(yaw))
        movement[0] += move_speed * math.cos(math.radians(yaw))
        movement[2] -= move_speed * math.sin(math.radians(yaw))
    if keys[pygame.K_SPACE]:  # Вверх
        camera_position[1] -= move_speed
        movement[1] -= move_speed
    if keys[pygame.K_LSHIFT]:  # Вниз
        camera_position[1] += move_speed
        movement[1] += move_speed

    length = math.sqrt(movement[0]**2 + movement[1]**2 + movement[2]**2)
    if length > 0:
        movement[0] /= length
        movement[1] /= length
        movement[2] /= length

    camera_position[0] += movement[0] * move_speed
    camera_position[1] += movement[1] * move_speed
    camera_position[2] += movement[2] * move_speed

def handle_camera_rotation():
    global yaw, pitch
    mouse_dx, mouse_dy = pygame.mouse.get_rel()

    sensitivity = 0.15
    yaw += mouse_dx * sensitivity
    pitch += mouse_dy * sensitivity

    pitch = max(-89, min(89, pitch))

is_panel_open = False
panel_width = 700

def draw_panel():
    LIGHTGRAY = (240, 240, 240)
    pygame.draw.rect(screen, LIGHTGRAY, (0, 0, panel_width, height))
    font = pygame.font.SysFont(None, 36)

    border_thickness = 1
    pygame.draw.rect(screen, BLACK, (0, 0, panel_width, height), border_thickness)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                is_panel_open = not is_panel_open

            if event.key == pygame.K_F11:
                if fullscreen:
                    screen = pygame.display.set_mode((1280, 720))
                    fullscreen = False
                else:
                    screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
                    fullscreen = True
                update_screen_dimensions()

    handle_camera_movement()
    handle_camera_rotation()

    screen.fill(LIGHTBLUE)

    if is_panel_open:
        draw_panel()

    pygame.draw.circle(screen, BLACK, center, 2)

    create_cube()

    pygame.display.flip()

    # Ограничитель FPS
    clock = pygame.time.Clock()
    clock.tick(120)
