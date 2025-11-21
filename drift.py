import pygame
import math

# --- KONFIGURACJA ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Kolory
COLOR_BG = (30, 30, 35)        # Ciemny asfalt
COLOR_CAR = (230, 50, 50)      # Czerwone auto
COLOR_WINDOW = (50, 200, 255)  # Szyba
COLOR_TRAIL = (50, 50, 50)     # Ślady opon

# Fizyka samochodu
MAX_SPEED = 10
ACCELERATION = 0.2
ROTATION_SPEED = 4
FRICTION = 0.98   # Opór powietrza/tarcie (im mniej, tym bardziej ślisko)
DRIFT_FACTOR = 0.9 # Jak bardzo auto trzyma się drogi (1.0 = brak driftu, 0.5 = lód)

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # 1. Tworzenie grafiki samochodu "w kodzie" (zamiast ładować obrazek)
        self.original_image = pygame.Surface((60, 30), pygame.SRCALPHA)
        # Nadwozie
        pygame.draw.rect(self.original_image, COLOR_CAR, (0, 0, 60, 30), border_radius=5)
        # Szyba (żeby wiedzieć gdzie przód - prawa strona)
        pygame.draw.rect(self.original_image, COLOR_WINDOW, (40, 2, 15, 26), border_radius=3)
        # Światła
        pygame.draw.rect(self.original_image, (255, 255, 200), (55, 2, 5, 8))
        pygame.draw.rect(self.original_image, (255, 255, 200), (55, 20, 5, 8))

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # 2. Fizyka - Wektory
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0  # 0 stopni to kierunek w prawo

    def get_input(self):
        keys = pygame.key.get_pressed()
        
        # Skręcanie (tylko gdy auto się porusza)
        if self.velocity.length() > 0.5: 
            # Odwracamy sterowanie na wstecznym dla realizmu
            direction = 1 if self.velocity.dot(self.direction_vector()) > 0 else -1
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle += ROTATION_SPEED * direction
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle -= ROTATION_SPEED * direction

        # Przyspieszanie / Hamowanie
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            # Dodajemy siłę w kierunku, w który PATRZY auto
            acceleration = self.direction_vector() * ACCELERATION
            self.velocity += acceleration
        
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            # Hamowanie / Wsteczny
            acceleration = self.direction_vector() * ACCELERATION
            self.velocity -= acceleration

    def direction_vector(self):
        # Zamiana kąta na wektor kierunkowy (matematyka trygonometrii)
        # Kąt w radianach, odwrócony Y bo w Pygame Y rośnie w dół
        rad = math.radians(self.angle)
        return pygame.math.Vector2(math.cos(rad), -math.sin(rad))

    def physics(self):
        # Aplikowanie tarcia (zwalnianie)
        self.velocity *= FRICTION

        # Ograniczenie prędkości maksymalnej
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)

        # --- LOGIKA DRIFTU ---
        # Jeśli nic nie zrobimy, auto będzie ślizgać się jak w "Asteroids".
        # Musimy trochę "nagiąć" wektor prędkości w stronę, w którą patrzy auto.
        # im wyższy DRIFT_FACTOR, tym szybciej auto odzyskuje przyczepność.
        
        current_speed = self.velocity.length()
        if current_speed > 0:
            # Wektor kierunku, w który patrzymy
            heading = self.direction_vector()
            # Interpolacja sferyczna (slerp) lub proste mieszanie wektorów
            # Tutaj uproszczone: bierzemy obecny wektor ruchu i "ciągniemy" go w stronę maski auta
            
            # Obliczamy nowy wektor, który jest mieszanką starego ruchu i kierunku kół
            # Musimy zachować prędkość (magnitude), zmieniając tylko kierunek
            move_angle = self.velocity.normalize()
            new_move_angle = move_angle.lerp(heading, 0.05 * current_speed) # Magiczna liczba 0.05 to "grip" opon
            
            self.velocity = new_move_angle * current_speed

        # Aktualizacja pozycji
        self.position += self.velocity
        self.rect.center = self.position

    def update(self):
        self.get_input()
        self.physics()
        self.rotate()

    def rotate(self):
        # Obracanie grafiki
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        # Ważne: przy obrocie zmienia się rozmiar prostokąta (rect), trzeba go wycentrować ponownie
        self.rect = self.image.get_rect(center=self.rect.center)

# --- KLASA ŚLADÓW OPON (Dla efektu wizualnego) ---
class Trail(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill(COLOR_TRAIL)
        self.image.set_alpha(100) # Półprzezroczystość
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=pos)
        self.timer = 100 # Czas życia śladu

    def update(self):
        self.timer -= 2
        self.image.set_alpha(self.timer)
        if self.timer <= 0:
            self.kill()

# --- GŁÓWNA PĘTLA ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Drift King - Pygame Prototype")
clock = pygame.time.Clock()

# Grupy sprite'ów
all_sprites = pygame.sprite.Group()
trails = pygame.sprite.Group()

player = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

running = True
while running:
    # 1. Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Logika gry
    # Dodawanie śladów opon jeśli auto dryfuje (kąt ruchu różni się od kąta patrzenia)
    if player.velocity.length() > 3:
        # Sprawdzamy różnicę między kierunkiem ruchu a kierunkiem patrzenia
        move_vec = player.velocity.normalize()
        look_vec = player.direction_vector()
        # Jeśli iloczyn skalarny jest mały, znaczy że lecimy bokiem -> rysuj ślady
        drift_intensity = abs(move_vec.dot(look_vec))
        if drift_intensity < 0.95: # Próg poślizgu
             trail = Trail(player.rect.center, player.angle)
             trails.add(trail)
             all_sprites.add(trail)

    all_sprites.update()

    # Zapętlenie ekranu (jak wyjedziesz z prawej, wracasz z lewej)
    if player.position.x > SCREEN_WIDTH: player.position.x = 0
    if player.position.x < 0: player.position.x = SCREEN_WIDTH
    if player.position.y > SCREEN_HEIGHT: player.position.y = 0
    if player.position.y < 0: player.position.y = SCREEN_HEIGHT

    # 3. Rysowanie
    screen.fill(COLOR_BG)
    
    # Rysujemy ślady opon pod spodem
    trails.draw(screen)
    # Rysujemy auto
    screen.blit(player.image, player.rect)
    
    # Debug (opcjonalne): Wyświetlanie prędkości
    # font = pygame.font.SysFont(None, 24)
    # img = font.render(f"Speed: {int(player.velocity.length()*10)}", True, (255, 255, 255))
    # screen.blit(img, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()