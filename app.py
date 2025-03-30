import pygame
import sys
import random
from flask import Flask, render_template, request, send_file  # new import for web version
import io  # new import for in-memory file handling
from PIL import Image  # new import to convert Pygame surface to image

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
SPRITE_SIZE = 32  # 16x16 or 32x32 for better visibility
FPS = 60
PALETTE = [
    (0, 0, 0),         # Black
    (255, 0, 0),       # Red
    (0, 255, 0),       # Green
    (0, 0, 255),       # Blue
    (255, 255, 0),     # Yellow
    (255, 0, 255),     # Magenta
    (0, 255, 255),     # Cyan
    (192, 192, 192),   # Light Gray
    (128, 128, 128),   # Gray
    (255, 165, 0),     # Orange
    (139, 0, 139),     # Purple
    (0, 255, 255),     # Aqua
    (255, 255, 255),   # White
    (128, 0, 0),       # Dark Red
    (0, 128, 0),       # Dark Green
    (0, 0, 128)        # Dark Blue
]

BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (50, 50, 50)
TEXT_COLOR = (200, 200, 200)
SELECTED_COLOR = (100, 100, 255)

class UIElement(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.selected = False
        self.image = pygame.Surface((w, h))
        self.update_image()
    
    def update_image(self):
        self.image.fill(SELECTED_COLOR if self.selected else BUTTON_COLOR)
        pygame.draw.rect(self.image, TEXT_COLOR, pygame.Rect(0, 0, self.rect.width, self.rect.height), 2)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, TEXT_COLOR)
        text_width = text.get_width()
        self.image.blit(text, ((self.rect.width - text_width) // 2, 5))

class Button(UIElement):
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.selected = not self.selected
                self.update_image()

class Dropdown(UIElement):
    def __init__(self, x, y, w, h, options):
        super().__init__(x, y, w, h, options[0])
        self.options = options
        self.open = False
        self.selected_index = 0
        self.option_rects = []
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
            elif self.open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.text = self.options[self.selected_index]
                        self.open = False
                        self.update_image()
                        break
                self.open = False
        elif event.type == pygame.MOUSEMOTION and self.open:
            for i, option_rect in enumerate(self.option_rects):
                if option_rect.collidepoint(event.pos):
                    pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
        if self.open:
            self.option_rects = []
            total_height = len(self.options) * 40
            menu_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, 
                                   self.rect.width, total_height)
            pygame.draw.rect(screen, (40, 40, 60), menu_rect)
            pygame.draw.rect(screen, (150, 150, 180), menu_rect, 2)
            
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + (i*40), 
                                  self.rect.width, 40)
                self.option_rects.append(rect)
                
                if i == self.selected_index:
                    pygame.draw.rect(screen, (80, 80, 150), rect)
                
                pygame.draw.rect(screen, (200, 200, 220), rect, 1)
                
                font = pygame.font.Font(None, 32)
                text = font.render(option, True, (240, 240, 240))
                screen.blit(text, (rect.x + 10, rect.y + 8))

class Label:
    def __init__(self, text, x, y, color=(255, 255, 255), font_size=28):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.surface = self.font.render(text, True, color)
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame_index = 0
        self.animation_frames = [image]
        self.animation_speed = 5
        self.animation_timer = 0
    
    def add_animation_frame(self, image):
        self.animation_frames.append(image)
    
    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= FPS // self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.frame_index]

def generate_sprite(class_type, animation, frame=0, skin_color=None, hair_color=None, outfit_color=None):
    img = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA, 32)
    img.fill((0, 0, 0, 0))
    
    if skin_color is None:
        skin_color = random.choice([(255, 213, 170), (240, 188, 150), (204, 145, 105), (160, 120, 90)])
    if hair_color is None:
        hair_color = random.choice([(50, 25, 0), (70, 50, 0), (255, 215, 0), (150, 75, 0)])
    if outfit_color is None:
        if class_type == 'warrior':
            outfit_color = random.choice([(139, 0, 0), (165, 42, 42), (128, 128, 128)])
        elif class_type == 'archer':
            outfit_color = random.choice([(0, 100, 0), (34, 139, 34), (47, 79, 79)])
        else:
            outfit_color = random.choice([(75, 0, 130), (72, 61, 139), (25, 25, 112)])
    
    y_offset = 0
    if animation == 'idle':
        y_offset = 0 if frame % 2 == 0 else 1
    
    pygame.draw.circle(img, skin_color, (SPRITE_SIZE//2, SPRITE_SIZE//4 - y_offset), 5)
    
    if animation == 'idle' and frame == 1:
        pygame.draw.line(img, (0, 0, 0), (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 - 1 - y_offset), 
                      (SPRITE_SIZE//2 - 1, SPRITE_SIZE//4 - 1 - y_offset), 1)
        pygame.draw.line(img, (0, 0, 0), (SPRITE_SIZE//2 + 1, SPRITE_SIZE//4 - 1 - y_offset), 
                      (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 - 1 - y_offset), 1)
    else:
        pygame.draw.rect(img, (0, 0, 0), (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 - 1 - y_offset, 2, 1))
        pygame.draw.rect(img, (0, 0, 0), (SPRITE_SIZE//2 + 1, SPRITE_SIZE//4 - 1 - y_offset, 2, 1))
    
    if class_type == 'warrior':
        # Enhanced warrior helmet with better placement and cooler design
        # Helmet base - positioned higher
        pygame.draw.rect(img, (100, 100, 120), (SPRITE_SIZE//2 - 4, SPRITE_SIZE//4 - 6 - y_offset, 8, 6))
        
        # Helmet crest - larger and more prominent
        pygame.draw.rect(img, (220, 50, 50), (SPRITE_SIZE//2 - 1, SPRITE_SIZE//4 - 9 - y_offset, 2, 6))
        
        # Helmet detail - improved side guards
        pygame.draw.line(img, (80, 80, 100), (SPRITE_SIZE//2 - 4, SPRITE_SIZE//4 - 4 - y_offset),
                        (SPRITE_SIZE//2 - 5, SPRITE_SIZE//4 - y_offset), 2)
        pygame.draw.line(img, (80, 80, 100), (SPRITE_SIZE//2 + 4, SPRITE_SIZE//4 - 4 - y_offset),
                        (SPRITE_SIZE//2 + 5, SPRITE_SIZE//4 - y_offset), 2)
        
        # Helmet visor/face guard
        pygame.draw.line(img, (160, 160, 180), (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 - 3 - y_offset), 
                        (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 - 3 - y_offset), 1)
        
        # Helmet brim
        pygame.draw.line(img, (140, 140, 160), (SPRITE_SIZE//2 - 4, SPRITE_SIZE//4 - 1 - y_offset), 
                        (SPRITE_SIZE//2 + 4, SPRITE_SIZE//4 - 1 - y_offset), 1)
    elif class_type == 'archer':
        # Hood base
        pygame.draw.arc(img, outfit_color, (SPRITE_SIZE//2 - 5, SPRITE_SIZE//4 - 10 - y_offset, 10, 8), 
                       3.14, 6.28, 2)
        
        # Add a feather to the hood
        feather_color = (240, 240, 240)  # White feather
        feather_x_positions = [0, 1, 0, -1]  # Slight movement for animation
        feather_x = feather_x_positions[frame % 4]
        
        pygame.draw.line(img, feather_color,
                        (SPRITE_SIZE//2 - 3 + feather_x, SPRITE_SIZE//4 - 9 - y_offset),
                        (SPRITE_SIZE//2 - 6 + feather_x, SPRITE_SIZE//4 - 12 - y_offset), 1)
        pygame.draw.line(img, feather_color,
                        (SPRITE_SIZE//2 - 5 + feather_x, SPRITE_SIZE//4 - 11 - y_offset),
                        (SPRITE_SIZE//2 - 3 + feather_x, SPRITE_SIZE//4 - 13 - y_offset), 1)
    else:
        pygame.draw.polygon(img, outfit_color, [
            (SPRITE_SIZE//2 - 5, SPRITE_SIZE//4 - 1 - y_offset),
            (SPRITE_SIZE//2 + 5, SPRITE_SIZE//4 - 1 - y_offset),
            (SPRITE_SIZE//2, SPRITE_SIZE//4 - 8 - y_offset)
        ])
    
    body_offset = 0
    if animation == 'walking':
        body_offset = frame % 2
    elif animation == 'idle':
        body_offset = y_offset
    
    pygame.draw.rect(img, outfit_color, 
                   (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 5 - body_offset, 
                    6, 8))
    
    if animation == 'idle':
        pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 4, SPRITE_SIZE//4 + 6 - body_offset), 
                        (SPRITE_SIZE//2 - 6, SPRITE_SIZE//4 + 12 - body_offset), 2)
        pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 4, SPRITE_SIZE//4 + 6 - body_offset), 
                        (SPRITE_SIZE//2 + 6, SPRITE_SIZE//4 + 12 - body_offset), 2)
    elif animation == 'walking':
        if frame % 2 == 0:
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 - 6, SPRITE_SIZE//4 + 11 - body_offset), 2)
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 + 5, SPRITE_SIZE//4 + 10 - body_offset), 2)
        else:
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 - 5, SPRITE_SIZE//4 + 10 - body_offset), 2)
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 + 6, SPRITE_SIZE//4 + 11 - body_offset), 2)
    elif animation == 'attacking':
        if class_type == 'warrior':
            # More dynamic warrior attacking animation
            # Attack phases: 0=wind up, 1=swing, 2=follow through, 3=return
            
            # Body slightly leans into attack
            lean_shift = [0, 1, 1, 0][frame]
            
            # Draw the left arm - position varies based on swing
            left_arm_positions = [(6, 10), (5, 8), (6, 7), (6, 9)]
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 - left_arm_positions[frame][0], SPRITE_SIZE//4 + left_arm_positions[frame][1] - body_offset), 2)
            
            # Draw the right arm wielding sword - follows through swing
            arm_extends = [0, 2, 3, 1][frame]
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 + 7 + arm_extends, SPRITE_SIZE//4 + 4 - body_offset - lean_shift), 2)
            
            # Sword angles for dynamic swing - varies by frame
            sword_angles = [(0, 0), (3, -3), (1, 2), (1, -1)]
            dx, dy = sword_angles[frame]
            
            # Sword hilt properly connected to hand
            pygame.draw.line(img, (150, 100, 50),  # hilt
                             (SPRITE_SIZE//2 + 7 + arm_extends, SPRITE_SIZE//4 + 4 - body_offset - lean_shift),
                             (SPRITE_SIZE//2 + 9 + arm_extends, SPRITE_SIZE//4 + 4 - body_offset - lean_shift), 2)
            
            # Sword blade with swing effect
            if frame == 1:  # During the main swing
                # Add motion blur/trail to the sword
                for i in range(1, 4):
                    trail_dx = dx * (i/4)
                    trail_dy = dy * (i/4)
                    alpha = 150 - (i * 40)  # Fading trail
                    trail_color = (200, 200, 220, alpha)
                    
                    trail_surf = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
                    pygame.draw.line(trail_surf, trail_color,
                                    (SPRITE_SIZE//2 + 9 + arm_extends - trail_dx, SPRITE_SIZE//4 + 4 - body_offset - lean_shift - trail_dy),
                                    (SPRITE_SIZE//2 + 17 + arm_extends - trail_dx*2, SPRITE_SIZE//4 + dy - trail_dy*2), 2)
                    img.blit(trail_surf, (0, 0))
            
            # Main sword blade
            pygame.draw.line(img, (200, 200, 220),
                            (SPRITE_SIZE//2 + 9 + arm_extends, SPRITE_SIZE//4 + 4 - body_offset - lean_shift),
                            (SPRITE_SIZE//2 + 17 + arm_extends + dx, SPRITE_SIZE//4 + dy - lean_shift), 3)
            
            # Hand grip on hilt
            pygame.draw.circle(img, skin_color, (SPRITE_SIZE//2 + 7 + arm_extends, SPRITE_SIZE//4 + 4 - body_offset - lean_shift), 2)
            
            # Add impact effect in frame 2 (after swing)
            if frame == 2:
                impact_surf = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
                impact_color = (255, 255, 220, 180)
                pygame.draw.line(impact_surf, impact_color,
                                (SPRITE_SIZE//2 + 18 + arm_extends + dx - 2, SPRITE_SIZE//4 + dy - lean_shift - 2),
                                (SPRITE_SIZE//2 + 22 + arm_extends + dx, SPRITE_SIZE//4 + dy - lean_shift + 2), 2)
                pygame.draw.line(impact_surf, impact_color,
                                (SPRITE_SIZE//2 + 18 + arm_extends + dx, SPRITE_SIZE//4 + dy - lean_shift + 2),
                                (SPRITE_SIZE//2 + 22 + arm_extends + dx - 2, SPRITE_SIZE//4 + dy - lean_shift - 2), 2)
                img.blit(impact_surf, (0, 0))
        elif class_type == 'archer':
            # Draw left arm pulling bow string
            string_pull = [1, 3, 2, 1][frame]  # How far back the string is pulled
            
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 - 6, SPRITE_SIZE//4 + 8 - body_offset), 2)
            
            # Draw right arm holding bow
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 + 7, SPRITE_SIZE//4 + 4 - body_offset), 2)
            
            # Draw bow
            bow_curve = 3 + string_pull  # Bow flexes more as string is pulled
            pygame.draw.arc(img, (139, 69, 19),  # Brown bow
                          (SPRITE_SIZE//2 + 7, SPRITE_SIZE//4 - 4 - body_offset, 4, 16),
                          -0.5, 0.5, 2)
            
            # Bowstring
            pygame.draw.line(img, (220, 220, 220),  # Light gray string
                           (SPRITE_SIZE//2 + 9, SPRITE_SIZE//4 - 4 - body_offset),  # Top of bow
                           (SPRITE_SIZE//2 + 9 - string_pull, SPRITE_SIZE//4 + 4 - body_offset),  # Middle (pulled)
                           1)
            pygame.draw.line(img, (220, 220, 220),  # Light gray string
                           (SPRITE_SIZE//2 + 9 - string_pull, SPRITE_SIZE//4 + 4 - body_offset),  # Middle
                           (SPRITE_SIZE//2 + 9, SPRITE_SIZE//4 + 12 - body_offset),  # Bottom of bow
                           1)
            
            # Arrow
            if frame > 0:  # Only show arrow when drawing bow
                arrow_positions = [0, 0, 2, 4]  # Arrow flight distance after release
                arrow_x = arrow_positions[frame]
                
                pygame.draw.line(img, (150, 75, 0),  # Arrow shaft
                              (SPRITE_SIZE//2 + 9 - string_pull, SPRITE_SIZE//4 + 4 - body_offset),
                              (SPRITE_SIZE//2 + 13 + arrow_x, SPRITE_SIZE//4 + 4 - body_offset), 1)
                
                # Arrow head
                if frame < 3:  # Arrow still visible in frame
                    pygame.draw.polygon(img, (200, 200, 220), [
                        (SPRITE_SIZE//2 + 13 + arrow_x, SPRITE_SIZE//4 + 3 - body_offset),
                        (SPRITE_SIZE//2 + 15 + arrow_x, SPRITE_SIZE//4 + 4 - body_offset),
                        (SPRITE_SIZE//2 + 13 + arrow_x, SPRITE_SIZE//4 + 5 - body_offset)
                    ])
        elif class_type == 'mage':
            # Draw left arm
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 - 6, SPRITE_SIZE//4 + 10 - body_offset), 2)
            
            # Draw right arm casting spell, moving based on frame
            arm_extend = [0, 2, 4, 2][frame]  # Arm extends forward during cast
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset), 
                            (SPRITE_SIZE//2 + 7 + arm_extend, SPRITE_SIZE//4 + 4 - body_offset), 2)
            
            # Magic staff/wand
            if frame <= 1:  # Staff raising
                pygame.draw.line(img, (150, 100, 50),
                                (SPRITE_SIZE//2 + 7 + arm_extend, SPRITE_SIZE//4 + 4 - body_offset),
                                (SPRITE_SIZE//2 + 12, SPRITE_SIZE//4 - 5 - body_offset), 2)
                pygame.draw.circle(img, (100, 180, 255),
                                 (SPRITE_SIZE//2 + 12, SPRITE_SIZE//4 - 6 - body_offset), 3)
            else:  # Staff pointing forward for casting
                pygame.draw.line(img, (150, 100, 50),
                                (SPRITE_SIZE//2 + 7 + arm_extend, SPRITE_SIZE//4 + 4 - body_offset),
                                (SPRITE_SIZE//2 + 14, SPRITE_SIZE//4 + 2 - body_offset), 2)
                pygame.draw.circle(img, (100, 180, 255),
                                 (SPRITE_SIZE//2 + 14, SPRITE_SIZE//4 + 1 - body_offset), 2)
            
            # Fireball getting larger and moving forward
            fireball_positions = [5, 8, 12, 16]
            fireball_x = SPRITE_SIZE//2 + fireball_positions[frame]
            fireball_sizes = [2, 3, 4, 3]
            fireball_y_offsets = [0, -1, 0, 1]  # Makes fireball move slightly up and down
            
            # Glowing effect around fireball
            glow_surf = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
            glow_radius = fireball_sizes[frame] + 1
            glow_color = (255, 160, 30, 100)  # Orange with transparency
            pygame.draw.circle(glow_surf, glow_color,
                              (fireball_x, SPRITE_SIZE//4 + 2 - body_offset + fireball_y_offsets[frame]),
                              glow_radius)
            img.blit(glow_surf, (0, 0))
            
            # Fireball itself
            pygame.draw.circle(img, (255, 100, 0),  # Bright orange
                             (fireball_x, SPRITE_SIZE//4 + 2 - body_offset + fireball_y_offsets[frame]),
                             fireball_sizes[frame])
    elif animation == 'defending':
        if class_type == 'warrior':
            # Right arm with shield (shield animating forward/backward)
            shield_x_positions = [3, 5, 3, 1]  # Shield moves forward/backward, much closer to warrior
            shield_x = shield_x_positions[frame]
            
            # Left arm (bare)
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset),
                             (SPRITE_SIZE//2 - 6, SPRITE_SIZE//4 + 10 - body_offset), 2)
            
            # Right arm holding shield
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset),
                             (SPRITE_SIZE//2 + 6, SPRITE_SIZE//4 + 3 - body_offset), 3)
            
            # Shield on right arm - moved much closer to warrior
            pygame.draw.ellipse(img, (200, 150, 100),
                                (SPRITE_SIZE//2 + shield_x, SPRITE_SIZE//4 + 1 - body_offset, 8, 12))
            pygame.draw.ellipse(img, (150, 100, 50),
                                (SPRITE_SIZE//2 + shield_x, SPRITE_SIZE//4 + 1 - body_offset, 8, 12), 1)
        elif class_type == 'archer':
            # Create a dynamic dodging animation
            dodge_x_shifts = [-2, -4, -2, 0]
            dodge_y_shifts = [-1, -2, -1, 0]
            
            x_shift = dodge_x_shifts[frame]
            y_shift = dodge_y_shifts[frame]
            x_center = SPRITE_SIZE//2 + x_shift

            # Head
            pygame.draw.circle(img, skin_color, (x_center, SPRITE_SIZE//4 - y_offset + y_shift), 5)
            
            # Hood/hat
            pygame.draw.arc(img, outfit_color, (x_center - 5, SPRITE_SIZE//4 - 10 - y_offset + y_shift, 10, 8),
                            3.14, 6.28, 2)
            
            # Body
            pygame.draw.rect(img, outfit_color,
                             (x_center - 3, SPRITE_SIZE//4 + 5 - body_offset + y_shift, 6, 8))
            
            # Arms with different positions per frame
            arm_angles = [(0, 0), (-1, -2), (0, 0), (1, 2)]  # (x, y) offsets for arm ends
            
            # Left arm
            pygame.draw.line(img, skin_color,
                             (x_center - 3, SPRITE_SIZE//4 + 6 - body_offset + y_shift),
                             (x_center - 6 + arm_angles[frame][0], 
                              SPRITE_SIZE//4 + 10 - body_offset + y_shift + arm_angles[frame][1]), 2)
            
            # Right arm
            pygame.draw.line(img, skin_color,
                             (x_center + 3, SPRITE_SIZE//4 + 6 - body_offset + y_shift),
                             (x_center + 6 - arm_angles[frame][0], 
                              SPRITE_SIZE//4 + 10 - body_offset + y_shift + arm_angles[frame][1]), 2)
            
            # Legs with slight variation
            leg_shift = abs(arm_angles[frame][1])
            pygame.draw.line(img, outfit_color, 
                             (x_center - 2, SPRITE_SIZE//4 + 13 - body_offset + y_shift),
                             (x_center - 2 - leg_shift, SPRITE_SIZE//4 + 20 - body_offset + y_shift), 2)
            pygame.draw.line(img, outfit_color, 
                             (x_center + 2, SPRITE_SIZE//4 + 13 - body_offset + y_shift),
                             (x_center + 2 + leg_shift, SPRITE_SIZE//4 + 20 - body_offset + y_shift), 2)
        elif class_type == 'mage':
            # Arms in defensive stance
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 6 - body_offset),
                             (SPRITE_SIZE//2 - 6, SPRITE_SIZE//4 + 10 - body_offset), 2)
            pygame.draw.line(img, skin_color, (SPRITE_SIZE//2 + 3, SPRITE_SIZE//4 + 6 - body_offset),
                             (SPRITE_SIZE//2 + 6, SPRITE_SIZE//4 + 10 - body_offset), 2)
            # Magic shield bubble
            shield_radius = [10, 12, 14, 12]
            shield_colors = [
                (100, 180, 255, 50),
                (120, 190, 255, 60),
                (140, 200, 255, 70),
                (120, 190, 255, 60)
            ]
            shield_surf = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, shield_colors[frame],
                               (SPRITE_SIZE//2, SPRITE_SIZE//4 + 8 - body_offset),
                               shield_radius[frame])
            img.blit(shield_surf, (0, 0))
    elif animation == 'dying':
        # Improved dying animation: add fall offset and rotation
        fall_progress = frame / 3.0
        fall_y_offset = int(10 * fall_progress)
        angle = -int(30 * fall_progress)  # Rotate up to -30 degrees as it falls
        if class_type == 'warrior':
            # Draw head and body falling
            pygame.draw.circle(img, skin_color, (SPRITE_SIZE//2, SPRITE_SIZE//4 + fall_y_offset), 5)
            pygame.draw.rect(img, outfit_color, (SPRITE_SIZE//2 - 3, SPRITE_SIZE//4 + 5 + fall_y_offset, 6, 8))
        elif class_type == 'archer':
            pygame.draw.circle(img, skin_color, (SPRITE_SIZE//2, SPRITE_SIZE//4 + fall_y_offset), 5)
            pygame.draw.arc(img, outfit_color, (SPRITE_SIZE//2 - 5, SPRITE_SIZE//4 - 10 + fall_y_offset, 10, 8), 3.14, 6.28, 2)
        else:
            pygame.draw.circle(img, skin_color, (SPRITE_SIZE//2, SPRITE_SIZE//4 + fall_y_offset), 5)
            pygame.draw.polygon(img, outfit_color, [
                (SPRITE_SIZE//2 - 5, SPRITE_SIZE//4 + fall_y_offset),
                (SPRITE_SIZE//2 + 5, SPRITE_SIZE//4 + fall_y_offset),
                (SPRITE_SIZE//2, SPRITE_SIZE//4 - 8 + fall_y_offset)
            ])
        # Rotate the entire sprite to simulate collapse
        img = pygame.transform.rotate(img, angle)
    
    # Ensure legs are drawn
    if animation == 'walking':
        if frame % 2 == 0:
            pygame.draw.line(img, outfit_color,
                             (SPRITE_SIZE//2 - 2, SPRITE_SIZE//4 + 13 - body_offset),
                             (SPRITE_SIZE//2 - 4, SPRITE_SIZE//4 + 20 - body_offset), 2)
            pygame.draw.line(img, outfit_color,
                             (SPRITE_SIZE//2 + 2, SPRITE_SIZE//4 + 13 - body_offset),
                             (SPRITE_SIZE//2 + 1, SPRITE_SIZE//4 + 20 - body_offset), 2)
        else:
            pygame.draw.line(img, outfit_color,
                             (SPRITE_SIZE//2 - 2, SPRITE_SIZE//4 + 13 - body_offset),
                             (SPRITE_SIZE//2 - 1, SPRITE_SIZE//4 + 20 - body_offset), 2)
            pygame.draw.line(img, outfit_color,
                             (SPRITE_SIZE//2 + 2, SPRITE_SIZE//4 + 13 - body_offset),
                             (SPRITE_SIZE//2 + 4, SPRITE_SIZE//4 + 20 - body_offset), 2)
    else:
        pygame.draw.line(img, outfit_color,
                         (SPRITE_SIZE//2 - 2, SPRITE_SIZE//4 + 13 - body_offset),
                         (SPRITE_SIZE//2 - 2, SPRITE_SIZE//4 + 20 - body_offset), 2)
        pygame.draw.line(img, outfit_color,
                         (SPRITE_SIZE//2 + 2, SPRITE_SIZE//4 + 13 - body_offset),
                         (SPRITE_SIZE//2 + 2, SPRITE_SIZE//4 + 20 - body_offset), 2)

    return img

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("16-bit Sprite Generator")
    clock = pygame.time.Clock()

    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color = (30, 30, 50 + int(y / HEIGHT * 20))
        pygame.draw.line(bg_surface, color, (0, y), (WIDTH, y))

    header_color = (255, 220, 100)
    label_color = (150, 220, 255)
    accent_color = (255, 128, 128)

    title_label = Label("16-Bit Sprite Generator", WIDTH//2 - 180, 20, header_color, 48)

    column_width = 200
    left_column_x = WIDTH//4 - column_width//2
    right_column_x = 3*WIDTH//4 - column_width//2
    row1_y = 80
    row2_y = 190
    row3_y = 380

    class_label = Label("Character Class:", left_column_x, row1_y, label_color)
    animation_label = Label("Animation Type:", right_column_x, row1_y, label_color)
    
    class_dropdown = Dropdown(
        left_column_x, row1_y + 30, column_width, 40,
        ['Warrior', 'Archer', 'Mage']
    )
    animation_dropdown = Dropdown(
        right_column_x, row1_y + 30, column_width, 40,
        ['Idle', 'Walking', 'Attacking', 'Defending', 'Dying']
    )
    
    generate_button = Button(
        left_column_x, row3_y, column_width, 50,
        'Generate Sprite'
    )
    save_button = Button(
        right_column_x, row3_y, column_width, 50,
        'Save Sprite'
    )
    
    speed_label = Label("Animation Speed:", WIDTH//2 - 100, row3_y + 70, label_color)
    speed_slider = Dropdown(
        WIDTH//2 - 150, row3_y + 100, 300, 40,
        ['Animation Speed: Normal', 'Animation Speed: Slow', 'Animation Speed: Fast']
    )

    all_sprites = pygame.sprite.RenderUpdates(
        class_dropdown, animation_dropdown, generate_button, save_button, speed_slider
    )
    
    current_frames = None
    generated_frames = {}
    current_preview_anim = None  # New variable

    preview_sprite = None
    preview_group = pygame.sprite.Group()

    preview_size = SPRITE_SIZE * 4
    preview_rect = pygame.Rect(
        WIDTH//2 - preview_size//2, 
        row2_y, 
        preview_size, 
        preview_size
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            class_dropdown.handle_event(event)
            animation_dropdown.handle_event(event)
            generate_button.handle_event(event)
            save_button.handle_event(event)
            speed_slider.handle_event(event)

        screen.blit(bg_surface, (0, 0))
        
        title_label.draw(screen)
        class_label.draw(screen)
        animation_label.draw(screen)
        speed_label.draw(screen)
        
        preview_label = Label("Preview", WIDTH//2 - 40, row2_y - 30, accent_color, 36)
        preview_label.draw(screen)
        
        outer_rect = pygame.Rect(preview_rect.x - 10, preview_rect.y - 10,
                              preview_rect.width + 20, preview_rect.height + 20)
        pygame.draw.rect(screen, (80, 80, 100), outer_rect)
        pygame.draw.rect(screen, (150, 150, 200), outer_rect, 2)
        
        pygame.draw.rect(screen, (60, 60, 80), preview_rect)
        
        checker_size = 8
        for x in range(preview_rect.left, preview_rect.right, checker_size):
            for y in range(preview_rect.top, preview_rect.bottom, checker_size):
                if (x//checker_size + y//checker_size) % 2 == 0:
                    pygame.draw.rect(screen, (80, 80, 100), 
                                   (x, y, checker_size, checker_size))
        
        for sprite in all_sprites:
            if not isinstance(sprite, Dropdown):
                screen.blit(sprite.image, sprite.rect)
        
        if generate_button.selected:
            class_val = class_dropdown.text.lower()
            selected_anim = animation_dropdown.text.lower()  # Preview selected anim when generate is clicked
            available_anims = ['idle', 'walking', 'attacking', 'defending', 'dying']
            generate_button.selected = False
            generate_button.update_image()
            
            preview_group.empty()
            generated_frames = {}
            
            skin_color = random.choice([(255, 213, 170), (240, 188, 150), (204, 145, 105), (160, 120, 90)])
            hair_color = random.choice([(50, 25, 0), (70, 50, 0), (255, 215, 0), (150, 75, 0)])
            if class_val == 'warrior':
                outfit_color = random.choice([(139, 0, 0), (165, 42, 42), (128, 128, 128)])
            elif class_val == 'archer':
                outfit_color = random.choice([(0, 100, 0), (34, 139, 34), (47, 79, 79)])
            else:
                outfit_color = random.choice([(75, 0, 130), (72, 61, 139), (25, 25, 112)])
            
            for anim in available_anims:
                frames = []
                for i in range(4):
                    frame_img = generate_sprite(class_val, anim, i, skin_color, hair_color, outfit_color)
                    frames.append(frame_img)
                generated_frames[anim] = frames
            
            # Update current preview using the initially selected anim
            current_preview_anim = selected_anim
            preview_frames = generated_frames[current_preview_anim]
            preview_sprite = GameSprite(preview_frames[0], preview_rect.x, preview_rect.y)
            for frame in preview_frames[1:]:
                preview_sprite.add_animation_frame(frame)
            if speed_slider.text == 'Animation Speed: Slow':
                preview_sprite.animation_speed = 3
            elif speed_slider.text == 'Animation Speed: Fast':
                preview_sprite.animation_speed = 8
            else:
                preview_sprite.animation_speed = 5
            preview_group.add(preview_sprite)
        
        # Check if the selected animation changed for preview
        if generated_frames and animation_dropdown.text.lower() != current_preview_anim:
            current_preview_anim = animation_dropdown.text.lower()
            preview_group.empty()
            preview_frames = generated_frames[current_preview_anim]
            preview_sprite = GameSprite(preview_frames[0], preview_rect.x, preview_rect.y)
            for frame in preview_frames[1:]:
                preview_sprite.add_animation_frame(frame)
            if speed_slider.text == 'Animation Speed: Slow':
                preview_sprite.animation_speed = 3
            elif speed_slider.text == 'Animation Speed: Fast':
                preview_sprite.animation_speed = 8
            else:
                preview_sprite.animation_speed = 5
            preview_group.add(preview_sprite)
        
        if save_button.selected and generated_frames:
            save_button.selected = False
            save_button.update_image()
            for anim, frames in generated_frames.items():
                for i, frame in enumerate(frames):
                    scaled_sprite = pygame.transform.scale(frame, (128, 160))
                    filename = f"{class_dropdown.text.lower()}_{anim}_{i}.png"
                    pygame.image.save(scaled_sprite, filename)
        
        if preview_sprite:
            preview_group.update()
            
            for sprite in preview_group:
                scaled_image = pygame.transform.scale(
                    sprite.image, 
                    (preview_rect.width - 20, preview_rect.height - 20)
                )
                sprite.image = scaled_image
                sprite.rect = scaled_image.get_rect(center=preview_rect.center)
            
            preview_group.draw(screen)
            
            status = f"{class_dropdown.text} - {animation_dropdown.text}"
            status_label = Label(status, WIDTH//2 - 80, preview_rect.bottom + 10, (255, 220, 100))
            status_label.draw(screen)
        
        for sprite in all_sprites:
            if isinstance(sprite, Dropdown):
                sprite.draw(screen)
        
        pygame.display.flip()  
        clock.tick(FPS)

# Determine run mode ("web" vs "pygame")
if len(sys.argv) > 1 and sys.argv[1] == "web":
    run_mode = "web"
else:
    run_mode = "pygame"

# Create a Flask app instance unconditionally (for gunicorn)
app = Flask(__name__)

if run_mode == "web":
    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/generate", methods=["POST"])
    def generate():
        char_class = request.form.get("class", "warrior").lower()
        anim = request.form.get("animation", "idle").lower()
        skin_color = random.choice([(255,213,170),(240,188,150),(204,145,105),(160,120,90)])
        hair_color = random.choice([(50,25,0),(70,50,0),(255,215,0),(150,75,0)])
        if char_class == "warrior":
            outfit_color = random.choice([(139,0,0),(165,42,42),(128,128,128)])
        elif char_class == "archer":
            outfit_color = random.choice([(0,100,0),(34,139,34),(47,79,79)])
        else:
            outfit_color = random.choice([(75,0,130),(72,61,139),(25,25,112)])
        sprite = generate_sprite(char_class, anim, 0, skin_color, hair_color, outfit_color)
        data = pygame.image.tostring(sprite, "RGBA")
        img = Image.frombytes("RGBA", (SPRITE_SIZE, SPRITE_SIZE), data)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    if run_mode == "web":
        app.run(debug=True)
    else:
        main()
