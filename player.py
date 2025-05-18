import pygame, sys
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Memuat animasi untuk berbagai aksi
        self.walk_right = [pygame.image.load(f'Player/walk/Walk_{i}.png').convert_alpha() for i in range(1, 9)]
        self.walk_left = [pygame.image.load(f'Player/walk_r/Walk_r{i}.png').convert_alpha() for i in range(1,9)]

        self.run_right = [pygame.image.load(f'Player/run/Run {i}.png').convert_alpha() for i in range(1, 9)]
        self.run_left = [pygame.image.load(f'Player/run_r/Run r{i}.png').convert_alpha() for i in range(1,9)]

        self.idle_right = [pygame.image.load(f'Player/idle/Idle {i}.png').convert_alpha() for i in range(1, 7)]
        self.idle_left = [pygame.image.load(f'Player/idle_r/Idle r{i}.png').convert_alpha() for i in range(1, 7)]

        self.attack_right1 = [pygame.image.load(f'Player/attack 1/Attack {i}.png').convert_alpha() for i in range(1, 5)]
        self.attack_left1 = [pygame.image.load(f'Player/attack 1_r/Attack r{i}.png').convert_alpha() for i in range(1, 5)]
        self.attack_right2 = [pygame.image.load(f'Player/attack 2/Attack {i}.png').convert_alpha() for i in range(1, 5)]
        self.attack_left2 = [pygame.image.load(f'Player/attack 2_r/Attack r{i}.png').convert_alpha() for i in range(1, 5)]
        
        # Status animasi
        self.is_attacking1 = False
        self.is_attacking2 = False
        self.attack_index = 0
        self.idle_index = 0
        self.char_index = 0
        self.facing_right = True 
        self.animation = self.walk_right[self.char_index]
        
        # Membuat rect untuk collision dan rendering
        self.rect = self.animation.get_rect(midbottom=(80, 300))

    def framing(self, frame):
        """Menangani perpindahan ke frame berikutnya dalam animasi"""
        if self.char_index >= len(frame):
            self.char_index = 0
        self.animation = frame[int(self.char_index)]

    def attack(self):
        """Menangani animasi serangan"""
        self.attack_index += 0.2

        if self.is_attacking1:
            attack_right = self.attack_right1
            attack_left = self.attack_left1
        elif self.is_attacking2:
            attack_right = self.attack_right2
            attack_left = self.attack_left2
        else:
            return

        if self.facing_right:
            if self.attack_index >= len(attack_right):
                self.attack_index = 0
                self.is_attacking1 = False
                self.is_attacking2 = False
            else:
                self.animation = attack_right[int(self.attack_index)]
        else:
            if self.attack_index >= len(attack_left):
                self.attack_index = 0
                self.is_attacking1 = False
                self.is_attacking2 = False
            else:
                self.animation = attack_left[int(self.attack_index)]

    def char_animation(self):
        """Menangani animasi karakter berdasarkan input pemain"""
        keys = pygame.key.get_pressed()
        moving = False

        # Jika sedang menyerang, tangani animasi khusus menyerang
        if self.is_attacking1 or self.is_attacking2:
            self.attack()
            return

        # Deteksi konflik input
        left_right_conflict = keys[pygame.K_a] and keys[pygame.K_d]
        up_down_conflict = keys[pygame.K_w] and keys[pygame.K_s]
        self.char_index += 0.1
        
        # Animasi pemain tanpa mengubah posisi (pergerakan ditangani oleh Game class)
        if not left_right_conflict:
            if keys[pygame.K_d]:
                if keys[pygame.K_p]:
                    self.framing(self.run_right)
                else:
                    self.framing(self.walk_right)
                self.facing_right = True
                moving = True

            if keys[pygame.K_a]:
                if keys[pygame.K_p]:
                    self.framing(self.run_left)
                else:
                    self.framing(self.walk_left)
                self.facing_right = False
                moving = True

        if not up_down_conflict:
            if keys[pygame.K_w]:
                if not moving:  # Hanya update animasi jika belum ada animasi horizontal
                    if self.facing_right:
                        if keys[pygame.K_p]:
                            self.framing(self.run_right)
                        else:
                            self.framing(self.walk_right)
                    else:
                        if keys[pygame.K_p]:
                            self.framing(self.run_left)
                        else:
                            self.framing(self.walk_left)
                    moving = True

            if keys[pygame.K_s]:
                if not moving:  # Hanya update animasi jika belum ada animasi horizontal
                    if self.facing_right:
                        if keys[pygame.K_p]:
                            self.framing(self.run_right)
                        else:
                            self.framing(self.walk_right)
                    else:
                        if keys[pygame.K_p]:
                            self.framing(self.run_left)
                        else:
                            self.framing(self.walk_left)
                    moving = True

        # Animasi idle jika tidak bergerak
        if not moving:
            self.idle_index += 0.1
            if self.facing_right:
                self.framing(self.idle_right)
            else:
                self.framing(self.idle_left)

    def update(self):
        """Update fungsi utama yang dipanggil setiap frame"""
        self.char_animation()
