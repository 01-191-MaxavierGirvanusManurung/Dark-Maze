import pygame
from settings import TILE_SIZE, DEFAULT_ANIMATION_SPEED
import settings as app_settings

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Menggunakan path absolut yang Anda berikan
        base_sprite_path_player = "Player/" 
        base_sound_path_player = "assets/"

        def _load_and_scale_player(base_path, subfolder, file_prefix, count, scale_factor=0.8):
            frames = []
            for i in range(1, count + 1):
                try:
                    # Contoh: D:\char\char\Player\walk\Walk_1.png
                    path = f"{base_path}{subfolder}/Walk_{i}.png" # Asumsi format file Walk_{i}.png
                    if "walk_r" in subfolder:
                         path = f"{base_path}{subfolder}/Walk_r{i}.png"
                    elif "run" in subfolder and "run_r" not in subfolder:
                         path = f"{base_path}{subfolder}/Run {i}.png"
                    elif "run_r" in subfolder:
                         path = f"{base_path}{subfolder}/Run r{i}.png"
                    elif "idle" in subfolder and "idle_r" not in subfolder:
                         path = f"{base_path}{subfolder}/Idle {i}.png"
                    elif "idle_r" in subfolder:
                         path = f"{base_path}{subfolder}/Idle r{i}.png"
                    elif "attack 1" in subfolder and "attack 1_r" not in subfolder:
                         path = f"{base_path}{subfolder}/Attack {i}.png"
                    elif "attack 1_r" in subfolder:
                         path = f"{base_path}{subfolder}/Attack r{i}.png"
                    elif "attack 2" in subfolder and "attack 2_r" not in subfolder:
                         path = f"{base_path}{subfolder}/Attack {i}.png"
                    elif "attack 2_r" in subfolder:
                         path = f"{base_path}{subfolder}/Attack r{i}.png"
                    else: # Default jika tidak cocok, mungkin perlu disesuaikan
                        path = f"{base_path}{subfolder}/{file_prefix}{i}.png"


                    image = pygame.image.load(path).convert_alpha()
                    width = int(image.get_width() * scale_factor)
                    height = int(image.get_height() * scale_factor)
                    frames.append(pygame.transform.scale(image, (width, height)))
                except pygame.error as e:
                    print(f"Error loading player image: {path} - {e}")
                    placeholder = pygame.Surface((int(64*scale_factor), int(64*scale_factor)), pygame.SRCALPHA)
                    placeholder.fill((0,255,0,128))
                    frames.append(placeholder)
            return frames

        self.walk_right = _load_and_scale_player(base_sprite_path_player, "walk", "Walk_", 8)
        self.walk_left = _load_and_scale_player(base_sprite_path_player, "walk_r", "Walk_r", 8)
        self.run_right = _load_and_scale_player(base_sprite_path_player, "run", "Run ", 8)
        self.run_left = _load_and_scale_player(base_sprite_path_player, "run_r", "Run r", 8)
        self.idle_right = _load_and_scale_player(base_sprite_path_player, "idle", "Idle ", 6)
        self.idle_left = _load_and_scale_player(base_sprite_path_player, "idle_r", "Idle r", 6)
        self.attack_right1 = _load_and_scale_player(base_sprite_path_player, "attack 1", "Attack ", 4)
        self.attack_left1 = _load_and_scale_player(base_sprite_path_player, "attack 1_r", "Attack r", 4)
        self.attack_right2 = _load_and_scale_player(base_sprite_path_player, "attack 2", "Attack ", 4)
        self.attack_left2 = _load_and_scale_player(base_sprite_path_player, "attack 2_r", "Attack r", 4)


        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        try:
            self.attack_sound1 = pygame.mixer.Sound(f"{base_sound_path_player}player attack 1.WAV")
        except pygame.error as e:
            print(f"Error loading sound: {base_sound_path_player}player attack 1.WAV - {e}")
            self.attack_sound1 = None
        try:
            self.attack_sound2 = pygame.mixer.Sound(f"{base_sound_path_player}player attack 2.WAV")
        except pygame.error as e:
            print(f"Error loading sound: {base_sound_path_player}player attack 2.WAV - {e}")
            self.attack_sound2 = None
        
        # Status animasi
        self.is_attacking1 = False
        self.is_attacking2 = False
        self.attack_index = 0.0
        self.char_index = 0.0
        self.facing_right = True 
        self.animation = self.idle_right[0] if self.idle_right else pygame.Surface((1,1)) # Fallback jika idle_right kosong
        self.current_animation_frames = self.idle_right

        self.walk_anim_speed = DEFAULT_ANIMATION_SPEED
        self.run_anim_speed = DEFAULT_ANIMATION_SPEED * 1.5
        self.idle_anim_speed = DEFAULT_ANIMATION_SPEED * 0.5
        self.attack_anim_speed = DEFAULT_ANIMATION_SPEED * 1.2

        self.hp = 50 # Increased HP for testing with bosses
        self.max_hp = 100
        self.attack_damage1 = 10
        self.attack_damage2 = 20
        self.attack_range = TILE_SIZE * 0.7 # Adjusted for TILE_SIZE

        self.rect = self.animation.get_rect()
        new_width = int(self.rect.width * 0.5) 
        new_height = int(self.rect.height * 0.8) 
        if new_width == 0 or new_height == 0: # Safety for placeholder
            new_width, new_height = TILE_SIZE//2, TILE_SIZE -10

        self.hitbox = pygame.Rect(0, 0, new_width, new_height)
        self.hitbox.midbottom = self.rect.midbottom

    def _update_animation_frame(self, dt, speed_multiplier=1.0):
        if not self.current_animation_frames: 
            return
        self.char_index += DEFAULT_ANIMATION_SPEED * speed_multiplier * dt
        if self.char_index >= len(self.current_animation_frames):
            self.char_index = 0
        self.animation = self.current_animation_frames[int(self.char_index)]

    def attack(self, target_group, camera_offset_x=0, camera_offset_y=0):
        if not (self.is_attacking1 or self.is_attacking2) or not target_group: # Added check for empty target_group
            return

        damage = self.attack_damage1 if self.is_attacking1 else self.attack_damage2
        attack_rect_width = self.attack_range 
        attack_rect_height = self.hitbox.height * 0.8 
        
        if self.facing_right:
            attack_rect_x = self.hitbox.right
        else:
            attack_rect_x = self.hitbox.left - attack_rect_width
        
        attack_rect_y = self.hitbox.centery - attack_rect_height / 2
        
        attack_hit_rect = pygame.Rect(attack_rect_x, attack_rect_y, attack_rect_width, attack_rect_height)

        # # For debugging, draw attack_hit_rect
        # screen = pygame.display.get_surface()
        # if screen: # Ensure screen exists
        #     debug_rect = attack_hit_rect.copy()
        #     debug_rect.x -= camera_offset_x
        #     debug_rect.y -= camera_offset_y
        #     pygame.draw.rect(screen, (255,0,0, 100), debug_rect, 2)


        for target in target_group:
            if hasattr(target, 'hitbox') and target.hitbox and attack_hit_rect.colliderect(target.hitbox): # Check if target.hitbox is not None
                if hasattr(target, 'take_damage') and target.hp > 0 : # Only hit living targets
                    target.take_damage(damage)
                    # print(f"Player hit {getattr(target, 'boss_type', 'target')} for {damage} damage.")


    def take_damage(self, amount):
        self.hp -= amount
        print(f"Player took {amount} damage. HP: {self.hp}/{self.max_hp}")
        if self.hp < 0:
            self.hp = 0
        if self.hp == 0:
            self.die()

    def die(self):
        print("Player mati!")
        # Potentially trigger a game over state or respawn mechanic here.
        # For now, it just prints. The game loop might not handle player death yet.
        # To make it visible, let's make the player a ghost or something simple
        if self.animation:
            try:
                self.animation.set_alpha(100) # Make player semi-transparent
            except: pass # Some surfaces might not support set_alpha well if not .convert_alpha()
        # A proper game over would stop player input and show a message.

    def draw_hp_bar(self, surface, camera_offset):
        if not self.hitbox: return # Safety check
        bar_width = 50
        bar_height = 8
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        
        bar_x = self.hitbox.centerx - bar_width // 2 - camera_offset.x
        bar_y = self.hitbox.top - 15 - camera_offset.y

        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (200, 50, 50), (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def attack_animation(self, dt):
        if self.attack_index == 0: # Play sound at the start of the animation
            active_sound = None
            if self.is_attacking1 and self.attack_sound1:
                active_sound = self.attack_sound1
            elif self.is_attacking2 and self.attack_sound2:
                active_sound = self.attack_sound2
            
            if active_sound:
                active_sound.set_volume(app_settings.global_volume)
                active_sound.play()

        self.attack_index += self.attack_anim_speed * dt

        current_attack_frames = []
        if self.is_attacking1:
            current_attack_frames = self.attack_right1 if self.facing_right else self.attack_left1
        elif self.is_attacking2:
            current_attack_frames = self.attack_right2 if self.facing_right else self.attack_left2
        
        if not current_attack_frames: 
            self.is_attacking1 = False
            self.is_attacking2 = False
            self.attack_index = 0
            return

        if int(self.attack_index) >= len(current_attack_frames):
            self.attack_index = 0
            self.is_attacking1 = False
            self.is_attacking2 = False
            self.char_index = 0 # Reset char_index to avoid animation jump
        else:
            self.animation = current_attack_frames[int(self.attack_index)]
            self.current_animation_frames = current_attack_frames # Keep track for consistent updates

    def char_animation(self, dt):
        keys = pygame.key.get_pressed()
        moving_x = False
        moving_y = False # Renamed from moving for clarity

        if self.is_attacking1 or self.is_attacking2:
            self.attack_animation(dt)
            # Call attack logic here if attack is tied to specific frames
            # For now, attack logic is triggered by key press and handled in main game loop or by attack_animation end
            return # Don't process movement/idle animations while attacking

        # Determine current animation set based on movement keys
        next_anim_frames = self.current_animation_frames # Default to current
        anim_speed_multiplier = 1.0 # Default walk animation speed

        if keys[pygame.K_d] and not keys[pygame.K_a]: # Moving right
            next_anim_frames = self.run_right if keys[pygame.K_p] else self.walk_right
            self.facing_right = True
            moving_x = True
        elif keys[pygame.K_a] and not keys[pygame.K_d]: # Moving left
            next_anim_frames = self.run_left if keys[pygame.K_p] else self.walk_left
            self.facing_right = False
            moving_x = True
        
        # Vertical movement can also set animation if not already moving horizontally
        if (keys[pygame.K_w] or keys[pygame.K_s]) and not (keys[pygame.K_w] and keys[pygame.K_s]):
            moving_y = True
            if not moving_x: # Only set walk/run anim if not already set by horizontal
                if self.facing_right:
                    next_anim_frames = self.run_right if keys[pygame.K_p] else self.walk_right
                else:
                    next_anim_frames = self.run_left if keys[pygame.K_p] else self.walk_left
        
        if not moving_x and not moving_y: # Idle
            next_anim_frames = self.idle_right if self.facing_right else self.idle_left
            anim_speed_multiplier = 0.5 # Idle animation is slower
        elif keys[pygame.K_p] and (moving_x or moving_y): # Running
            anim_speed_multiplier = 1.5 # Run animation is faster
        
        if self.current_animation_frames != next_anim_frames:
            self.current_animation_frames = next_anim_frames
            self.char_index = 0 # Reset frame index when animation set changes

        self._update_animation_frame(dt, anim_speed_multiplier)


    def update(self, dt):
        if self.hp <= 0: # If player is dead, maybe a specific "dead" animation or behavior
            # For now, just use the last frame or a ghost effect from die()
            # And ensure rect updates.
            if self.animation and self.hitbox:
                 self.rect = self.animation.get_rect(midbottom=self.hitbox.midbottom)
            return


        self.char_animation(dt)
        # Ensure rect image always updates its position from hitbox
        if self.animation and self.hitbox: # Only if animation (image) and hitbox exist
            self.rect = self.animation.get_rect(midbottom=self.hitbox.midbottom)
        elif self.hitbox : # Fallback if no animation (e.g., all images failed to load) but hitbox exists
            self.rect.midbottom = self.hitbox.midbottom
