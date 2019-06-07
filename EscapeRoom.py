





#!/usr/bin/python3
import pygame
from pygame.locals import *
import random
import RPi.GPIO as GPIO


def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


class Pointer(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('pointer.png'), (300, 50))
        self.seconds = 3720;
        # A reference to the original image to preserve the quality.
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)  # The original center position/pivot point.
        self.offset = pygame.math.Vector2(42, 0)  # We shift the sprite 50 px to the right.
        self.angle = -180
        self.active = False

    def update(self):
        if self.active:
            if self.angle > -195:
                self.angle -= 3
        else:
            if dead:
                self.angle += 20
            else:
                self.angle = -195 + 220 * (3720 - self.seconds) / 3720
        self.rotate()

    def rotate(self):
        """Rotate the image of the sprite around a pivot point."""
        # Rotate the image.
        if self.active == True:
            random_angle = self.angle
        else:
            random_angle = self.angle + random.random() * 9 * (3720 - self.seconds) / 3720
        self.image = pygame.transform.rotozoom(self.orig_image, -random_angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(random_angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos+offset_rotated)


GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('alarm.mp3')
print(pygame.display.list_modes(32)[0])
screen = pygame.display.set_mode(pygame.display.list_modes(32)[0], pygame.FULLSCREEN)
pygame.display.set_caption('Escape Room')
pygame.mouse.set_visible(0)
background = pygame.image.load('background.png')
renders = pygame.sprite.RenderUpdates()
pointer = Pointer((350, 324))
group = pygame.sprite.Group(pointer)
clock = pygame.time.Clock()
font = pygame.font.Font('audiowide.ttf', 128)
started = False
start_time = 0
dead = False
warned = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.mixer.music.stop()
            pygame.quit()
            quit()
    GPIO.output(5, not started)
    GPIO.output(3, not dead)
    GPIO.output(13, not pointer.active)
    if GPIO.input(11):
        dead = False
        warned = False
        started = False
        pointer.active = False
        pygame.mixer.music.stop()
    group.update()
    screen.fill((0, 80, 150))
    screen.blit(background, (0, -50))
    group.draw(screen)
    if started:
        if dead or pointer.active:
            total_seconds = 0
        else:
            total_seconds = 3720 - (pygame.time.get_ticks() - start_time) / 1000
            if not warned and total_seconds <= 600:
                warned = True
                pygame.mixer.music.play(-1)
            if total_seconds <= 0:
                dead = True
                pygame.mixer.music.stop()
                pygame.mixer.music.load('airraide.mp3')
                pygame.mixer.music.play()
            
    else:
        total_seconds = 3720
        if GPIO.input(8):
            started = True
            start_time = pygame.time.get_ticks()
    if total_seconds < 0:
        total_seconds = 0
    seconds = int(total_seconds % 60)
    minutes = int(total_seconds / 60)
    pointer.seconds = total_seconds
    if dead:
        dead_text = font.render('You are dead!', True, (255, 0, 0))
        screen.blit(dead_text, dead_text.get_rect(center=(600, 200)))
    if not pointer.active:
        text = font.render((str(0) if minutes < 10 and not minutes is 0 else '') + str(minutes) + (str(0) if minutes is 0 else '') + ':' + (str(0) if seconds < 10 and not seconds is 0 else '') + str(seconds) + (str(0) if seconds is 0 else ''), True, (0, 255, 0) if total_seconds > 600 else (255, 0, 0))
    screen.blit(text, text.get_rect(center=(900, 350)))
    pygame.display.flip()
    if GPIO.input(7):
        pointer.active = True
        pygame.mixer.music.stop()
    clock.tick(30)
