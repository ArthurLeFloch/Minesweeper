import pygame
import sys
import random
import math
from pygame import freetype
from pygame.locals import *
import numpy as np
import matplotlib.pyplot as plt


class Slider:

    """
    Create a slider, get its value with Slider.dict[sliderName].value
    """

    font = None
    focused = None
    dict = {}

    def __init__(self, name, pos=(100, 200), size=(300, 40), limits=(0, 100), default=40, step=1, vertical=False, thickness=3):
        self.pos = pos
        self.name = name
        self.size = size
        self.step = step
        self.rect = pygame.Rect((pos[0], pos[1]), (size[0], size[1]))
        self.value = default
        self.limits = limits
        self.default = default
        self.vertical = vertical
        self.thickness = thickness
        Slider.dict[name] = self

    def update(window, x, y):
        for key in Slider.dict:
            self = Slider.dict[key]
            if (not self.rect.collidepoint(x, y) or not pygame.mouse.get_pressed()[0]) and Slider.focused == key:
                Slider.focused = None
            radius = (self.size[1]-2*self.thickness)//2
            pygame.draw.rect(
                window, (0, 93, 67), (self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=30)
            pygame.draw.rect(window, (0, 66, 47), (self.pos[0]+self.thickness, self.pos[1]+self.thickness,
                             self.size[0]-2*self.thickness, self.size[1]-2*self.thickness), border_radius=26)
            if self.rect.collidepoint(x, y):
                if pygame.mouse.get_pressed()[0]:
                    self.value = max(self.limits[0], min(self.limits[1], self.limits[0] + 10**(-self.step)*int(10**(self.step)*(
                        x-self.pos[0]-radius-self.thickness)*(self.limits[1]-self.limits[0])/(self.size[0]-2*self.thickness-2*radius))))
                    Slider.focused = key
                    if self.step == 1:
                        self.value = round(self.value)
                Slider.font.render_to(
                    window, (x, self.pos[1]-20), str(self.value), (255, 255, 255))
            pygame.draw.circle(window, (255, 255, 255), (self.pos[0] + self.thickness + radius + 10**(-self.step)*int((10**self.step)*(
                self.size[0]-2*self.thickness-2*radius)*(self.value-self.limits[0])/(self.limits[1]-self.limits[0])), self.pos[1]+self.size[1]//2), radius)


class Button:

    """
    Create a button, clicked event : Button.dict[buttonName].clickedUp
    """

    font = None
    gridFont = None
    dict = {'classic': {}, 'grid': {}}
    numbers = [None, None, None, None, None, None, None, None, None]
    colors = [(0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0), (55, 55, 200), (200, 55, 55), (55, 200, 55), (55, 55, 200), (80, 80, 80)]
    explodeColor = (None, None, None)

    exploding = None
    pushed = None
    hovered = None
    none = None

    counting = 0
    marked = 0
    wellmarked = 0
    xp, yp = None, None
    xr, yr = None, None

    def __init__(self, name, pos=(100, 100), size=(300, 40), type='classic', text='', hiddenText=False, hoverable=True, thickness=3):
        self.pos = pos
        self.name = name
        self.size = size
        self.text = text
        self.rect = pygame.Rect((pos[0], pos[1]), (size[0], size[1]))
        self.down = False  # * True si bouton appuyé, False sinon
        self.clickedUp = False
        if type == 'grid':
            self.RclickedUp = False
            self.marked = False
        self.hoverable = hoverable
        self.hiddenText = hiddenText
        self.thickness = thickness
        Button.dict[type][name] = self

    def __repr__(self):
        return self.name  # + ' ' + str(self.down) + ' ' + str(self.clickedUp)

    def setupText():
        for k in range(len(Button.numbers)):
            Button.numbers[k] = Button.gridFont.render(
                str(k), Button.colors[k])

    def update(window, x, y, events):
        k2 = ''
        for key in Button.dict['classic']:
            pressed = pygame.mouse.get_pressed()[0]
            self = Button.dict['classic'][key]
            self.clickedUp = False
            test = self.rect.collidepoint(x, y)
            self.down = test and pressed
            if test:
                k2 = key
            if self.down:
                pygame.draw.rect(
                    window, (0, 93, 67), (self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=10)
                pygame.draw.rect(window, (0, 66, 47), (self.pos[0]+self.thickness, self.pos[1]+self.thickness,
                                 self.size[0]-2*self.thickness, self.size[1]-2*self.thickness), border_radius=8)
            elif test and self.hoverable:
                pygame.draw.rect(
                    window, (93, 67, 0), (self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=10)
                pygame.draw.rect(window, (66, 47, 0), (self.pos[0]+self.thickness, self.pos[1]+self.thickness,
                                 self.size[0]-2*self.thickness, self.size[1]-2*self.thickness), border_radius=8)
            else:
                pygame.draw.rect(
                    window, (90, 90, 90), (self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=10)
                pygame.draw.rect(window, (60, 60, 60), (self.pos[0]+self.thickness, self.pos[1]+self.thickness,
                                 self.size[0]-2*self.thickness, self.size[1]-2*self.thickness), border_radius=8)
            if not self.hiddenText:
                texte = Button.font.render(self.text, (255, 255, 255))
                window.blit(texte[0], (self.pos[0]+self.size[0]//2-texte[1].width //
                            2, self.pos[1]+self.size[1]//2-texte[1].height//2))

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if k2 != '':
                    Button.dict['classic'][k2].clickedUp = True

    def update_grid(window, x, y, events):
        p1, _, p2 = pygame.mouse.get_pressed()
        k2 = ''
        Button.counting = 0
        Button.marked = 0
        if Button.explodeColor != (None, None, None):
            size = Button.pushed.get_size()[0]
            tmp = pygame.Surface((size, size))
            pygame.draw.rect(tmp, (255, 255, 255), (0, 0, size, size))
            pygame.draw.rect(tmp, Button.explodeColor,
                             (1, 1, size-2, size-2))
            Button.exploding = tmp
        for key in Button.dict['grid']:
            self = Button.dict['grid'][key]
            self.clickedUp = False
            self.RclickedUp = False
            test = self.rect.collidepoint(x, y) and (
                self.text in ["-1", "0"] or self.hiddenText)
            self.down = test and p1
            if test:
                k2 = key
            if self.down and not self.marked:
                window.blit(Button.pushed, (self.pos[0], self.pos[1]))
            elif (test and p2) or (self.marked and Button.explodeColor == (None, None, None)):
                window.blit(Button.Rpushed, (self.pos[0], self.pos[1]))
            elif test and self.hoverable:
                window.blit(Button.hovered, (self.pos[0], self.pos[1]))
            elif not self.text in ["-1", "0"] and not self.hiddenText:
                texte = Button.numbers[int(self.text)]
                window.blit(texte[0], (self.pos[0]+self.size[0]//2-texte[1].width //
                            2, self.pos[1]+self.size[1]//2-texte[1].height//2))
            elif Button.explodeColor != (None, None, None) and self.text == '-1':
                window.blit(Button.exploding, (self.pos[0], self.pos[1]))
            else:
                window.blit(Button.none, (self.pos[0], self.pos[1]))
            if self.hiddenText:
                Button.counting += 1
            if self.marked:
                Button.marked += 1

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if k2 != '':
                    self = Button.dict['grid'][k2]
                    if event.button == 1:
                        self.clickedUp = True
                        Button.xp, Button.yp = k2.split(',')
                        Button.xp = int(Button.xp)
                        Button.yp = int(Button.yp)
                    if event.button == 3:
                        self.RclickedUp = True
                        if self.text in ['-1', '0'] or self.hiddenText:
                            if self.marked:
                                self.marked = False
                                Button.marked -= 1
                                if self.text == '-1':
                                    Button.wellmarked -= 1
                            else:
                                self.marked = True
                                Button.marked += 1
                                if self.text == '-1':
                                    Button.wellmarked += 1

                        Button.xr, Button.yr = k2.split(',')
                        Button.xr = int(Button.xr)
                        Button.yr = int(Button.yr)
