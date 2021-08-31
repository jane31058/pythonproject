"""
Subcontroller module for Froggit

This module contains the subcontroller to manage a single level in the Froggit game.
Instances of Level represent a single game, read from a JSON.  Whenever you load a new
level, you are expected to make a new instance of this class.

The subcontroller Level manages the frog and all of the obstacles. However, those are
all defined in models.py.  The only thing in this class is the level class and all of
the individual lanes.

This module should not contain any more classes than Levels. If you need a new class,
it should either go in the lanes.py module or the models.py module.

Name: Jane Lee (jyl99)
Date: 12/19/2020
"""
from game2d import *
from consts import *
from lanes  import *
from models import *

# PRIMARY RULE: Level can only access attributes in models.py or lanes.py using getters
# and setters. Level is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Level(object):
    """
    This class controls a single level of Froggit.

    This subcontroller has a reference to the frog and the individual lanes.  However,
    it does not directly store any information about the contents of a lane (e.g. the
    cars, logs, or other items in each lane). That information is stored inside of the
    individual lane objects.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lesson 27 for an example.  This class will be similar to that
    one in many ways.

    All attributes of this class are to be hidden.  No attribute should be accessed
    without going through a getter/setter first.  However, just because you have an
    attribute does not mean that you have to have a getter for it.  For example, the
    Froggit app probably never needs to access the attribute for the Frog object, so
    there is no need for a getter.

    The one thing you DO need a getter for is the width and height.  The width and height
    of a level is different than the default width and height and the window needs to
    resize to match.  That resizing is done in the Froggit app, and so it needs to access
    these values in the level.  The height value should include one extra grid square
    to suppose the number of lives meter.
    """

    # LIST ALL HIDDEN ATTRIBUTES HERE
    # Attribute _JSON: !
    # Invariant: Is a valid dictionary for the game
    #
    # Attribute _lanes: is a list lanes
    # Invariant: type(_lanes) == list & inside the list are Lane objects
    #
    # Attribute _width: is the width of the game window
    # Invariant: is an int >= 10*GRID_SIZE
    #
    # Attribute _height: is the height of the game window
    # Invariant: is an int >= 8*GRID_SIZE
    #
    # Attribute _cooldown: cooldown period
    # Invariant: is a float
    #
    # Attribute _lastarrow:
    # Invariant: is == None or == ('up' or 'down' or 'left' or 'right')
    #
    # Attribute _dead: is an indicator of whether the frog died or not
    # Invariant: is a boolean
    #
    # Attribute _frog: is the frog that the game player moves
    # Invariant: is a Frog (class) object
    #
    # Attribute _frogH: represents the remaining number of lives
    # Invariant: is a list of GImage objects
    #
    # Attribute _win: Determines whether the player has won the round
    # Invariant: is a bool
    #
    # Attribute _gamewin: Determines whether the player has won the game
    # Invariant: is a bool
    #
    # Attribute self._hedgelns: represents the total number of hedge lanes
    # Invariant: is an int >= 0
    #
    # Attribute _occupied: represents how many hedges are fully occupied by
    #                      blue (safe) frogs
    # Invariant: is an int >= 0

    # Attribute _hitbox: a dictionary of all the image hitbox sizes
    # Invariant: type(_hitbox) == dict

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getFrog(self):
        """
        Returns the GImage objects of the moving frog
        """
        return self._frog

    def getDeath(self):
        """
        Returns a bool indicating whether frog is dead or not
        """
        return self._dead

    def SetDeath(self,value=False):
        """
        Sets the state of death of the frog

        Parameter value: boolean expression that determines whether the frog is
        dead/alive
        Precondition: is a bool
        """
        self._dead = value

    def getFrogH(self):
        """
        Returns a list of GImage objects representing the "lives"
        """
        return self._frogH

    def setFrogH(self,value):
        """
        Sets the number of lives to the desired amount (decreasing since one
        life is taken away every time the user dies)

        Parameter value: represents the "lives"
        Precondition: a list of frogH GImages
        """
        self._frogH = value

    def getWin(self):
        """
        Returns whether the user has won the game
        """
        return self._win

    def setWin(self,value=False):
        """
        Sets the win attribute to the desired boolean

        Parameter value: determines whether the state of "win" is T/F
        Precondition: is a bool
        """
        self._win = value

    def getGameWin(self):
        """
        Returns whether the user has won the entire level (filled all the exits)
        """
        return self._gamewin

    # INITIALIZER (standard form) TO CREATE THE FROG AND LANES
    def __init__(self,JSON,hitbox,width,height):
        """
        Initializes the level by loading the JSON dictionary to set the
        "playing field" including the road, grass, water, hedge, and all other
        moving objects.

        Parameter JSON: a JSON dictionary containing all information about level
        Precondition: is a valid JSON level dictionary

        Parameter width: is the width of the game window
        Precondition: is an int >= 10*GRID_SIZE

        Parameter height: is the height of the game window
        Precondition: is an int >= 8*GRID_SIZE
        """
        assert type(JSON) == dict
        assert type(width) == int and width >= 10*GRID_SIZE
        assert type(height) == int and height >= 8*GRID_SIZE

        # Dictionary of the loaded level
        self._JSON = JSON
        self._hitbox = hitbox
        # Width and height of the Level window
        self._width = width
        self._height = height

        # List of composite objects of Lane
        self._lanes = []
        self._appending()

        self._cooldown = 0
        self._lastarrow = None
        self._dead = False
        self._win = False
        self._gamewin = False
        self._hedgelns = 0
        self._occupied = 0

        self._frog = Frog(x = self._JSON['start'][0]*GRID_SIZE+GRID_SIZE/2,
                        y = self._JSON['start'][1]*GRID_SIZE+GRID_SIZE/2)

        # Frog lives represented by frog heads
        self._frogH = self._frogHead()

    # UPDATE METHOD TO MOVE THE FROG AND UPDATE ALL OF THE LANES
    def update(self,dt,input):
        """
        Updates the movement of the frog of the game

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)

        Paramter input: determines which key has been pressed down
        Precondition: is an inherited GInput attribute
        """
        if self._cooldown > 0:
            self._cooldown -= dt
        elif self._cooldown <= 0:
            self._movingFrog(input)
            self._movingundo(self._lanes,self._frog,self._lastarrow)
        self._movingObjects(dt,self._lanes)
        self._hedgelns = 0
        self._occupied = 0
        for ln in self._lanes:
            if isinstance(ln,Hedge):
                self._hedgelns += 1
                if ln.allOccupied():
                    self._occupied += 1
            if isinstance(ln,Road) and ln.isNotSafe(self._frog):
                self._frog = None
                self._dead = True
        for index in range(len(self._lanes)):
            ln = self._lanes[index]
            if isinstance(ln,Water) and self._frog != None:
                if ln.onLog(self._frog):
                    self._frog.x += dt*self._JSON['lanes'][index]['speed']
                    if self._frog.left < 0 or self._frog.right > self._width:
                        self._frog = None
                        self._dead = True
                elif ln.getTile().contains((self._frog.x,self._frog.y)):
                    self._frog = None
                    self._dead = True
        if self._hedgelns == self._occupied:
            if ln.allOccupied():
                self._gamewin = True

    # DRAW METHOD TO DRAW THE FROG AND THE INDIVIDUAL LANES
    def draw(self,view):
        """
        Draws the game objects to the view.

        Parameter view: The view window
        Precondition: view is a GView.
        """
        # Drawing the lanes
        for lanes in self._lanes:
            lanes.draw(view)
        # Drawing the frog
        if self._frog != None:
            self._frog.draw(view)

        # Drawing the frog head
        for i in range(len(self._frogH)):
            self._frogH[i].draw(view)

        for lanes in self._lanes:
            if isinstance(lanes,Hedge):
                for frog in lanes.getSafeFrog():
                    if frog != None and lanes.alrOcc(frog):
                        frog.draw(view)

    def setFrog(self):
        """
        Resets the frog to the original position of the game once
        the frog dies/reaches an exit
        """
        self._frog = Frog(x = self._JSON['start'][0]*GRID_SIZE+GRID_SIZE/2,
                        y = self._JSON['start'][1]*GRID_SIZE+GRID_SIZE/2)

    # ANY NECESSARY HELPERS (SHOULD BE HIDDEN)
    def _appending(self):
        """
        This is a helper function for initializing all the lanes of the game
        """
        for index in range(len(self._JSON['lanes'])):
            r = self._JSON['lanes'][index]
            if r['type'] == 'hedge':
                self._lanes.append(Hedge(r,self._width,index,self._hitbox))
            if r['type'] == 'grass':
                self._lanes.append(Grass(r,self._width,index,self._hitbox))
            if r['type'] == 'road':
                self._lanes.append(Road(r,self._width,index,self._hitbox))
            if r['type'] == 'water':
                self._lanes.append(Water(r,self._width,index,self._hitbox))

    def _frogHead(self):
        """
        Helper function for creating a list of lives represented by GImages
        of frog heads
        """
        heads = []
        left = self._width - GRID_SIZE*3
        top = self._height
        heads.append(GLabel(text='LIVES:',right=left,y=top-GRID_SIZE/2,
                linecolor='dark green',font_name=ALLOY_FONT,font_size=ALLOY_SMALL))
        for i in range(3):
            p = GImage(source=FROG_HEAD,width=GRID_SIZE,height=GRID_SIZE,
                left=left,top=top)
            heads.append(p)
            left = left + GRID_SIZE
        return heads

    def _movingFrog(self,input):
        """
        Is a helper function for moving the frog based on whatever key was
        pressed by the user

        Paramter input: determines which key has been pressed down
        Precondition: is an inherited GInput attribute
        """
        # Checking key
        up = input.is_key_down('up')
        down = input.is_key_down('down')
        left = input.is_key_down('left')
        right = input.is_key_down('right')

        # Movements
        if up and not down and not right and not left:
            self._lastarrow = 'up'
            self._frog.angle = FROG_NORTH
            if self._frog.top < (self._height - GRID_SIZE*2):
                self._frog.y += GRID_SIZE
                self._cooldown = FROG_SPEED
        if down and not up and not right and not left:
            self._lastarrow = 'down'
            self._frog.angle = FROG_SOUTH
            if self._frog.bottom > GRID_SIZE:
                self._frog.y -= GRID_SIZE
                self._cooldown = FROG_SPEED
        if left and not right and not up and not down:
            self._lastarrow = 'left'
            self._frog.angle = FROG_WEST
            if self._frog.left > GRID_SIZE:
                self._frog.x -= GRID_SIZE
                self._cooldown = FROG_SPEED
        if right and not left and not up and not down:
            self._lastarrow = 'right'
            self._frog.angle = FROG_EAST
            if self._frog.right < self._width - GRID_SIZE:
                self._frog.x += GRID_SIZE
                self._cooldown = FROG_SPEED

    def _movingundo(self,lanes,frog,lastarrow):
        """
        Helper function for undoing the movement of the frog if the frog is
        crashing into a hedge.

        Parameter lanes: is a list of lanes of the game
        Precondition: is a list of Lane objects (including subclass)

        Parameter frog: the frog that is moving
        Precondition: is a valid Frog (class) object or None

        Parameter lastarrow: the arrow that was just clicked by the user
        Precondition: is a valid string ('up', 'down', 'left', or 'right')
        """
        for ln in lanes:
            if isinstance(ln,Hedge):
                if ln.check(frog,lastarrow):
                # Moves back a step if the frog is stepping into a hedge
                    if lastarrow == 'up':
                        frog.y -= GRID_SIZE
                    if lastarrow == 'down':
                        frog.y += GRID_SIZE
                    if lastarrow == 'left':
                        frog.x += GRID_SIZE
                    if lastarrow == 'right':
                        frog.x -= GRID_SIZE
                if  ln.alrOcc(frog):
                    if lastarrow == 'up':
                        frog.y -= GRID_SIZE
                    if lastarrow == 'down':
                        frog.y += GRID_SIZE
                    if lastarrow == 'left':
                        frog.x += GRID_SIZE
                    if lastarrow == 'right':
                        frog.x -= GRID_SIZE
                if not ln.check(frog,lastarrow) and ln.isInExit(frog):
                    self._frog = None
                    self._win = True

    def _movingObjects(self,dt,lanes):
        """
        Helper function for moving the objects in the update function

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)

        Parameter lanes: List of lanes in the game
        Precondition: Is a valid, non-empty list of Lane objects (including the
        subclasses)
        """
        for ln in lanes:
            buff = 0
            for objs in ln.getObjs():
                if objs.width > buff:
                    buff = objs.width/GRID_SIZE
            ln.update(dt,buff)
