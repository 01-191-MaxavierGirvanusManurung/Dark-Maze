import pygame, sys
from settings import *
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Dark Maze')
        self.clock = pygame.time.Clock()

        self.player = Player()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j and not self.player.is_attacking2 and not self.player.is_attacking1:
                        self.player.is_attacking2 = True
                        self.player.attack_index = 0
                    elif event.key == pygame.K_k and not self.player.is_attacking1 and not self.player.is_attacking2:
                        self.player.is_attacking1 = True
                        self.player.attack_index = 0
                
            self.screen.fill((94, 129, 162))
            self.player.update()
            self.screen.blit(self.player.animation, self.player.rect)
            pygame.display.update()
            self.clock.tick(fps)

if __name__ == '__main__':
    game = Game()
    game.run()
