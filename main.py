import pygame, random
from pygame.locals import *

pygame.init()

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)


class Game:

    def __init__(self):
        self.width = 1920
        self.height = 1080
        self.resolution = self.width, self.height
        self.midpoint = self.width/2, self.height/2
        self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        self.turn = 1
        self.objects = GameObjects()

    def setup(self):
        global player, camera, side_gui, clock

        clock = pygame.time.Clock()

        player = Player()

        Grid.generate_grid()
        Grid.generate_border()
        Grid.generate_terrain()

        self.spawn_fighters(4)

        player.spawn((1, 1))

        camera = Camera(player)

        side_gui = SideGui()
        side_gui.active = True
        side_gui.message('Startup')

    def next_turn(self):
        for i in game.objects.all_npcs:
            i.brain()
        self.turn += 1
        camera.update()

    def spawn_fighters(self, num_each):
        d = {}
        for i in range(num_each-1):
            d[i] = NPC(f'Blue {i+2}', 'blue', 'Blue')
            d[i].spawn((2+i, 1))
        for i in range(num_each):
            d[i] = NPC(f'Red {i+1}', 'red', 'Red')
            d[i].spawn((Grid.grid_width - 1-i, Grid.grid_height - 1))
        for i in range(num_each):
            d[i] = NPC(f'Green {i+1}', 'green', 'Green')
            d[i].spawn((Grid.grid_width - 1, 1+i))
        for i in range(num_each):
            d[i] = NPC(f'Yellow {i+1}', 'yellow', 'Yellow')
            d[i].spawn((1, Grid.grid_height - 1-i))

    def game_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    exit()

            self.screen.fill(white)

            self.objects.all_objects.sort(key=lambda x: x.blit_priority)

            for i in self.objects.all_objects:
                self.screen.blit(i.surf, (i.rect.x-camera.camera_rect.x, i.rect.y-camera.camera_rect.y))
            for i in self.objects.all_guis:
                if i.active:
                    self.screen.blit(i.surf, i.rect)
                    i.surf.fill(black)
                    for x in range(len(i.elements)):
                        i.surf.blit(i.elements[x].surf, i.elements[x].rect)

            player.tick_input(events)
            pygame.display.flip()

            clock.tick()


class GameObjects:

    def __init__(self):
        self.all_objects = []
        self.all_grid_objects = []
        self.grid_coords = {}
        self.all_players = []
        self.all_npcs = []
        self.all_walls = []
        self.all_tiles = []
        self.all_guis = []

    def add_basic_object(self, obj):
        self.all_objects.append(obj)

    def add_player_object(self, obj):
        self.all_objects.append(obj)
        self.all_players.append(obj)

    def add_npc_object(self, obj):
        self.all_objects.append(obj)
        self.all_npcs.append(obj)

    def add_grid_object(self, obj):
        self.all_grid_objects.append(obj)

    def add_wall_object(self, obj):
        self.all_objects.append(obj)
        self.all_walls.append(obj)

    def add_tile_object(self, obj):
        self.all_objects.append(obj)
        self.all_tiles.append(obj)

    def add_gui(self, obj):
        self.all_guis.append(obj)

    @staticmethod
    def remove(obj):
        for i in dir(game.objects):
            x = game.objects.__getattribute__(i)
            if isinstance(x, type([])):
                if obj in x:
                    del x[x.index(obj)]


class Grid:

    gp_width = 32
    gp_height = 32
    dimensions = '32x32'
    grid_width = int(dimensions.split('x')[0])
    grid_height = int(dimensions.split('x')[1])

    def __init__(self, x, y):
        self.surf = pygame.image.load('tiles\\gridpoint.png')
        self.surf = pygame.transform.scale(self.surf, (int(Grid.gp_width), int(Grid.gp_height)))
        self.rect = self.surf.get_rect(topleft=(x,y))
        self.grid_x = 0
        self.grid_y = 0
        self.objects = []
        self.impassable = False
        game.objects.add_grid_object(self)

    @staticmethod
    def find_gp_w_h():
        for i in range(25, 100):
            if game.width % i == 0:
                w_divisor = int(i)
                break
        for i in range(25, 100):
            if game.height % i == 0:
                h_divisor = int(i)
                break
        return w_divisor, h_divisor

    @staticmethod
    def generate_grid():
        points = {}
        obj_index = 0
        x = 0
        y = 0
        x2 = Grid.grid_width
        y2 = Grid.grid_height
        x_coord = 0
        y_coord = 0
        while True:
            if y2 < 0:
                return points
            if x2 < 0:
                x = 0
                x2 = Grid.grid_width
                x_coord = 0
                y += Grid.gp_height
                y2 -= 1
                y_coord += 1
                continue
            points[str(obj_index)] = Grid(x, y)
            game.objects.grid_coords[(x_coord, y_coord)] = points[str(obj_index)]
            points[str(obj_index)].grid_x = x_coord
            points[str(obj_index)].grid_y = y_coord
            x += Grid.gp_width
            x2 -= 1
            x_coord += 1
            obj_index += 1

    @staticmethod
    def generate_border():
        walls = {}
        for i in range(Grid.grid_width):
            walls[i] = Wall('void wall')
            walls[i].spawn((0, i))
        for i in range(Grid.grid_height):
            walls[i] = Wall('void wall')
            walls[i].spawn((i, 0))
        for i in range(Grid.grid_width):
            walls[i] = Wall('void wall')
            walls[i].spawn((i, Grid.grid_height))
        for i in range(Grid.grid_height+1):
            walls[i] = Wall('void wall')
            walls[i].spawn((Grid.grid_width, i))

    @staticmethod
    def generate_terrain():
        terrain = {}
        x = Grid.grid_width+1
        y = 0
        while True:
            if y > Grid.grid_height:
                return
            for i in range(x):
                if game.objects.grid_coords[(i, y)].objects:
                    continue
                rnd = random.randrange(4)
                if rnd == 1:
                    terrain[i] = Wall('stone wall')
                    terrain[i].spawn((i, y))
                else:
                    terrain[i] = Tile('grass')
                    terrain[i].spawn((i, y))
            y += 1


class Entity:

    def __init__(self):
        self.grid_x = 0
        self.grid_y = 0
        self.on_grid = None
        self.rect = Rect(0, 0, 0, 0)
        self.surf = None
        self.rect = None
        self.blit_priority = 0
        self.impassable = False
        self.adj_grids = {}
        self.name = 'Entity'
        self.team = None
        self.health = 100
        self.dead = False
        self.attack_dmg_range = 0, 0

    def spawn(self, coords):
        start_gridpos = game.objects.grid_coords[(coords[0], coords[1])]
        if self.impassable:
            start_gridpos.impassable = True
        self.rect.center = start_gridpos.rect.center
        self.grid_x = start_gridpos.grid_x
        self.grid_y = start_gridpos.grid_y
        self.on_grid = game.objects.grid_coords[(self.grid_x, self.grid_y)]
        start_gridpos.objects.append(self)
        self.find_adj_gridpoints()

    def find_adj_gridpoints(self):
        try:
            self.adj_grids['topleft'] = game.objects.grid_coords[(self.grid_x - 1, self.grid_y - 1)]
            self.adj_grids['top'] = game.objects.grid_coords[(self.grid_x, self.grid_y - 1)]
            self.adj_grids['topright'] = game.objects.grid_coords[(self.grid_x + 1, self.grid_y - 1)]
            self.adj_grids['left'] = game.objects.grid_coords[(self.grid_x - 1, self.grid_y)]
            self.adj_grids['right'] = game.objects.grid_coords[(self.grid_x + 1, self.grid_y)]
            self.adj_grids['bottomleft'] = game.objects.grid_coords[(self.grid_x - 1, self.grid_y + 1)]
            self.adj_grids['bottom'] = game.objects.grid_coords[(self.grid_x, self.grid_y + 1)]
            self.adj_grids['bottomright'] = game.objects.grid_coords[(self.grid_x + 1, self.grid_y + 1)]
        except KeyError:
            return

    def move(self, direction):
        movegrid = self.adj_grids[direction]
        if movegrid.impassable:
            return

        if self.on_grid.impassable:
            for i in self.on_grid.objects:
                if not i.impassable:
                    self.on_grid.impassable = False

        self.on_grid.objects.remove(self)
        movegrid.objects.append(self)
        self.rect.center = movegrid.rect.center
        self.grid_x = movegrid.grid_x
        self.grid_y = movegrid.grid_y

        if self.impassable:
            movegrid.impassable = True

        self.on_grid = movegrid
        self.find_adj_gridpoints()

    def attack(self, victim):
        atk = random.randrange(self.attack_dmg_range[0], self.attack_dmg_range[1])
        victim.health -= atk

        if victim.team != player.team:
            msgcolor = yellow
        if victim.team == player.team:
            msgcolor = red
        if self.team == player.team:
            msgcolor = blue

        side_gui.message('{} attacks {} dealing {} damage!'.format(self.name, victim.name, atk), color=msgcolor)
        side_gui.message('{} now has {} health!'.format(victim.name, victim.health), color=msgcolor)

        blood = Misc(pygame.image.load(f'tiles\\blood{random.randrange(1, 4)}.png'), rota=90*random.randrange(3))
        blood.spawn((victim.grid_x, victim.grid_y))
        blood.blit_priority = 2

        if victim.health < 1:
            victim.die()

    def die(self):
        side_gui.message('{} has died!'.format(self.name), color=yellow)
        game.objects.remove(self)
        del self.on_grid.objects[self.on_grid.objects.index(self)]
        self.on_grid.impassable = False
        for i in self.on_grid.objects:
            if i.impassable:
                self.on_grid.impassable = True
        grave = Misc(pygame.image.load('tiles\\grave.png'))
        grave.spawn((self.on_grid.grid_x, self.on_grid.grid_y))
        self.dead = True


class Player(Entity):

    def __init__(self):
        Entity.__init__(self)
        self.surf = pygame.image.load('tiles\\blue.png')
        self.rect = self.surf.get_rect()
        self.blit_priority = 10
        self.impassable = True
        self.name = 'Player'
        self.team = 'Blue'
        self.attack_dmg_range = 1, 30
        game.objects.add_player_object(self)

    def player_move(self, direction):
        if self.dead:
            exit()

        movegrid = self.adj_grids[direction]

        for i in movegrid.objects:
            if i.team != self.team and i.team is not None:
                self.attack(i)
                game.next_turn()
                return

        if movegrid.impassable:
            return

        if self.on_grid.impassable:
            for i in self.on_grid.objects:
                if not i.impassable:
                    self.on_grid.impassable = False

        self.on_grid.objects.remove(self)
        movegrid.objects.append(self)
        self.rect.center = movegrid.rect.center
        self.grid_x = movegrid.grid_x
        self.grid_y = movegrid.grid_y

        if self.impassable:
            movegrid.impassable = True

        self.on_grid = movegrid
        self.find_adj_gridpoints()
        game.next_turn()

    def tick_input(self, events):
        for event in events:
            if event.type == KEYUP:
                if event.__dict__['key'] == 263:
                    self.player_move('topleft')
                if event.__dict__['key'] == 264:
                    self.player_move('top')
                if event.__dict__['key'] == 265:
                    self.player_move('topright')
                if event.__dict__['key'] == 260:
                    self.player_move('left')
                if event.__dict__['key'] == 261:
                    game.next_turn()
                if event.__dict__['key'] == 262:
                    self.player_move('right')
                if event.__dict__['key'] == 257:
                    self.player_move('bottomleft')
                if event.__dict__['key'] == 258:
                    self.player_move('bottom')
                if event.__dict__['key'] == 259:
                    self.player_move('bottomright')


class NPC(Entity):

    def __init__(self, name, color, team):
        Entity.__init__(self)
        self.surf = pygame.image.load(f'tiles\\{color}.png')
        self.rect = self.surf.get_rect()
        self.blit_priority = 10
        self.impassable = True
        self.team = team
        self.enemies = []
        self.current_target = None
        self.name = name
        self.attack_dmg_range = 1, 30
        self.fleeing = False
        game.objects.add_npc_object(self)

    def brain(self):
        for i in game.objects.all_players + game.objects.all_npcs:
            if i.team != self.team and i not in self.enemies:
                self.enemies.append(i)

        if not self.current_target:
            self.current_target = random.choice(self.enemies)

        if self.current_target.dead:
            self.current_target = None
            return

        if self.fleeing:
            path = self.pathfinding((self.current_target.grid_x,
                                     self.current_target.grid_y),
                                    (self.grid_x, self.grid_y),
                                    reverse=True)
            side_gui.message(f'{self.name} is fleeing to {path}!')
            self.move(path)
            return

        if self.health < 70:
            if random.randrange(3) == 0:
                self.fleeing = True

        for i in self.adj_grids.values():
            for obj in i.objects:
                if obj in self.enemies:
                    self.attack(obj)
                    return

        path = self.pathfinding((self.current_target.grid_x,
                                 self.current_target.grid_y),
                                (self.grid_x, self.grid_y))
        if not path:
            return
        self.move(path)

    def pathfinding(self, target_location, current_location, reverse=False):
        potentialdirs = ['topleft', 'top', 'topright', 'left', 'right', 'bottomleft', 'bottom', 'bottomright']
        direction = ''

        if target_location[1] < current_location[1]:
            direction += 'top'
        if target_location[1] > current_location[1]:
            direction += 'bottom'
        if target_location[0] < current_location[0]:
            direction += 'left'
        if target_location[0] > current_location[0]:
            direction += 'right'

        if self.adj_grids[direction].impassable:
            self.fleeing = False
            for i in self.adj_grids:
                if self.adj_grids.get(i).impassable:
                    potentialdirs.remove(i)
            if not potentialdirs:
                return
            return random.choice(potentialdirs)

        if reverse:
            potentialdirs.reverse()
            revdirs = potentialdirs
            potentialdirs.reverse()
            return revdirs[potentialdirs.index(direction)]

        return direction


class Wall(Entity):

    def __init__(self, walltype):
        Entity.__init__(self)
        wall_types = {
            'void wall': self.void_wall,
            'stone wall': self.stone_wall,
        }
        wall_types[walltype]()
        self.impassable = True
        game.objects.add_wall_object(self)

    def void_wall(self):
        self.surf = pygame.image.load('tiles\\void_wall.png')
        self.rect = self.surf.get_rect()

    def stone_wall(self):
        self.surf = pygame.image.load('tiles\\stone_wall.png')
        rnd = random.randrange(3)
        self.surf = pygame.transform.rotate(self.surf, 90 * rnd)
        self.rect = self.surf.get_rect()


class Tile(Entity):

    def __init__(self, tiletype):
        Entity.__init__(self)
        tile_types = {
            'grass': self.grass,
        }
        tile_types[tiletype]()
        game.objects.add_tile_object(self)

    def grass(self):
        self.surf = pygame.image.load('tiles\\grass.png')
        rnd = random.randrange(3)
        self.surf = pygame.transform.rotate(self.surf, 90*rnd)
        self.rect = self.surf.get_rect()


class Misc(Entity):

    def __init__(self, surf, rota=0):
        Entity.__init__(self)
        self.surf = surf
        self.rect = self.surf.get_rect()
        if rota:
            self.surf = pygame.transform.rotate(self.surf, rota)
        self.blit_priority = 1
        game.objects.add_basic_object(self)


class Camera:

    def __init__(self, following):
        self.camera_rect = pygame.Surface.get_rect(game.screen)
        self.following = following
        self.camera_rect.center = self.following.rect.center

    def update(self):
        self.camera_rect.center = self.following.rect.center


class SideGui:

    def __init__(self):
        self.surf = pygame.Surface((game.width/5, game.height))
        self.rect = self.surf.get_rect(left = int(game.width-game.width/5), bottom = game.height)
        self.active = False
        self.elements = []
        game.objects.add_gui(self)

    def message(self, text, color=white):
        msg = Text(text, 20, color, (0, game.height-50))
        self.elements.append(msg)
        for i in self.elements:
            if i.rect.centery < 60:
                del self.elements[self.elements.index(i)]
                del i
        try:
            for i in range(len(self.elements)-1):
                self.elements[i].rect.centery -= 20
        except KeyError:
            return


class Text:

    def __init__(self, text, size, color, pos):
        self.font = pygame.font.Font('Font\\Roboto-Black.ttf', size)
        self.surf = self.font.render(text, True, color)
        self.rect = self.surf.get_rect(topleft=pos)

if __name__ == '__main__':
    game = Game()
    game.setup()
    game.game_loop()