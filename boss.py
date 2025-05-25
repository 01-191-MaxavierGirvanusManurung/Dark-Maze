# boss.py
import pygame
import math
import random # Import random module
from settings import TILE_SIZE, DEFAULT_ANIMATION_SPEED

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, player, all_map_obstacles, boss_type_str, scale_factor=0.8):
        super().__init__()
        self.boss_type_str = boss_type_str
        self.player = player
        self.all_map_obstacles = all_map_obstacles
        self.scale_factor = scale_factor

        self.animations = {}
        # Initialize with a placeholder surface
        self.current_animation_frames = [pygame.Surface((int(TILE_SIZE * scale_factor), int(TILE_SIZE * scale_factor)), pygame.SRCALPHA)]
        if self.current_animation_frames[0]: # Check if surface was created
            self.current_animation_frames[0].fill((255,0,0,100)) # Placeholder color

        self.image = self.current_animation_frames[0] if self.current_animation_frames else pygame.Surface((1,1)) # Fallback
        self.rect = self.image.get_rect(center=(x, y))

        hb_width = int(self.rect.width * 0.5)
        hb_height = int(self.rect.height * 0.7)
        if hb_width == 0: hb_width = TILE_SIZE // 3
        if hb_height == 0: hb_height = TILE_SIZE // 2
        self.hitbox = pygame.Rect(0, 0, hb_width, hb_height)
        self.hitbox.center = self.rect.center

        self.hp = 100
        self.max_hp = 100
        self.attack_damage = 10
        self.speed = 120
        self.detection_radius = TILE_SIZE * 6
        self.attack_range = TILE_SIZE * 0.6 # Used by deal_damage_to_player for attack hitbox size
        self.attack_cooldown_duration = 2000 # Milliseconds
        self.last_attack_time = 0 # Game time in seconds when last attack started
        self.attack_chance_on_collision = 0.6

        self.state = "idle"
        self.facing_right = True
        self.frame_index = 0.0 # For non-attack animations
        self.attack_frame_index = 0.0 # For attack animations

        self.animation_speed = DEFAULT_ANIMATION_SPEED
        self.attack_animation_speed = DEFAULT_ANIMATION_SPEED * 1.2

        self.movement_vector = pygame.math.Vector2(0, 0)
        self.is_dying_animation_finished = False
        self.hurt_timer = 0 # Milliseconds
        self.hurt_duration = 300 # Milliseconds
        self.dealt_damage_this_attack = False # Flag to ensure damage is dealt once per attack animation
        # print(f"Boss {self.boss_type_str} initialized. Attack Cooldown: {self.attack_cooldown_duration/1000}s")


    def _load_animation_frames(self, folder_name, file_prefix, frame_count, use_mirror_suffix=False, mirror_suffix_char='M'):
        frames = []
        base_path = f"{self.boss_type_str}/"
        for i in range(1, frame_count + 1):
            try:
                actual_file_prefix = file_prefix
                if self.boss_type_str == "Wizard" and "attack" in folder_name.lower() and file_prefix == "Attack_" and i > 1:
                     actual_file_prefix = "attack_"
                elif self.boss_type_str == "Wizard" and "attack" in folder_name.lower() and file_prefix == "Attack r" and i > 1:
                    actual_file_prefix = "attack r"

                path_segment = f"{actual_file_prefix}{i}"

                if use_mirror_suffix:
                    path = f"{base_path}{folder_name}/{path_segment}{mirror_suffix_char}.png"
                else:
                    path = f"{base_path}{folder_name}/{path_segment}.png"

                image = pygame.image.load(path).convert_alpha()
                width = int(image.get_width() * self.scale_factor)
                height = int(image.get_height() * self.scale_factor)
                frames.append(pygame.transform.scale(image, (width, height)))
            except pygame.error as e:
                print(f"Error loading boss image: {path} - {e}")
                placeholder_size = int(64 * self.scale_factor)
                placeholder = pygame.Surface((placeholder_size, placeholder_size), pygame.SRCALPHA)
                if placeholder: placeholder.fill((255,0,0,128))
                frames.append(placeholder)
        return frames

    def update_animation_state(self): # Only for non-attack states
        if self.state == "idle":
            anim_key = 'idle_right' if self.facing_right else 'idle_left'
        elif self.state == "chasing":
            if self.boss_type_str in ["Knight", "Samurai"] and 'run_right' in self.animations:
                anim_key = 'run_right' if self.facing_right else 'run_left'
            else:
                anim_key = 'walk_right' if self.facing_right else 'walk_left'
        elif self.state == "hurt":
            anim_key = 'hurt_right' if self.facing_right else 'hurt_left'
        elif self.state == "dying":
            anim_key = 'death_right' if self.facing_right else 'death_left'
        else:
            # print(f"DEBUG: Boss in unknown animation state for update_animation_state: {self.state}")
            anim_key = 'idle_right' if self.facing_right else 'idle_left' # Fallback

        self.current_animation_frames = self.animations.get(anim_key, []) # Default to empty list if key not found
        if not self.current_animation_frames: # If still no frames, use a very basic fallback
            # print(f"Warning: No frames for {anim_key} in {self.boss_type_str}. Using placeholder.")
            placeholder_anim_key = 'idle_right' if self.facing_right else 'idle_left'
            self.current_animation_frames = self.animations.get(placeholder_anim_key, [pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)])


    def animate(self, dt):
        if self.is_dying_animation_finished:
            return

        if self.state == "attacking":
            self.handle_attack_animation(dt)
        else: # For idle, chasing, hurt, dying
            self.update_animation_state() # Set self.current_animation_frames
            if not self.current_animation_frames: # Ensure there are frames
                # print(f"DEBUG: No animation frames for state {self.state} in {self.boss_type_str}")
                self.image = pygame.Surface((int(TILE_SIZE*self.scale_factor), int(TILE_SIZE*self.scale_factor)), pygame.SRCALPHA) # Fallback image
                if self.image: self.image.fill((0,0,255,100)) # Blue placeholder for non-attack missing anim
                return

            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(self.current_animation_frames):
                if self.state == "dying":
                    self.frame_index = len(self.current_animation_frames) - 1
                    self.is_dying_animation_finished = True
                    self.kill()
                    return
                elif self.state == "hurt":
                    self.state = "chasing" # Will be re-evaluated by ai_logic
                    self.frame_index = 0
                else: # idle, chasing
                    self.frame_index = 0
            
            current_frame_idx = int(self.frame_index)
            if 0 <= current_frame_idx < len(self.current_animation_frames):
                self.image = self.current_animation_frames[current_frame_idx]
            # else:
                # print(f"DEBUG: frame_index {self.frame_index} out of bounds for {self.state} (len: {len(self.current_animation_frames)})")


    def handle_attack_animation(self, dt):
        # print(f"DEBUG: {self.boss_type_str} In handle_attack_animation, state: {self.state}")
        attack_frames_key = 'attack_right' if self.facing_right else 'attack_left'
        attack_frames = self.animations.get(attack_frames_key)

        if not attack_frames:
            # print(f"DEBUG: No attack frames for {attack_frames_key} in {self.boss_type_str}. Switching to chasing.")
            self.state = "chasing" # Fallback if attack animation is missing
            self.attack_frame_index = 0
            return

        self.attack_frame_index += self.attack_animation_speed * dt
        # print(f"DEBUG: {self.boss_type_str} attack_frame_index: {self.attack_frame_index:.2f} / {len(attack_frames)}")

        damage_frame_index = max(0, len(attack_frames) // 3) if len(attack_frames) > 0 else 0

        if int(self.attack_frame_index) >= damage_frame_index and not self.dealt_damage_this_attack:
            # print(f"DEBUG: {self.boss_type_str} attempting to deal damage. Frame: {int(self.attack_frame_index)}, DmgFrame: {damage_frame_index}")
            self.deal_damage_to_player()
            self.dealt_damage_this_attack = True

        if self.attack_frame_index >= len(attack_frames):
            # print(f"DEBUG: {self.boss_type_str} attack animation finished.")
            self.attack_frame_index = 0
            self.state = "chasing" # Transition out of attack state, ai_logic will decide next
            self.dealt_damage_this_attack = False # Reset for next attack sequence
        
        current_attack_frame_idx = int(self.attack_frame_index)
        if 0 <= current_attack_frame_idx < len(attack_frames):
            self.image = attack_frames[current_attack_frame_idx]
        # else:
            # print(f"DEBUG: {self.boss_type_str} attack_frame_index {self.attack_frame_index} out of bounds for attack (len: {len(attack_frames)})")


    def deal_damage_to_player(self):
        # print(f"DEBUG: {self.boss_type_str} - INSIDE DEAL DAMAGE TO PLAYER")
        attack_hit_rect = self.hitbox.copy()
        effective_attack_range = self.attack_range * 1.2

        if self.facing_right:
            attack_hit_rect.left = self.hitbox.right
            attack_hit_rect.width = effective_attack_range
        else:
            attack_hit_rect.width = effective_attack_range
            attack_hit_rect.right = self.hitbox.left

        attack_hit_rect.height = self.hitbox.height * 1.2
        attack_hit_rect.centery = self.hitbox.centery
        
        # print(f"  {self.boss_type_str} - Player hitbox: {self.player.hitbox}, Boss attack_hit_rect: {attack_hit_rect}")

        if self.player.hitbox and attack_hit_rect.colliderect(self.player.hitbox) and self.player.hp > 0:
            # print(f"  SUCCESS: {self.boss_type_str} COLLIDED with player hitbox during attack!")
            self.player.take_damage(self.attack_damage) # Player class has its own print for damage taken
        # else:
            # collision_check = "N/A"
            # if self.player.hitbox:
            #     collision_check = attack_hit_rect.colliderect(self.player.hitbox)
            # print(f"  FAIL: {self.boss_type_str} attack did not connect. PlayerHP:{self.player.hp}, PlayerHitboxExists:{self.player.hitbox is not None}, Collision:{collision_check}")


    def ai_logic(self, dt, current_game_time): # current_game_time is in seconds
        # print(f"DEBUG AI: {self.boss_type_str}, State: {self.state}, Time: {current_game_time:.2f}, LastAtk: {self.last_attack_time:.2f}, NextAtkAfter: {self.last_attack_time + (self.attack_cooldown_duration/1000.0):.2f}")
        
        if self.state == "dying" or self.state == "attacking": # If already attacking, let animation finish
            # if self.state == "attacking": print(f"DEBUG AI: {self.boss_type_str} is busy attacking.")
            return

        if self.state == "hurt":
            self.hurt_timer += dt * 1000 # dt is seconds
            if self.hurt_timer >= self.hurt_duration:
                self.state = "chasing" # Re-evaluate
                self.hurt_timer = 0
                self.frame_index = 0 # Reset non-attack animation index
            else:
                self.movement_vector = pygame.math.Vector2(0,0) # Stay still
                return

        if self.player.hp <= 0:
            self.state = "idle"
            self.movement_vector = pygame.math.Vector2(0,0)
            return

        player_pos = pygame.math.Vector2(self.player.hitbox.center)
        boss_pos = pygame.math.Vector2(self.hitbox.center)
        # distance_to_player = boss_pos.distance_to(player_pos) if player_pos != boss_pos else 0 # Causes error if perfectly aligned
        distance_to_player = 0
        if player_pos != boss_pos: # Check to prevent error with distance_to if positions are identical
             distance_to_player = boss_pos.distance_to(player_pos)


        if player_pos.x < boss_pos.x:
            self.facing_right = False
        else:
            self.facing_right = True

        colliding_with_player = False
        if self.player.hitbox and self.hitbox.colliderect(self.player.hitbox):
            colliding_with_player = True
            # print(f"DEBUG AI: {self.boss_type_str} COLLIDING with player. Dist: {distance_to_player:.1f}")
        
        # Corrected Cooldown Check: game_time is seconds, cooldown_duration is ms
        cooldown_in_seconds = self.attack_cooldown_duration / 1000.0
        can_attack_cooldown = (current_game_time - self.last_attack_time) >= cooldown_in_seconds
        
        # if colliding_with_player:
        #     print(f"DEBUG AI: {self.boss_type_str} - Colliding: {colliding_with_player}, Cooldown Ready: {can_attack_cooldown} ({(current_game_time - self.last_attack_time):.2f}s / {cooldown_in_seconds:.2f}s)")

        if colliding_with_player and can_attack_cooldown:
            if random.random() < self.attack_chance_on_collision:
                # print(f"DEBUG AI: {self.boss_type_str} ATTEMPTING ATTACK (RANDOM SUCCESS)")
                self.state = "attacking"
                self.attack_frame_index = 0 # Reset attack animation
                self.last_attack_time = current_game_time # Record time of this attack
                self.movement_vector = pygame.math.Vector2(0, 0) # Stop moving to attack
                self.dealt_damage_this_attack = False # Reset for this new attack
                # print(f"DEBUG AI: {self.boss_type_str} -> ATTACKING. Last attack time: {self.last_attack_time:.2f}")
                return # Important: exit AI to let attack animation play

        # If not attacking, then decide to chase or idle
        if distance_to_player <= self.detection_radius:
            if self.state != "attacking": # Ensure state wasn't just set to attacking
                self.state = "chasing"
                current_speed = self.speed
                if self.boss_type_str in ["Knight", "Samurai"] and hasattr(self, 'run_speed'):
                    current_speed = self.run_speed
                
                # Move only if not too close (prevents jitter) and player exists
                if distance_to_player > TILE_SIZE * 0.05 and self.player.hp > 0 :
                    try:
                        self.movement_vector = (player_pos - boss_pos).normalize() * current_speed
                    except ValueError: # Avoid error if player_pos is exactly boss_pos
                        self.movement_vector = pygame.math.Vector2(0,0)
                else:
                    self.movement_vector = pygame.math.Vector2(0,0) # Stop if too close or player dead
        else:
            if self.state != "attacking":
                self.state = "idle"
                self.movement_vector = pygame.math.Vector2(0, 0)
        
        # if self.state == "chasing": print(f"DEBUG AI: {self.boss_type_str} Chasing. Vec: {self.movement_vector}")
        # elif self.state == "idle": print(f"DEBUG AI: {self.boss_type_str} Idling.")


    def move_and_collide(self, dt):
        # This method should only be called if state is "chasing"
        if self.state != "chasing" or self.movement_vector.length_squared() == 0:
            return

        self.hitbox.x += self.movement_vector.x * dt
        for obstacle_obj in self.all_map_obstacles:
            obs_rect = obstacle_obj['rect']
            obs_type = obstacle_obj['type']
            if obs_type in ['wall', 'door'] and self.hitbox.colliderect(obs_rect):
                if self.movement_vector.x > 0:
                    self.hitbox.right = obs_rect.left
                elif self.movement_vector.x < 0:
                    self.hitbox.left = obs_rect.right
                self.movement_vector.x = 0 # Stop horizontal movement

        self.hitbox.y += self.movement_vector.y * dt
        for obstacle_obj in self.all_map_obstacles:
            obs_rect = obstacle_obj['rect']
            obs_type = obstacle_obj['type']
            if obs_type in ['wall', 'door'] and self.hitbox.colliderect(obs_rect):
                if self.movement_vector.y > 0:
                    self.hitbox.bottom = obs_rect.top
                elif self.movement_vector.y < 0:
                    self.hitbox.top = obs_rect.bottom
                self.movement_vector.y = 0 # Stop vertical movement
        
        self.rect.center = self.hitbox.center


    def take_damage(self, amount):
        if self.state == "dying": return

        self.hp -= amount
        # print(f"Boss {self.boss_type_str} took {amount} damage. HP: {self.hp}/{self.max_hp}")
        if self.hp <= 0:
            self.hp = 0
            self.die()
        else:
            if self.state not in ["attacking", "dying", "hurt"]: # Don't interrupt attack/death, or re-trigger hurt if already hurt
                # print(f"Boss {self.boss_type_str} switching to HURT state.")
                self.state = "hurt"
                self.frame_index = 0 # Reset non-attack animation index
                self.hurt_timer = 0

    def die(self):
        if self.state != "dying":
            # print(f"Boss {self.boss_type_str} is DYING.")
            self.state = "dying"
            self.frame_index = 0 # Reset non-attack animation index for death animation
            self.movement_vector = pygame.math.Vector2(0, 0)

    def draw_hp_bar(self, surface, camera_offset):
        if self.state == "dying" and self.is_dying_animation_finished: return

        bar_width = 60
        bar_height = 8
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0

        bar_x = self.hitbox.centerx - bar_width // 2 - camera_offset.x
        bar_y = self.hitbox.top - 15 - camera_offset.y

        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (200, 0, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        pygame.draw.rect(surface, (220, 220, 220), (bar_x, bar_y, bar_width, bar_height), 1)


    def update(self, dt, current_game_time, camera_offset):
        if self.is_dying_animation_finished:
            if self.alive(): self.kill()
            return

        self.ai_logic(dt, current_game_time) # Determines state and movement_vector

        if self.state == "chasing": # Only move if chasing
            self.move_and_collide(dt)
        
        self.animate(dt) # Handles animation based on current state, including attack

        # Ensure rect position is updated based on hitbox after all logic
        if hasattr(self, 'image') and self.image and hasattr(self, 'hitbox') and self.hitbox:
            self.rect = self.image.get_rect(center=self.hitbox.center)
        # else:
            # print(f"Warning: Boss {self.boss_type_str} missing image or hitbox for rect update.")


# --- Knight Boss ---
class KnightBoss(Boss):
    def __init__(self, x, y, player, all_map_obstacles, scale_factor=0.9):
        super().__init__(x, y, player, all_map_obstacles, "Knight", scale_factor)
        self.hp = 200
        self.max_hp = 200
        self.attack_damage = 20
        self.speed = 90
        self.run_speed = 140
        self.attack_range = TILE_SIZE * 0.75 
        self.attack_cooldown_duration = 2500 #ms
        self.animation_speed = DEFAULT_ANIMATION_SPEED * 0.8
        self.attack_animation_speed = DEFAULT_ANIMATION_SPEED * 1.0
        self.attack_chance_on_collision = 0.7 

        self.animations['walk_right'] = self._load_animation_frames("walk", "Walk_", 8)
        self.animations['walk_left'] = self._load_animation_frames("walk_r", "Walk_", 8, use_mirror_suffix=True)
        self.animations['run_right'] = self._load_animation_frames("run", "Run_", 7)
        self.animations['run_left'] = self._load_animation_frames("run_r", "Run_", 7, use_mirror_suffix=True)
        self.animations['idle_right'] = self._load_animation_frames("idle", "Idle_", 3)
        self.animations['idle_left'] = self._load_animation_frames("idle_r", "Idle_", 3, use_mirror_suffix=True)
        self.animations['attack_right'] = self._load_animation_frames("attack", "Attack_", 13)
        self.animations['attack_left'] = self._load_animation_frames("attack_r", "Attack_", 13, use_mirror_suffix=True)
        self.animations['hurt_right'] = self._load_animation_frames("hurt", "Hurt_", 2)
        self.animations['hurt_left'] = self._load_animation_frames("hurt_r", "Hurt_", 2, use_mirror_suffix=True)
        self.animations['death_right'] = self._load_animation_frames("dead", "Dead_", 6)
        self.animations['death_left'] = self._load_animation_frames("dead_r", "Dead_", 6, use_mirror_suffix=True)

        self.update_animation_state() # Initialize current_animation_frames and image
        if self.current_animation_frames and len(self.current_animation_frames) > 0 :
             self.image = self.current_animation_frames[0]
        else: # Fallback if animations didn't load
            self.image = pygame.Surface((int(TILE_SIZE*self.scale_factor), int(TILE_SIZE*self.scale_factor)), pygame.SRCALPHA)
            if self.image: self.image.fill((255,100,100,100))
        
        self.rect = self.image.get_rect(center=(x,y)) # Re-set rect after image is confirmed
        hb_width = int(self.rect.width * 0.40)
        hb_height = int(self.rect.height * 0.70)
        self.hitbox = pygame.Rect(0,0, hb_width, hb_height)
        self.hitbox.center = self.rect.center


# --- Wizard Boss ---
class WizardBoss(Boss):
    def __init__(self, x, y, player, all_map_obstacles, scale_factor=0.8):
        super().__init__(x, y, player, all_map_obstacles, "Wizard", scale_factor)
        self.hp = 120
        self.max_hp = 120
        self.attack_damage = 25
        self.speed = 70
        self.attack_range = TILE_SIZE * 0.8 
        self.attack_cooldown_duration = 2800 #ms
        self.animation_speed = DEFAULT_ANIMATION_SPEED * 0.7
        self.attack_animation_speed = DEFAULT_ANIMATION_SPEED * 0.9
        self.attack_chance_on_collision = 0.5 

        self.animations['walk_right'] = self._load_animation_frames("walk", "walk ", 7)
        self.animations['walk_left'] = self._load_animation_frames("walk r", "walk r", 7)
        self.animations['idle_right'] = self._load_animation_frames("idle", "idle ", 8)
        self.animations['idle_left'] = self._load_animation_frames("idle r", "idle r", 8)
        self.animations['attack_right'] = self._load_animation_frames("attack", "Attack_", 7)
        self.animations['attack_left'] = self._load_animation_frames("attack r", "Attack r", 7)
        self.animations['hurt_right'] = self._load_animation_frames("hurt", "hurt ", 4)
        self.animations['hurt_left'] = self._load_animation_frames("hurt r", "hurt r", 4)
        self.animations['death_right'] = self._load_animation_frames("dead", "Dead ", 4)
        self.animations['death_left'] = self._load_animation_frames("dead r", "dead r", 4)

        self.update_animation_state()
        if self.current_animation_frames and len(self.current_animation_frames) > 0 :
            self.image = self.current_animation_frames[0]
        else:
            self.image = pygame.Surface((int(TILE_SIZE*self.scale_factor), int(TILE_SIZE*self.scale_factor)), pygame.SRCALPHA)
            if self.image: self.image.fill((100,255,100,100))

        self.rect = self.image.get_rect(center=(x,y))
        hb_width = int(self.rect.width * 0.45)
        hb_height = int(self.rect.height * 0.75)
        self.hitbox = pygame.Rect(0,0, hb_width, hb_height)
        self.hitbox.center = self.rect.center


# --- Samurai Boss ---
class SamuraiBoss(Boss):
    def __init__(self, x, y, player, all_map_obstacles, scale_factor=0.85):
        super().__init__(x, y, player, all_map_obstacles, "Samurai", scale_factor)
        self.hp = 160
        self.max_hp = 160
        self.attack_damage = 15
        self.speed = 100
        self.run_speed = 160
        self.attack_range = TILE_SIZE * 0.85 
        self.attack_cooldown_duration = 1800 #ms 
        self.animation_speed = DEFAULT_ANIMATION_SPEED * 0.9
        self.attack_animation_speed = DEFAULT_ANIMATION_SPEED * 1.3
        self.attack_chance_on_collision = 0.75 

        self.animations['walk_right'] = self._load_animation_frames("walk", "Walk ", 9)
        self.animations['walk_left'] = self._load_animation_frames("walk r", "Walk r", 9)
        self.animations['run_right'] = self._load_animation_frames("run", "Run ", 8)
        self.animations['run_left'] = self._load_animation_frames("run r", "Run r", 8)
        self.animations['idle_right'] = self._load_animation_frames("idle", "Idle ", 6)
        self.animations['idle_left'] = self._load_animation_frames("idle r", "Idle r", 6)

        self.animations['attack_right'] = self._load_animation_frames("attack1", "Attack ", 4)
        self.animations['attack_left'] = self._load_animation_frames("attack1 r", "Attack r", 4)

        self.animations['attack2_right'] = self._load_animation_frames("attack2", "Attack ", 5)
        self.animations['attack2_left'] = self._load_animation_frames("attack2 r", "Attack r", 5)
        self.animations['attack3_right'] = self._load_animation_frames("attack3", "Attack ", 4)
        self.animations['attack3_left'] = self._load_animation_frames("attack3 r", "Attack r", 4)

        self.animations['hurt_right'] = self._load_animation_frames("hurt", "Hurt ", 3)
        self.animations['hurt_left'] = self._load_animation_frames("hurt r", "Hurt r", 3)
        self.animations['death_right'] = self._load_animation_frames("dead", "Dead ", 4)
        self.animations['death_left'] = self._load_animation_frames("dead r", "Dead r", 4)

        self.update_animation_state()
        if self.current_animation_frames and len(self.current_animation_frames) > 0:
            self.image = self.current_animation_frames[0]
        else:
            self.image = pygame.Surface((int(TILE_SIZE*self.scale_factor), int(TILE_SIZE*self.scale_factor)), pygame.SRCALPHA)
            if self.image: self.image.fill((100,100,255,100))

        self.rect = self.image.get_rect(center=(x,y))
        hb_width = int(self.rect.width * 0.35)
        hb_height = int(self.rect.height * 0.7)
        self.hitbox = pygame.Rect(0,0, hb_width, hb_height)
        self.hitbox.center = self.rect.center
