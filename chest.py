import pygame
import random
from settings import DEFAULT_ANIMATION_SPEED
import settings as app_settings

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Path untuk sprite peti (sesuai permintaan Anda)
        # dan path 'assets/' untuk item-item

        def load_and_scale(path, scale=2.0):
            try:
                image = pygame.image.load(path).convert_alpha()
                size = (int(image.get_width() * scale), int(image.get_height() * scale))
                return pygame.transform.scale(image, size)
            except pygame.error as e:
                print(f"Error loading image: {path} - {e}")
                placeholder = pygame.Surface((int(32*scale), int(32*scale)), pygame.SRCALPHA)
                placeholder.fill((255,0,0,128))
                return placeholder


        self.frames = [
            load_and_scale("peti/peti 1.png", scale=2.0),
            load_and_scale("peti/peti 2.png", scale=2.0),
            load_and_scale("peti/peti 3.png", scale=2.0),
            load_and_scale("peti/peti 4.png", scale=2.0),
            load_and_scale("peti/peti 5.png", scale=2.0),
            load_and_scale("peti/peti 6.png", scale=2.0),
            load_and_scale("peti/peti 7.png", scale=2.0),
            load_and_scale("peti/peti 8.png", scale=2.0),
            load_and_scale("peti/peti 9.png", scale=2.0),
            load_and_scale("peti/peti 10.png", scale=2.0)
        ]
        self.index = 0
        self.image = self.frames[self.index] if self.frames and self.frames[self.index] else pygame.Surface((1,1))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.opening = False
        self.finished = False
        self.reward_given = False
        self.reward = None
        self.reward_type = None
        self.reward_rect = None

        self.animation_speed = DEFAULT_ANIMATION_SPEED

        try:
            # Suara open treasure dari folder assets umum
            self.open_sound = pygame.mixer.Sound(f"asset item/open treasure.mp3")
        except pygame.error as e:
            print(f"Error loading sound: asset item/open treasure.mp3 - {e}")
            self.open_sound = None


    def update(self, player, dt):
        if self.opening and not self.finished:
            self.index += self.animation_speed * dt
            if int(self.index) < len(self.frames):
                if self.frames[int(self.index)]: # Pastikan frame ada
                     self.image = self.frames[int(self.index)]
            else:
                self.finished = True
                self.drop_reward()
        
        if self.finished and not self.reward and not self.opening: # Jika sudah selesai, reward diambil, dan tidak sedang animasi buka lagi
            self.kill()


    def open(self):
        if not self.opening and not self.finished:
            self.opening = True
            self.index = 0 # Mulai animasi dari awal
            if self.open_sound:
                self.open_sound.set_volume(app_settings.global_volume)
                self.open_sound.play()

    def drop_reward(self):
        if self.reward_given:
            return
        self.reward_given = True

        # Path item dari asset item ('assets/')
        key_images_paths = [
            f"asset item/key 1.png",
            f"asset item/key 2.png",
            f"asset item/key 4.png"
        ]
        potion_red_path = f"asset item/potion 1.png"
        potion_blue_path = f"asset item/potion 2.png"

        key_images = []
        for path in key_images_paths:
            try:
                key_images.append(pygame.image.load(path).convert_alpha())
            except pygame.error as e:
                print(f"Error loading key image: {path} - {e}")
        
        try:
            potion_red_img = pygame.image.load(potion_red_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading red potion: {potion_red_path} - {e}")
            potion_red_img = None

        try:
            potion_blue_img = pygame.image.load(potion_blue_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading blue potion: {potion_blue_path} - {e}")
            potion_blue_img = None

        drop = random.random()

        if drop < 0.2 and key_images:
            chosen_key_img = random.choice(key_images)
            self.reward = pygame.transform.scale(chosen_key_img, (32, 32))
            self.reward_type = "key"
            print("🔑 Kamu mendapatkan kunci!")
        elif drop < 0.6 and potion_red_img:
            self.reward = pygame.transform.scale(potion_red_img, (32, 32))
            self.reward_type = "red_potion"
            print("❤️ Kamu mendapatkan Potion Merah (+HP)")
        elif potion_blue_img:
            self.reward = pygame.transform.scale(potion_blue_img, (32, 32))
            self.reward_type = "blue_potion"
            print("💡 Kamu mendapatkan Potion Biru (+Cahaya)")
        else:
            print("Tidak ada reward yang dijatuhkan.")
            self.reward = None
            self.reward_type = None
            return

        if self.reward:
            # Posisikan reward di atas chest yang terbuka
            self.reward_rect = self.reward.get_rect(centerx=self.rect.centerx, bottom=self.rect.top + 50)


def generate_random_chests(collision_map_data, tile_size, chest_probability=0.03):
    chests = pygame.sprite.Group()
    for y, row in enumerate(collision_map_data):
        for x, tile in enumerate(row):
            if tile == 0 and random.random() < chest_probability:
                chest = Chest(x * tile_size, y * tile_size)
                chests.add(chest)
    return chests
