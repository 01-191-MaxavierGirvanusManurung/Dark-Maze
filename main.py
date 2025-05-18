import pygame, sys
from settings import *
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Dark Maze')
        self.clock = pygame.time.Clock()

        # Cari posisi spawn player
        spawn_x, spawn_y = 0, 0
        for y, row in enumerate(collision_map):
            for x, tile in enumerate(row):
                if tile == 'p':
                    spawn_x = x * TILE_SIZE
                    spawn_y = y * TILE_SIZE
                    break

        self.player = Player()
        self.player.rect.midbottom = (spawn_x + TILE_SIZE // 2, spawn_y + TILE_SIZE)
        self.camera_offset = pygame.Vector2(0, 0)

    def get_wall_rects(self):
        walls = []
        for y in range(len(collision_map)):
            for x in range(len(collision_map[0])):
                if collision_map[y][x] == 80:
                    wall = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    walls.append(wall)
        return walls

    def handle_movement(self):
        keys = pygame.key.get_pressed()
        
        # Simpan posisi original untuk digunakan dalam collision check
        original_x = self.player.rect.x
        original_y = self.player.rect.y
        
        # Menangani input dan memperbarui posisi
        if not self.player.is_attacking1 and not self.player.is_attacking2:
            speed = 50 if keys[pygame.K_p] else 10  # Speed boost dengan tombol P
            
            # X movement
            if keys[pygame.K_d] and not keys[pygame.K_a]:
                self.player.rect.x += speed
                self.player.facing_right = True
            elif keys[pygame.K_a] and not keys[pygame.K_d]:
                self.player.rect.x -= speed
                self.player.facing_right = False
                
            # Check X collision
            for wall in self.get_wall_rects():
                if self.player.rect.colliderect(wall):
                    if keys[pygame.K_d]:
                        self.player.rect.right = wall.left
                    elif keys[pygame.K_a]:
                        self.player.rect.left = wall.right
            
            # Y movement
            if keys[pygame.K_w] and not keys[pygame.K_s]:
                self.player.rect.y -= speed
            elif keys[pygame.K_s] and not keys[pygame.K_w]:
                self.player.rect.y += speed
                
            # Check Y collision
            for wall in self.get_wall_rects():
                if self.player.rect.colliderect(wall):
                    if keys[pygame.K_s]:
                        self.player.rect.bottom = wall.top
                    elif keys[pygame.K_w]:
                        self.player.rect.top = wall.bottom

    def run(self):
        while True:
            dt = self.clock.tick(fps) / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j and not self.player.is_attacking2 and not self.player.is_attacking1:
                        self.player.is_attacking1 = True
                        self.player.attack_index = 0
                    elif event.key == pygame.K_k and not self.player.is_attacking1 and not self.player.is_attacking2:
                        self.player.is_attacking2 = True
                        self.player.attack_index = 0

            # Menangani pergerakan dan collision
            self.handle_movement()
            
            # Update camera to follow player (centered)
            self.camera_offset.x = self.player.rect.centerx - width // 2
            self.camera_offset.y = self.player.rect.centery - height // 2

            # DRAW
            self.screen.fill((94, 129, 162))  # background

            # Draw walls with camera offset
            for wall in self.get_wall_rects():
                offset_wall = wall.move(-int(self.camera_offset.x), -int(self.camera_offset.y))
                pygame.draw.rect(self.screen, 'black', offset_wall)

            # Update & Draw player with camera offset
            self.player.update()
            player_draw_pos = self.player.rect.move(-int(self.camera_offset.x), -int(self.camera_offset.y))
            self.screen.blit(self.player.animation, player_draw_pos)
            # self.screen.blit(self.player.animation, 'green')
            pygame.display.update()
            

if __name__ == '__main__':
    game = Game()
    game.run()
