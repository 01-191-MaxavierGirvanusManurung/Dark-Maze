import pygame, sys

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
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
        
        self.is_attacking1 = False
        self.is_attacking2 = False
        self.attack_index = 0
        self.idle_index = 0
        self.char_index = 0
        self.facing_right = True 
        self.animation = self.walk_right[self.char_index]
        self.rect = self.animation.get_rect(midbottom=(80, 300))

    def framing(self, frame):
        self.frame = frame
        if self.char_index >= len(self.frame): self.char_index = 0
        self.animation = self.frame[int(self.char_index)]

    def attack(self):
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
        keys = pygame.key.get_pressed()
        moving = False

        if self.is_attacking1 or self.is_attacking2:
            self.attack()
            return

        left_right_conflict = keys[pygame.K_a] and keys[pygame.K_d]
        up_down_conflict = keys[pygame.K_w] and keys[pygame.K_s]
        self.char_index += 0.1

        if not left_right_conflict:
            if keys[pygame.K_d]:
                self.framing(self.walk_right)
                self.rect.x += 2
                self.facing_right = True
                moving = True
                if keys[pygame.K_p]:
                    self.rect.x += 5
                    self.framing(self.run_right)

            if keys[pygame.K_a]:
                self.framing(self.walk_left)
                self.rect.x -= 2
                self.facing_right = False
                moving = True
                if keys[pygame.K_p]:
                    self.rect.x -= 5
                    self.framing(self.run_left)

        if not up_down_conflict:
            if keys[pygame.K_w]:
                if self.facing_right:
                    self.framing(self.walk_right)
                if not self.facing_right:
                    self.framing(self.walk_left)
                self.rect.y -= 2
                moving = True
                if keys[pygame.K_p]:
                    self.rect.y -= 5
                    if self.facing_right:
                        self.framing(self.run_right)
                    else:
                        self.framing(self.run_left)

            if keys[pygame.K_s]:
                if self.facing_right:
                    self.framing(self.walk_right)
                if not self.facing_right:
                    self.framing(self.walk_left)
                self.rect.y += 2
                moving = True
                if keys[pygame.K_p]:
                    self.rect.y += 5
                    if self.facing_right:
                        self.framing(self.run_right)
                    else:
                        self.framing(self.run_left)

        if not moving:
            self.idle_index += 0.1
            if keys[pygame.K_d]:self.facing_right = True
            elif keys[pygame.K_a]: self.facing_right = False
            if self.facing_right:
                self.framing(self.idle_right)
            else:
                self.framing(self.idle_left)

        if self.rect.x <= -50 : self.rect.x = -50
        if self.rect.x >= 1200 : self.rect.x = 1200
        if self.rect.y >= 590 : self.rect.y = 590
        if self.rect.y <= -60 : self.rect.y = -60

    def update(self):
        self.char_animation()

# pygame.init()
# screen = pygame.display.set_mode((1280, 720))
# clock = pygame.time.Clock()

# player = Player()

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_k and not player.is_attacking2 and not player.is_attacking1:
        #         player.is_attacking2 = True
        #         player.attack_index = 0
        #     elif event.key == pygame.K_j and not player.is_attacking1 and not player.is_attacking2:
        #         player.is_attacking1 = True
        #         player.attack_index = 0

    # screen.fill((94, 129, 162))

    # player.update()
    # screen.blit(player.animation, player.rect)

    # pygame.display.update()
    # clock.tick(60)
