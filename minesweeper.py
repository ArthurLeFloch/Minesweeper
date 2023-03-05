import pygame
import sys
from pygame.locals import *
from ui import Slider, Button
from random import randint as rd
import numpy as np
import time


sys.setrecursionlimit(10000)

pygame.init()
pygame.display.set_caption("Minesweeper")
pygame_icon = pygame.image.load('icon.ico')
pygame.display.set_icon(pygame_icon)

flags = FULLSCREEN | DOUBLEBUF
SW, SH = 0,0
SCREEN = pygame.display.set_mode((SW, SH), flags, 16)
SW, SH = SCREEN.get_size()
clock = pygame.time.Clock()

dx = 0

settings = {'width':40, 'difficulty':.12, 'nbColor':0, 'dev':False, 'animation':True, 'settings':0}

colors = {'wallpaper': (10, 14, 18),
		  'settings': (100, 100, 100),
		  'button': {'none': (18, 22, 27), 'Bnone': (42, 47, 51),
					 'pushed': (109, 102, 91), 'Bpushed': (42, 47, 51),
					 'Rpushed': (40, 0, 10), 'BRpushed': (255, 165, 0),
					 'hovered': (50, 50, 50), 'Bhovered': (60, 60, 60)},
		  'numbers': {'1':
						{
							'0': '#000000',
							'1': '#ff6961',  # ? Pastel colors
							'2': '#ffb480',
							'3': '#f8f30d',
							'4': '#42d6a4',
							'5': '#08cad1',
							'6': '#59adf6',
							'7': '#9d94ff',
							'8': '#c780e8'},
					'0':
						{   
							'0': (0,0,0),
							'1': (0,0,255), # ? Classic colors
							'2': (0,255,0),
							'3': (255,0,0),
							'4': (55,55,200),
							'5': (200,55,55),
							'6': (55,200,55),
							'7': (55,55,200),
							'8': (80,80,80)},
					}
		  }

FONT = pygame.freetype.Font("fonts/MonoglycerideDemiBold.ttf", 24)
LITTLEFONT = pygame.freetype.Font("fonts/MonoglycerideDemiBold.ttf", 18)
BOLD = pygame.freetype.Font("fonts/MonoglycerideBold.ttf", 30)
Slider.font = LITTLEFONT
Button.font = FONT
Button.gridFont = FONT
Button.colors = [colors['numbers']['0'][str(k)] for k in range(9)]
Button.setupText()


FPS = 0 #? FPS max, 0 for infinite
execute = True

popup = ''
tab = None
gamesize = [0, 0]
mines = 0
tps = 0
tf = 0

def f1(v):
	if settings['dev']:
		return (99 * v - 900)/90
	else:
		return (99 * v - 975)/15


def f2(v):
	if settings['dev']:
		return (90 * v + 900)/99
	else:
		return (15 * v + 975)/99


def show_settings():
	if settings['settings'] > 0:
		FONT.render_to(SCREEN, (20, 20),
					   (f'fps : {int(clock.get_fps())}'), colors['settings'])
	if settings['settings'] == 2:
		k=0
		if settings['dev']:
			FONT.render_to(SCREEN, (20, 140),
					   (f'difficulty : {round(settings["difficulty"], 4)} (dev.)'), colors['settings'])
			FONT.render_to(SCREEN, (20, 200), (f"(total) : {len(Button.dict['grid'])} (dev.)"), colors['settings'])
			FONT.render_to(SCREEN, (20, 260),
					   (f'(well) : {Button.wellmarked} (dev.)'), colors['settings'])
			k = 30
		FONT.render_to(SCREEN, (20, 50),
					   (f'time : {int(time.time()-tps)}'), colors['settings'])
		FONT.render_to(SCREEN, (20, 80),
					   (f'dimension : {gamesize}'), colors['settings'])
		FONT.render_to(SCREEN, (20, 110), 
					   (f'mines : {mines}'), colors['settings'])
		FONT.render_to(SCREEN, (20, 140 + k),
					   (f'hidden : {Button.counting}'), colors['settings'])
		
		
		FONT.render_to(SCREEN, (20, 170 + 2 * k),
					   (f'flagged : {Button.marked}'), colors['settings'])
		
	if settings['settings'] == 3:
		k=0
		if settings['dev']:
			FONT.render_to(SCREEN, (20, 110),
					   '[d] : toggle dev. mode ', colors['settings'])
			FONT.render_to(SCREEN, (20, 140),
					   '[g] : get file (dev.) ', colors['settings'])
			k = 30
		FONT.render_to(SCREEN, (20, 50),
					   '[a] : toggle animation ', colors['settings'])
		FONT.render_to(SCREEN, (20, 80),
					   '[c] : toggle theme ', colors['settings'])
		FONT.render_to(SCREEN, (20, 110 + 2 * k),
					   '[h] : starting place ', colors['settings'])
		FONT.render_to(SCREEN, (20, 140 + 2 * k),
					   '[LSHIFT] : settings view ', colors['settings'])
		FONT.render_to(SCREEN, (20, 170 + 2 * k),
					   '[ ] : gen./accept ', colors['settings'])
		FONT.render_to(SCREEN, (20, 200 + 2 * k),
					   '[esc] : exit gen./game ', colors['settings'])
	if settings['dev']:
		FONT.render_to(SCREEN,(20, SH - 40),'Dev.',colors['settings'])
			


def research(tab, grid, j, i, count, animate, val, visited=[]):
	if val == -1:
		visited[j][i] = 1
	if val != -1 and animate and rd(0, val) == 0:
		SCREEN.fill(colors['wallpaper'])
		Button.update_grid(SCREEN, -1, -1, [])
		show_settings()
		pygame.display.update()
		clock.tick(0)
	if f'{i},{j}' in grid and not grid[f'{i},{j}'].marked:
		count+=1
		if tab[j][i] > 0:
			if val != -1:
				grid[f'{i},{j}'].hiddenText = False
				grid[f'{i},{j}'].hoverable = False
		else:
			del grid[f'{i},{j}']
			
			if f'{i+1},{j}' in grid:
				if tab[j][i+1] != -1:
					if (val == -1 and visited[j][i+1] == 0) or (val != -1 and grid[f'{i+1},{j}'].hoverable):
						count += research(tab, grid, j, i+1, 0, animate, val, visited)
			if f'{i-1},{j}' in grid:
				if tab[j][i-1] != -1:
					if (val == -1 and visited[j][i-1] == 0) or (val != -1 and grid[f'{i-1},{j}'].hoverable):
						count += research(tab, grid, j, i-1, 0, animate, val, visited)
			if f'{i},{j+1}' in grid:
				if tab[j+1][i] != -1:
					if (val == -1 and visited[j+1][i] == 0) or (val != -1 and grid[f'{i},{j+1}'].hoverable):
						count += research(tab, grid, j+1, i, 0, animate, val, visited)
			if f'{i},{j-1}' in grid:
				if tab[j-1][i] != -1:
					if (val == -1 and visited[j-1][i] == 0) or (val != -1 and grid[f'{i},{j-1}'].hoverable):
						count += research(tab, grid, j-1, i, 0, animate, val, visited)
			if f'{i-1},{j-1}' in grid:
				if tab[j-1][i-1] != -1:
					if (val == -1 and visited[j-1][i-1] == 0) or (val != -1 and grid[f'{i-1},{j-1}'].hoverable):
						count += research(tab, grid, j-1, i-1, 0, animate, val, visited)
			if f'{i-1},{j+1}' in grid:
				if tab[j+1][i-1] != -1:
					if (val == -1 and visited[j+1][i-1] == 0) or (val != -1 and grid[f'{i-1},{j+1}'].hoverable):
						count += research(tab, grid, j+1, i-1, 0, animate, val, visited)
			if f'{i+1},{j+1}' in grid:
				if tab[j+1][i+1] != -1:
					if (val == -1 and visited[j+1][i+1] == 0) or (val != -1 and grid[f'{i+1},{j+1}'].hoverable):
						count += research(tab, grid, j+1, i+1, 0, animate, val, visited)
			if f'{i+1},{j-1}' in grid:
				if tab[j-1][i+1] != -1:
					if (val == -1 and visited[j-1][i+1] == 0) or (val != -1 and grid[f'{i+1},{j-1}'].hoverable):
						count += research(tab, grid, j-1, i+1, 0, animate, val, visited)
	return count



def discover(tab, j, i, fps):
	val = 0
	if settings['animation']:
		SCREEN.fill(colors['wallpaper'])
		Button.update_grid(SCREEN, -1, -1, [])
		show_settings()
		pygame.display.update()
		clock.tick(0)
		
		visited = np.zeros((len(tab),len(tab[0])))
		k = research(tab, Button.dict['grid'].copy(), j, i, 0, False, -1,visited)
		
		val = int(k/fps)
	
	research(tab, Button.dict['grid'], j, i, 0, settings['animation'], val)
	
	SCREEN.fill(colors['wallpaper'])
	Button.update_grid(SCREEN, -1, -1, [])


def pop_up(msg):
	if popup in ['Victory !','Lost !','Generation :']:
		pygame.draw.rect(SCREEN, (0, 0, 0), (SW//2-200, SH//2-160, 400, 320), border_radius=26)
		pygame.draw.rect(SCREEN, (15, 15, 15), (SW//2-196, SH//2-156, 392, 312), border_radius=22)
		pygame.draw.line(SCREEN,(0,0,0),(SW//2-200,SH//2 - 100),(SW//2+196,SH//2-100),4)
		pygame.draw.line(SCREEN,(0,0,0),(SW//2,SH//2 - 100),(SW//2,SH//2+160),4)
		texte = BOLD.render(msg, (255, 255, 255))
		SCREEN.blit(texte[0], (SW//2-texte[1].width//2, SH//2 - 130 - texte[1].height//2))
		#* Statistics
		total = gamesize[0]*gamesize[1]
		texte = FONT.render('Statistics :', (200, 200, 200))
		SCREEN.blit(texte[0], (SW//2-100-texte[1].width//2, SH//2 - 70 - texte[1].height//2))

		LITTLEFONT.render_to(SCREEN,(SW//2 - 180, SH//2 - 40),f'Dimensions : {gamesize}',(150,150,150))
		LITTLEFONT.render_to(SCREEN,(SW//2 - 180, SH//2 - 20),f'({total} cases)',(150,150,150))

		LITTLEFONT.render_to(SCREEN,(SW//2 - 180, SH//2 + 10),f'Mines : {mines}',(150,150,150))

		LITTLEFONT.render_to(SCREEN,(SW//2 - 180, SH//2 + 40),f'Difficulty : {int(f1(100*settings["difficulty"]))}',(150,150,150))

		LITTLEFONT.render_to(SCREEN,(SW//2 - 180, SH//2 + 70),f'Time : {tf if popup in ["Victory !", "Lost !"] else int(time.time()-tps)}s',(150,150,150))

		#* Rejouer ?
		texte = FONT.render('Play again ?', (200, 200, 200))
		SCREEN.blit(texte[0], (SW//2+100-texte[1].width//2, SH//2 - 70 - texte[1].height//2))

		texte = LITTLEFONT.render('Width :', (150, 150, 150))
		SCREEN.blit(texte[0], (SW//2+100-texte[1].width//2, SH//2 - 40))

		texte = LITTLEFONT.render('Difficulty :', (150, 150, 150))
		SCREEN.blit(texte[0], (SW//2+100-texte[1].width//2, SH//2 + 30))
	else:
		pygame.draw.rect(SCREEN, (0, 0, 0), (SW//2-200, SH//2-30, 400, 60), border_radius=26)
		pygame.draw.rect(SCREEN, (15, 15, 15), (SW//2-196, SH//2-26, 392, 52), border_radius=22)
		texte = BOLD.render(msg, (255, 255, 255))
		SCREEN.blit(texte[0], (SW//2-texte[1].width//2, SH//2 - texte[1].height//2))


def setup_btn(size):
	tmp = pygame.Surface((size, size))
	pygame.draw.rect(tmp, colors['button']['Bpushed'], (0, 0, size, size))
	pygame.draw.rect(tmp, colors['button']['pushed'], (1, 1, size-2, size-2))
	Button.pushed = tmp

	tmp = pygame.Surface((size, size))
	pygame.draw.rect(tmp, colors['button']['BRpushed'], (0, 0, size, size))
	pygame.draw.rect(tmp, colors['button']['Rpushed'], (1, 1, size-2, size-2))
	Button.Rpushed = tmp

	tmp = pygame.Surface((size, size))
	pygame.draw.rect(tmp, colors['button']['Bhovered'], (0, 0, size, size))
	pygame.draw.rect(tmp, colors['button']['hovered'], (1, 1, size-2, size-2))
	Button.hovered = tmp

	tmp = pygame.Surface((size, size))
	pygame.draw.rect(tmp, colors['button']['Bnone'], (0, 0, size, size))
	pygame.draw.rect(tmp, colors['button']['none'], (1, 1, size-2, size-2))
	Button.none = tmp


def incr(tab, j, i):
	"""
	Incrémente les valeurs adjacentes de la position ligne j colonne i
	"""
	x, y = len(tab[0])-1, len(tab)-1
	c1 = i > 0
	c2 = j > 0
	c3 = i < x
	c4 = j < y
	if c1 and c2 and tab[j-1][i-1] != -1:
		tab[j-1][i-1] += 1
	if c1 and tab[j][i-1] != -1:
		tab[j][i-1] += 1
	if c1 and c4 and tab[j+1][i-1] != -1:
		tab[j+1][i-1] += 1
	if c4 and tab[j+1][i] != -1:
		tab[j+1][i] += 1
	if c4 and c3 and tab[j+1][i+1] != -1:
		tab[j+1][i+1] += 1
	if c3 and tab[j][i+1] != -1:
		tab[j][i+1] += 1
	if c3 and c2 and tab[j-1][i+1] != -1:
		tab[j-1][i+1] += 1
	if c2 and tab[j-1][i] != -1:
		tab[j-1][i] += 1


def find_start(tab,fps):
	l = [*Button.dict['grid']]
	test = 0
	v = l[rd(0, len(l) - 1)]
	i, j = v.split(',')
	i = int(i)
	j = int(j)
	while test < 1000 and tab[j][i] != 0:
		v = l[rd(0, len(l) - 1)]
		i, j = v.split(',')
		i = int(i)
		j = int(j)
		test += 1
	if tab[j][i] == 0:
		discover(tab, j, i, fps)


def set_grid(cx, cy=0, mines=-1):
	Button.xp,Button.yp = None, None
	Button.xr,Button.yr = None, None
	Button.explodeColor = (None, None, None)
	global tps
	tps = time.time()
	Button.dict['grid'] = {}
	Button.wellmarked = 0
	if not cy:
		cy = int(cx * SH / SW)
	if mines == -1:
		mines = int(cx * cy * settings['difficulty'])
	if mines > cx * cy:
		mines = 1
	size = min(int((SW - 2 * dx) / cx), int((SH - 2 * dx) / cy))
	gamesize[0] = cx
	gamesize[1] = cy

	F1 = pygame.freetype.Font("fonts/MonoglycerideDemiBold.ttf", size - 1)
	Button.gridFont = F1
	Button.setupText()
	setup_btn(size)

	dx1 = (SW - cx * size) / 2
	dy1 = (SH - cy * size) / 2

	tab = np.zeros((cy, cx))
	placed = 0
	while placed < mines:
		rx, ry = rd(0, cx - 1), rd(0, cy - 1)
		if tab[ry][rx] != -1:
			tab[ry][rx] = -1
			incr(tab, ry, rx)
			placed += 1

	for x in range(cx):
		for y in range(cy):
			Button(f"{x},{y}", (dx1 + size * x, dy1 + size * y),
				   (size, size), 'grid', str(int(tab[y][x])), True)
	find_start(tab, 1)
	return tab, mines



def explode(fps,good=False):
	
	val = max(1, int(2 * 255 / fps))
	if good:
		i = 0
		while i < 120:
			Button.explodeColor = (10, i, 18)
			SCREEN.fill(colors['wallpaper'])
			Button.update_grid(SCREEN, -1, -1, [])
			show_settings()
			pygame.display.update()
			clock.tick(0)
			i+=min(120, val)
	else:
		i=0
		while i < 120:
			Button.explodeColor = (i, 14, 18)
			SCREEN.fill(colors['wallpaper'])
			Button.update_grid(SCREEN, -1, -1, [])
			show_settings()
			pygame.display.update()
			clock.tick(0)
			i += min(120, val)

	gr = Button.dict['grid']
	val = max(1, int(2 * len(gr) / fps))
	l = list(gr)
	b = True
	while gr != {} and b:
		for _ in range(val):
			i = rd(0,len(l)-1)
			key = str(gr[l[i]])
			if key in gr and gr[key].text != '-1':
				l.pop(i)
				del gr[key]
			elif len(l) == mines:
				b = False
		SCREEN.fill(colors['wallpaper'])
		Button.update_grid(SCREEN, -1, -1, [])
		show_settings()
		pygame.display.update()
		clock.tick(0)
		  
	SCREEN.fill(colors['wallpaper'])
	Button.update_grid(SCREEN, -1, -1, [])
	_ = pygame.event.get()
	
popup = ''

while execute:
	
	SCREEN.fill(colors['wallpaper'])

	events = pygame.event.get().copy()
	xm, ym = pygame.mouse.get_pos()

	if Button.dict['grid'] == {}:
		i = rd(5, 100)
		tab, mines = set_grid(i)

	if popup == '':
		tf = 0
		Button.explodeColor = (None, None, None)
		Button.update_grid(SCREEN, xm, ym, events)
	else:
		Button.update_grid(SCREEN, -1, -1, [])
		pop_up(popup)
		if popup in ['Victory !', 'Lost !', 'Generation :']:
			if not 'playAgain' in Button.dict['classic']:
				Button('playAgain', (SW // 2 + 20, SH // 2 + 100), (160, 40), 'classic', 'Play again')
				Button('quit', (SW // 2-180, SH // 2 + 100), (160, 40), 'classic', 'Quit')
			if not 'size' in Slider.dict:
				Slider('size', (SW // 2 + 20, SH // 2 - 10), (160, 25),(5, 100), settings['width'])
				Slider('difficulty', (SW//2 +20, SH//2 + 60), (160,25), (1,100), int(f1(100 * settings['difficulty'])))
			Button.update(SCREEN, xm, ym, events)
			Slider.update(SCREEN, xm, ym)

	if popup in ['Victory !', 'Lost !', 'Generation :']:
		if Button.dict['classic']['playAgain'].clickedUp:
			settings['width'] = Slider.dict['size'].value
			settings['difficulty'] = f2(Slider.dict['difficulty'].value) / 100
			tab, mines = set_grid(settings['width'])
			del Button.dict['classic']['playAgain']
			del Slider.dict['size']
			del Slider.dict['difficulty']
			Button.counting = 0
			popup = ''
			SCREEN.fill(colors['wallpaper'])
			Button.update_grid(SCREEN, -1, -1, [])
			if popup != 'Generation :':
				tf = 0
		elif Button.dict['classic']['quit'].clickedUp:
			execute = False
	

	if (Button.counting == mines or (Button.wellmarked == mines and Button.marked == mines)) and popup != 'Lost !' and tf == 0 and mines != gamesize[0] * gamesize[1]:
		tf = int(time.time() - tps)
		if settings['animation']:
			explode(max(1, fps), True)
		popup = 'Victory !'

	for event in events:
		
		if event.type == QUIT:
			execute = False

		if event.type == MOUSEBUTTONUP:
			if popup.startswith('Entered') or popup.startswith('Exited'):
				popup = ''
			if event.button == 1:
				
				b = f'{Button.xp},{Button.yp}' in Button.dict['grid'] and not Button.dict['grid'][f'{Button.xp},{Button.yp}'].marked
				if b and popup == '':
					if tab[Button.yp, Button.xp] == -1:
						tf = int(time.time() - tps)
						if settings['animation']:
							explode(max(1, fps))
						popup = 'Lost !'
					else:
						discover(tab, Button.yp, Button.xp, max(1, fps))

		pressed_keys = pygame.key.get_pressed()

		if event.type == KEYDOWN:
			if pressed_keys[K_ESCAPE]:
				if not popup in ['Victory !', 'Lost !', '']:
					popup = ''
				else:
					execute = False

			if pressed_keys[K_SPACE]:
				if popup == '':
					popup = 'Generation :'
				else:
					settings['width'] = Slider.dict['size'].value
					settings['difficulty'] = f2(Slider.dict['difficulty'].value)/100
					tab,mines = set_grid(settings['width'])
					del Button.dict['classic']['playAgain']
					del Slider.dict['size']
					del Slider.dict['difficulty']
					Button.counting = 0
					popup = ''
					SCREEN.fill(colors['wallpaper'])
					Button.update_grid(SCREEN, -1, -1, [])
					
			if pressed_keys[K_h] and popup == '':
				find_start(tab, max(1, fps))
				
			if pressed_keys[K_LSHIFT]:
				if settings['settings'] < 3:
					settings['settings'] += 1
				else:
					settings['settings'] = 0
			
			if pressed_keys[K_a]:
				settings['animation'] = not settings['animation']
					
			if pressed_keys[K_c]:
				settings['nbColor'] = 1 - settings['nbColor']
				Button.colors = [colors['numbers'][str(settings['nbColor'])][str(k)] for k in range(9)]
				Button.setupText()

			if pressed_keys[K_d] and popup == '':
				settings['dev'] = not settings['dev']
				if not settings['dev'] and settings['difficulty'] > .25:
					settings['difficulty'] = 0.25
				a = 'Entered' if settings['dev'] else 'Exited'
				popup = a + ' developer mode !'
			
	fps = int(clock.get_fps())
	show_settings()
	pygame.display.update()
	clock.tick(FPS)

pygame.quit()
sys.exit()