# main.py

import pygame, sys
from settings import * # width, height, fps, TILE_SIZE
import settings as app_settings # Impor modul settings untuk akses global_volume dan collision_map
from player import Player
from button import Button
from musik import play_music, stop_music, set_music_volume
from chest import generate_random_chests
from boss import KnightBoss, WizardBoss, SamuraiBoss # Import Boss classes

def get_font(size):
    try:
        return pygame.font.Font("assets/font.ttf", size)
    except pygame.error as e:
        print(f"Error loading font: assets/font.ttf - {e}. Using default font.")
        return pygame.font.Font(None, size + 10) # Default font larger for visibility


def options_menu(screen):
    running = True
    font_title = get_font(45)
    font_buttons = get_font(75)

    try:
        BG = pygame.image.load("assets/Background.png")
    except pygame.error as e:
        print(f"Error loading Background.png: {e}")
        BG = pygame.Surface(screen.get_size())
        BG.fill((30,30,30))


    LEFT_BUTTON = Button(image=None, pos=(screen.get_width() // 2 - 100, 350), text_input="<", font=font_buttons, base_color="#d7fcd4", hovering_color="White")
    RIGHT_BUTTON = Button(image=None, pos=(screen.get_width() // 2 + 100, 350), text_input=">", font=font_buttons, base_color="#d7fcd4", hovering_color="White")
    BACK_BUTTON = Button(image=None, pos=(screen.get_width() // 2, 460), text_input="BACK", font=font_buttons, base_color="#d7fcd4", hovering_color="White")

    while running:
        screen.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title_text = font_title.render(f"OPTIONS - Volume: {app_settings.global_volume*100:.0f}%", True, "#b68f40")
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 260))
        screen.blit(title_text, title_rect)

        for button in [LEFT_BUTTON, RIGHT_BUTTON, BACK_BUTTON]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(mouse_pos):
                    running = False
                elif LEFT_BUTTON.checkForInput(mouse_pos):
                    new_volume = round(app_settings.global_volume - 0.1, 1)
                    if new_volume < 0: new_volume = 0.0
                    set_music_volume(new_volume) 
                elif RIGHT_BUTTON.checkForInput(mouse_pos):
                    new_volume = round(app_settings.global_volume + 0.1, 1)
                    if new_volume > 1: new_volume = 1.0
                    set_music_volume(new_volume) 

        pygame.display.update()

def congratulations_screen(screen):
    running = True
    font_title = get_font(75)
    font_subtitle = get_font(40)
    font_buttons = get_font(60)
    play_music("assets/main menu.WAV") 

    try:
        BG = pygame.image.load("assets/Background.png") 
    except pygame.error as e:
        print(f"Error loading Background.png: {e}")
        BG = pygame.Surface(screen.get_size())
        BG.fill((20, 60, 20)) 

    MENU_BUTTON = Button(image=None, pos=(screen.get_width() // 2, 450),
                         text_input="MAIN MENU", font=font_buttons, base_color="#d7fcd4", hovering_color="White")
    QUIT_BUTTON = Button(image=None, pos=(screen.get_width() // 2, 600),
                         text_input="QUIT", font=font_buttons, base_color="#d7fcd4", hovering_color="White")

    while running:
        screen.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title_text = font_title.render("CONGRATULATIONS!", True, "#FFD700") 
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(title_text, title_rect)

        subtitle_text = font_subtitle.render("You have escaped the Dark Maze!", True, "#FFFFFF") 
        subtitle_rect = subtitle_text.get_rect(center=(screen.get_width() // 2, 300))
        screen.blit(subtitle_text, subtitle_rect)

        for button in [MENU_BUTTON, QUIT_BUTTON]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if MENU_BUTTON.checkForInput(mouse_pos):
                    running = False 
                    return 
                elif QUIT_BUTTON.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def main_menu():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512) 

    SCREEN = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Dark Maze - Menu")

    play_music("assets/main menu.WAV")

    try:
        BG = pygame.image.load("assets/Background.png")
    except pygame.error as e:
        print(f"Error loading Background.png: {e}")
        BG = pygame.Surface(SCREEN.get_size())
        BG.fill((30,30,30))

    font_title = get_font(100)
    font_buttons = get_font(75)

    try:
        play_rect_img = pygame.image.load("assets/Play Rect.png")
        options_rect_img = pygame.image.load("assets/Options Rect.png")
        quit_rect_img = pygame.image.load("assets/Quit Rect.png")
    except pygame.error as e:
        print(f"Error loading button images: {e}")
        play_rect_img, options_rect_img, quit_rect_img = None, None, None


    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = font_title.render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(width // 2, 100))

        PLAY_BUTTON = Button(image=play_rect_img, pos=(width // 2, 250),
                            text_input="PLAY", font=font_buttons, base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=options_rect_img, pos=(width // 2, 400),
                            text_input="OPTIONS", font=font_buttons, base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=quit_rect_img, pos=(width // 2, 550),
                            text_input="QUIT", font=font_buttons, base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    stop_music()
                    
                    game = Game()
                    game_result = game.run() 

                    if game_result == "WON":
                        congratulations_screen(SCREEN)
                        play_music("assets/main menu.WAV") 
                    elif game_result == "ESCAPED" or game_result == "PLAYER_DIED": 
                        if game_result == "PLAYER_DIED":
                            font_game_over = get_font(80)
                            game_over_text = font_game_over.render("GAME OVER", True, (200,0,0))
                            game_over_rect = game_over_text.get_rect(center=(width//2, height//2))
                            SCREEN.blit(game_over_text, game_over_rect)
                            pygame.display.flip()
                            pygame.time.wait(3000) 

                        play_music("assets/main menu.WAV") 
                    

                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options_menu(SCREEN)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Dark Maze')
        self.clock = pygame.time.Clock()
        self.current_game_time = 0 

        self.game_collision_map = [row[:] for row in app_settings.collision_map] 

        self.chests = generate_random_chests(self.game_collision_map, TILE_SIZE, chest_probability=0.03)
        
        self.bosses = pygame.sprite.Group() 

        self.WALK_SPEED_PPS = 200
        self.RUN_SPEED_PPS = 750

        self.map_width_pixels = len(self.game_collision_map[0]) * TILE_SIZE
        self.map_height_pixels = len(self.game_collision_map) * TILE_SIZE

        spawn_x, spawn_y = TILE_SIZE, TILE_SIZE 
        player_spawn_found = False
        for r, row in enumerate(self.game_collision_map):
            for c, tile in enumerate(row):
                if tile == 'p':
                    spawn_x = c * TILE_SIZE
                    spawn_y = r * TILE_SIZE
                    player_spawn_found = True
                    self.game_collision_map[r][c] = 0 
                    break
            if player_spawn_found:
                break
        if not player_spawn_found:
            print("Peringatan: Titik spawn pemain ('p') tidak ditemukan. Spawn di posisi default.")
        
        self.player = Player()
        self.player.hitbox.midbottom = (spawn_x + TILE_SIZE // 2, spawn_y + TILE_SIZE)
        self.player.rect.midbottom = self.player.hitbox.midbottom

        boss_spawn_points = {'k': [], 'w': [], 's': []}
        for r_idx, row_val in enumerate(self.game_collision_map):
            for c_idx, tile_val in enumerate(row_val):
                if tile_val in boss_spawn_points:
                    bx, by = c_idx * TILE_SIZE + TILE_SIZE // 2, r_idx * TILE_SIZE + TILE_SIZE 
                    boss_spawn_points[tile_val].append((bx, by))
                    self.game_collision_map[r_idx][c_idx] = 0 

        self.wall_rects, self.goal_rects = self.get_collidables()

        for spawn_char, pos_list in boss_spawn_points.items():
            for pos_x, pos_y in pos_list:
                boss_instance = None
                if spawn_char == 'k':
                    boss_instance = KnightBoss(pos_x, pos_y, self.player, self.wall_rects)
                elif spawn_char == 'w':
                    boss_instance = WizardBoss(pos_x, pos_y, self.player, self.wall_rects)
                elif spawn_char == 's':
                    boss_instance = SamuraiBoss(pos_x, pos_y, self.player, self.wall_rects)
                
                if boss_instance:
                    self.bosses.add(boss_instance)
                    print(f"Spawned {boss_instance.boss_type_str} at ({pos_x},{pos_y})")


        self.camera_offset = pygame.Vector2(0, 0)

        self.light_radius = 250
        self.darkness_color = (0, 0, 0, 230)
        self.font_pickup = get_font(20)
        self.update_light_radius()

        self.inventory = {"keys": 0}
        self.game_won = False 
        self.player_dead = False


    def update_light_radius(self):
        diameter = self.light_radius * 2
        self.light_img = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.light_img, (255, 255, 255, 0), (self.light_radius, self.light_radius), self.light_radius)
        for i in range(self.light_radius, 0, -2): 
            alpha = int(255 * (1 - (i / self.light_radius)**1.5 )) 
            alpha = max(0, min(255, alpha)) 
            pygame.draw.circle(self.light_img, (255, 255, 255, alpha),
                                (self.light_radius, self.light_radius), i)


    def get_collidables(self):
        walls_doors_boundaries = []
        goals = []
        for r_idx, row in enumerate(self.game_collision_map):
            for c_idx, tile in enumerate(row):
                rect = pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == 80:
                    walls_doors_boundaries.append({'rect': rect, 'type': 'wall', 'coords': (c_idx, r_idx)})
                elif tile == 'd':
                    walls_doors_boundaries.append({'rect': rect, 'type': 'door', 'coords': (c_idx, r_idx)})
                elif tile == 'b': 
                    walls_doors_boundaries.append({'rect': rect, 'type': 'boss_boundary', 'coords': (c_idx, r_idx)})
                elif tile == 5: 
                    goals.append(rect)
        return walls_doors_boundaries, goals

    def open_door_at_coords(self, coords_tuple):
        c, r = coords_tuple
        if 0 <= r < len(self.game_collision_map) and 0 <= c < len(self.game_collision_map[0]):
            if self.game_collision_map[r][c] == 'd':
                self.game_collision_map[r][c] = 0 
                self.wall_rects, self.goal_rects = self.get_collidables() 
                for boss in self.bosses:
                    if hasattr(boss, 'all_map_obstacles'): 
                        boss.all_map_obstacles = self.wall_rects
                print(f"Door at ({c},{r}) opened. Collidables refreshed.")


    def handle_movement(self, dt):
        if self.player.hp <= 0: 
            return

        keys = pygame.key.get_pressed()
        player_hitbox = self.player.hitbox

        if not self.player.is_attacking1 and not self.player.is_attacking2:
            current_speed = self.RUN_SPEED_PPS if keys[pygame.K_p] else self.WALK_SPEED_PPS

            dx = 0
            if keys[pygame.K_d] and not keys[pygame.K_a]: dx = current_speed * dt
            elif keys[pygame.K_a] and not keys[pygame.K_d]: dx = -current_speed * dt

            if dx != 0:
                player_hitbox.x += dx
                for collidable_obj in self.wall_rects: 
                    coll_rect = collidable_obj['rect']
                    coll_type = collidable_obj['type']
                    
                    # --- PEMAIN BISA MENEMBUS 'b' (BOSS BOUNDARY) ---
                    if coll_type == 'boss_boundary': 
                        continue 
                    # --- AKHIR PERUBAHAN ---
                        
                    if player_hitbox.colliderect(coll_rect):
                        if coll_type == 'door':
                            if self.inventory["keys"] >= 3: 
                                self.inventory["keys"] -= 3
                                print(f"Door unlocked! Keys left: {self.inventory['keys']}")
                                self.open_door_at_coords(collidable_obj['coords'])
                            else: 
                                if dx > 0: player_hitbox.right = coll_rect.left
                                elif dx < 0: player_hitbox.left = coll_rect.right
                                print("Door is locked. Need 3 key!")
                        elif coll_type == 'wall': 
                            if dx > 0: player_hitbox.right = coll_rect.left
                            elif dx < 0: player_hitbox.left = coll_rect.right
                        break 

            dy = 0
            if keys[pygame.K_w] and not keys[pygame.K_s]: dy = -current_speed * dt
            elif keys[pygame.K_s] and not keys[pygame.K_w]: dy = current_speed * dt

            if dy != 0:
                player_hitbox.y += dy
                for collidable_obj in self.wall_rects: 
                    coll_rect = collidable_obj['rect']
                    coll_type = collidable_obj['type']

                    # --- PEMAIN BISA MENEMBUS 'b' (BOSS BOUNDARY) ---
                    if coll_type == 'boss_boundary':
                        continue
                    # --- AKHIR PERUBAHAN ---

                    if player_hitbox.colliderect(coll_rect):
                        if coll_type == 'door':
                            if self.inventory["keys"] >= 3: 
                                self.inventory["keys"] -= 3
                                print(f"Door unlocked! Keys left: {self.inventory['keys']}")
                                self.open_door_at_coords(collidable_obj['coords'])
                            else: 
                                if dy > 0: player_hitbox.bottom = coll_rect.top
                                elif dy < 0: player_hitbox.top = coll_rect.bottom
                                print("Door is locked. Need 3 key!")
                        elif coll_type == 'wall': 
                            if dy > 0: player_hitbox.bottom = coll_rect.top
                            elif dy < 0: player_hitbox.top = coll_rect.bottom
                        break
            
            for goal_rect in self.goal_rects:
                if player_hitbox.colliderect(goal_rect):
                    self.game_won = True
                    return 

    def render_lighting(self):
        if not self.player.hitbox: return 
        player_screen_pos = (
            self.player.hitbox.centerx - int(self.camera_offset.x),
            self.player.hitbox.centery - int(self.camera_offset.y)
        )
        darkness = pygame.Surface((width, height), pygame.SRCALPHA)
        darkness.fill(self.darkness_color)
        
        if hasattr(self, 'light_img') and self.light_img:
            light_rect = self.light_img.get_rect(center=player_screen_pos)
            darkness.blit(self.light_img, light_rect, special_flags=pygame.BLEND_RGBA_SUB)
        
        self.screen.blit(darkness, (0, 0))

    def run(self):
        play_music() 
        self.game_won = False
        self.player_dead = False 

        running = True
        while running:
            dt = self.clock.tick(fps) / 1000.0
            self.current_game_time += dt 
            pickup_pressed_this_frame = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_music()
                    pygame.quit()
                    sys.exit() 
                if self.player.hp > 0: 
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_j and not self.player.is_attacking2 and not self.player.is_attacking1:
                            self.player.is_attacking1 = True
                            self.player.attack_index = 0
                            self.player.attack(self.bosses, self.camera_offset.x, self.camera_offset.y) 
                        elif event.key == pygame.K_k and not self.player.is_attacking1 and not self.player.is_attacking2:
                            self.player.is_attacking2 = True
                            self.player.attack_index = 0
                            self.player.attack(self.bosses, self.camera_offset.x, self.camera_offset.y) 
                        elif event.key == pygame.K_l:
                            pickup_pressed_this_frame = True
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_ESCAPE:
                        stop_music()
                        return "ESCAPED" 

            if self.player.hp <= 0 and not self.player_dead:
                self.player_dead = True 
                self.player.die() 
                
            self.handle_movement(dt)

            if self.game_won: 
                stop_music()
                return "WON" 
            
            if self.player_dead:
                stop_music()
                return "PLAYER_DIED"

            self.player.update(dt)
            for chest in self.chests:
                chest.update(self.player, dt) 
            
            for boss in self.bosses:
                boss.update(dt, self.current_game_time, self.camera_offset)
            
            if self.player.hitbox:
                self.camera_offset.x = self.player.hitbox.centerx - width // 2
                self.camera_offset.y = self.player.hitbox.centery - height // 2
                self.camera_offset.x = max(0, min(self.camera_offset.x, self.map_width_pixels - width))
                self.camera_offset.y = max(0, min(self.camera_offset.y, self.map_height_pixels - height))

            self.screen.fill((50,50,50)) 

            for collidable_item in self.wall_rects:
                offset_rect = collidable_item['rect'].move(-self.camera_offset.x, -self.camera_offset.y)
                if self.screen.get_rect().colliderect(offset_rect):
                    color = (0,0,0) 
                    if collidable_item['type'] == 'door': color = (139, 69, 19) 
                    elif collidable_item['type'] == 'boss_boundary': color = (100, 0, 0) 
                    pygame.draw.rect(self.screen, color, offset_rect)

            for goal_rect_item in self.goal_rects:
                offset_goal_rect = goal_rect_item.move(-self.camera_offset.x, -self.camera_offset.y)
                if self.screen.get_rect().colliderect(offset_goal_rect):
                    pygame.draw.rect(self.screen, (0, 100, 0), offset_goal_rect) 

            for chest in list(self.chests): 
                if not chest.finished:
                    chest_draw_pos = chest.rect.move(-self.camera_offset.x, -self.camera_offset.y)
                    if hasattr(chest, 'image') and chest.image: 
                         self.screen.blit(chest.image, chest_draw_pos)

                if chest.reward_given and chest.reward and chest.reward_rect:
                    reward_screen_pos = chest.reward_rect.move(-self.camera_offset.x, -self.camera_offset.y)
                    self.screen.blit(chest.reward, reward_screen_pos)

                    if self.player.hitbox and self.player.hitbox.colliderect(chest.reward_rect):
                        prompt_text = self.font_pickup.render("Tekan L", True, (255, 255, 255))
                        prompt_rect = prompt_text.get_rect(midbottom=reward_screen_pos.midtop)
                        self.screen.blit(prompt_text, prompt_rect)

                        if pickup_pressed_this_frame:
                            if chest.reward_type == "red_potion":
                                self.player.hp = min(self.player.max_hp, self.player.hp + 20)
                                print("❤️ HP ditambah 20")
                            elif chest.reward_type == "blue_potion":
                                self.light_radius += 50
                                self.update_light_radius()
                                print("🔆 Radius cahaya bertambah")
                            elif chest.reward_type == "key":
                                self.inventory["keys"] += 1
                                print(f"🔐 Kunci diperoleh! Total: {self.inventory['keys']}")
                            chest.reward = None 

                keys_pressed = pygame.key.get_pressed() 
                if not chest.opening and not chest.finished and \
                   self.player.hitbox and self.player.hitbox.colliderect(chest.rect) and keys_pressed[pygame.K_l]:
                    chest.open()
            
            for boss in self.bosses:
                if boss.alive() or (boss.state == "dying" and not boss.is_dying_animation_finished):
                    if hasattr(boss, 'image') and boss.image and hasattr(boss, 'rect') and boss.rect:
                        boss_draw_pos = boss.rect.move(-self.camera_offset.x, -self.camera_offset.y)
                        self.screen.blit(boss.image, boss_draw_pos)
                        boss.draw_hp_bar(self.screen, self.camera_offset)


            if self.player.animation and self.player.rect : 
                player_draw_pos = self.player.rect.move(-self.camera_offset.x, -self.camera_offset.y)
                self.screen.blit(self.player.animation, player_draw_pos)
                if self.player.hp > 0: 
                    self.player.draw_hp_bar(self.screen, self.camera_offset)

            self.render_lighting()

            key_text = get_font(25).render(f"Keys: {self.inventory['keys']}", True, (255, 215, 0))
            self.screen.blit(key_text, (10, 10))
            
            player_hp_text = get_font(25).render(f"HP: {self.player.hp}", True, (255,255,255))
            self.screen.blit(player_hp_text, (10, 40))


            pygame.display.flip()
        
        stop_music()
        if self.player_dead: return "PLAYER_DIED" 
        return "ESCAPED" 


if __name__ == '__main__':
    main_menu()
