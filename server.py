# ===============================
# NEXER: Despertar 2072
# Proyecto escolar - FPS 3D en Python (Ursina)
# ===============================

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random, json, os, sys

# --------- RUTAS COMPATIBLES CON .EXE ---------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --------- VOZ (OPCIONAL) ---------
try:
    import pyttsx3
    tts = pyttsx3.init()
    def amy_speak(text):
        try:
            tts.say(text)
            tts.runAndWait()
        except:
            pass
except:
    def amy_speak(text): pass

# --------- APP ---------
app = Ursina()
window.title = "NEXER"
window.color = color.black
scene.fog_density = 0.02
scene.fog_color = color.rgb(10,10,30)

SAVE_FILE = 'save.json'

def save_game(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return None

# --------- ESTADOS ---------
state = 'menu'  # menu, options, game, pause, intro

# --------- MENÚ PRINCIPAL ---------
menu = Entity(parent=camera.ui)
menu_bg = Entity(parent=camera.ui, model='quad', color=color.rgb(10,10,30), scale=2, z=1)

title = Text("NEXER\nDespertar 2072", parent=menu, origin=(0,0), scale=2, y=0.25)

def start_new():
    global state
    state = 'intro'
    menu.enabled = False
    options.enabled = False
    pause_ui.enabled = False
    menu_bg.enabled = False
    intro()

def continue_game():
    data = load_game()
    start_new()
    if data:
        player.position = Vec3(*data.get('pos', [0,2,0]))

def open_options():
    global state
    state = 'options'
    menu.enabled = False
    options.enabled = True

def exit_game():
    application.quit()

Button("CONTINUAR", parent=menu, y=0.08, scale=(0.35,0.08), on_click=continue_game)
Button("NUEVA PARTIDA", parent=menu, y=-0.02, scale=(0.35,0.08), on_click=start_new)
Button("OPCIONES", parent=menu, y=-0.12, scale=(0.35,0.08), on_click=open_options)
Button("SALIR", parent=menu, y=-0.22, scale=(0.35,0.08), on_click=exit_game)

# --------- OPCIONES ---------
options = Entity(parent=camera.ui, enabled=False)
Text("OPCIONES", parent=options, y=0.25, scale=2)

volume = 0.5
def set_volume(v):
    global volume
    volume = v

Slider(min=0, max=1, default=0.5, parent=options, y=0.05, on_value_changed=set_volume)

def back_menu():
    global state
    state = 'menu'
    options.enabled = False
    menu.enabled = True

Button("VOLVER", parent=options, y=-0.2, scale=(0.3,0.08), on_click=back_menu)

# --------- PAUSA ---------
pause_ui = Entity(parent=camera.ui, enabled=False)
Text("PAUSA", parent=pause_ui, y=0.2, scale=2)

def resume():
    global state
    state = 'game'
    pause_ui.enabled = False
    mouse.locked = True

def save_and_exit():
    if player:
        save_game({'pos':[player.x, player.y, player.z]})
    application.quit()

Button("CONTINUAR", parent=pause_ui, y=0.0, on_click=resume)
Button("GUARDAR Y SALIR", parent=pause_ui, y=-0.1, on_click=save_and_exit)

# --------- INTRO CINEMÁTICA ---------
def intro():
    camera.parent = None
    camera.position = (0,15,-35)
    camera.look_at(Vec3(0,0,0))
    Text("Año 2072...", scale=2, y=0.3)
    invoke(start_level, delay=3)

# --------- VARIABLES JUEGO ---------
player = None
enemies = []
boss = None

health, shield, shield_timer = 100, 100, 0
ammo = 30
boss_health = 200

# HUD refs
shield_bar = None
health_bar = None
ammo_text = None
crosshair = None
amy_text = None
damage_overlay = None

# --------- NIVEL ---------
def start_level():
    global state, player, shield_bar, health_bar, ammo_text, crosshair, amy_text, damage_overlay

    state = 'game'

    Entity(model='plane', scale=(80,1,80), texture='white_cube',
           texture_scale=(80,80), collider='box', color=color.gray)

    Sky()
    DirectionalLight().look_at(Vec3(1,-1,-1))

    player = FirstPersonController()
    player.speed = 5
    mouse.locked = True

    # HUD
    shield_bar = Entity(parent=camera.ui, model='quad', color=color.azure,
                        scale=(0.4,0.03), position=(-0.3,-0.45))
    health_bar = Entity(parent=camera.ui, model='quad', color=color.red,
                        scale=(0.4,0.02), position=(-0.3,-0.40))

    ammo_text = Text(f"Ammo: {ammo}", position=(0.5,-0.45), scale=1.2)
    crosshair = Entity(parent=camera.ui, model='quad', color=color.white, scale=0.01)
    amy_text = Text("", y=0.4, scale=1.5, color=color.cyan)

    damage_overlay = Entity(parent=camera.ui, model='quad',
                            color=color.rgba(255,0,0,0), scale=2)

    spawn_wave()
    amy_text.text = "Amy: Nexer... despierta."
    amy_speak("Nexer despierta")

# --------- ENEMIGOS ---------
def spawn_enemy(tipo="normal"):
    speed, col = 2, color.red
    if tipo == "rapido": speed, col = 4, color.yellow
    if tipo == "tanque": speed, col = 1, color.rgb(150,0,0)

    e = Entity(model='cube', color=col, scale=1.5,
               position=(random.randint(-30,30),1,random.randint(-30,30)),
               collider='box')
    e.speed = speed
    enemies.append(e)

def spawn_wave():
    enemies.clear()
    for _ in range(3):
        spawn_enemy("normal")
        spawn_enemy("rapido")
        spawn_enemy("tanque")

def spawn_boss():
    global boss
    boss = Entity(model='cube', color=color.orange, scale=5,
                  position=(0,2,20), collider='box')
    amy_text.text = "Amy: Entidad mayor detectada."
    amy_speak("Entidad mayor detectada")

# --------- IA ---------
def enemy_shoot(enemy):
    bullet = Entity(model='sphere', color=color.orange, scale=0.2,
                    position=enemy.position)
    def update_bullet():
        bullet.position += (player.position - enemy.position).normalized() * time.dt * 10
        if distance(bullet.position, player.position) < 1:
            take_damage(10)
            destroy(bullet)
    bullet.update = update_bullet

def enemy_ai():
    for e in enemies:
        e.look_at(player)
        e.position += e.forward * time.dt * e.speed
        if random.random() < 0.01:
            enemy_shoot(e)

def boss_ai():
    if not boss: return
    boss.look_at(player)
    boss.position += boss.forward * time.dt * 1.5
    if random.random() < 0.02:
        enemy_shoot(boss)
    if boss_health < 100:
        boss.color = color.red

# --------- COMBATE ---------
def shoot():
    global ammo, boss_health
    if ammo <= 0: return

    ammo -= 1
    ammo_text.text = f"Ammo: {ammo}"
    camera.rotation_x -= 2

    bullet = Entity(model='sphere', color=color.yellow, scale=0.2,
                    position=player.position + player.forward)

    def update_bullet():
        bullet.position += player.forward * time.dt * 20

        for e in enemies:
            if distance(bullet.position, e.position) < 1:
                destroy(e); enemies.remove(e); destroy(bullet)
                if len(enemies) == 0:
                    spawn_boss()
                return

        if boss and distance(bullet.position, boss.position) < 2:
            global boss_health
            boss_health -= 10
            destroy(bullet)
            if boss_health <= 0:
                victory()

    bullet.update = update_bullet
    invoke(lambda: setattr(camera,'rotation_x',0), delay=0.1)

def reload():
    global ammo
    ammo = 30
    ammo_text.text = f"Ammo: {ammo}"

def take_damage(dmg):
    global shield, health, shield_timer
    shield_timer = 0
    damage_overlay.color = color.rgba(255,0,0,120)
    invoke(lambda: setattr(damage_overlay,'color',color.rgba(255,0,0,0)), delay=0.2)

    if shield > 0:
        shield -= dmg
        if shield < 0:
            health += shield
            shield = 0
    else:
        health -= dmg

    if health <= 0:
        game_over()

# --------- FINAL ---------
def victory():
    Text("MISIÓN COMPLETA", scale=3)
    amy_text.text = "Amy: Lo lograste, Nexer."
    amy_speak("Mision completada")

def game_over():
    Text("GAME OVER", scale=3)
    amy_text.text = "Amy: Hemos fallado."
    amy_speak("Hemos fallado")

# --------- INPUT ---------
def input(key):
    global state

    if key == 'escape':
        if state == 'game':
            state = 'pause'
            pause_ui.enabled = True
            mouse.locked = False
        elif state == 'pause':
            resume()

    if state != 'game':
        return

    if key == 'left mouse down':
        shoot()
    if key == 'r':
        reload()

# --------- UPDATE ---------
def update():
    global shield, shield_timer

    if state != 'game':
        return

    enemy_ai()
    boss_ai()

    if shield < 100:
        shield_timer += time.dt
        if shield_timer > 2:
            shield += 20 * time.dt
            shield = min(shield,100)

    shield_bar.scale_x = 0.4 * (shield / 100)
    health_bar.scale_x = 0.4 * (health / 100)

app.run()
