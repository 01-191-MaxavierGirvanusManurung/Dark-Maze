import pygame
import settings as app_settings # Impor modul settings untuk akses dinamis ke global_volume

pygame.mixer.init() # Inisialisasi mixer sekali di sini atau di awal game

def play_music(track_path="assets/Ground.MP3"): # Jadikan path trek sebagai argumen opsional
    try:
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.set_volume(app_settings.global_volume) # Gunakan nilai terkini
        pygame.mixer.music.play(-1) # Loop tak terbatas
    except pygame.error as e:
        print(f"Error playing music {track_path}: {e}")


def stop_music():
    pygame.mixer.music.stop()

def set_music_volume(volume): # Fungsi helper untuk mengatur volume musik
    app_settings.global_volume = max(0.0, min(1.0, volume)) # Clamp volume 0-1
    pygame.mixer.music.set_volume(app_settings.global_volume)
