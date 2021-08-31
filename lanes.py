"""
Lanes module for Froggit

This module contains the lane classes for the Frogger game. The lanes are the vertical
slice that the frog goes through: grass, roads, water, and the exit hedge.

Each lane is like its own level. It has hazards (e.g. cars) that the frog has to make
it past.  Therefore, it is a lot easier to program frogger by breaking each level into
a bunch of lane objects (and this is exactly how the level files are organized).

You should think of each lane as a secondary subcontroller.  The level is a subcontroller
to app, but then that subcontroller is broken up into several other subcontrollers, one
for each lane.  That means that lanes need to have a traditional subcontroller set-up.
They need their own initializer, update, and draw methods.

There are potentially a lot of classes here -- one for each type of lane.  But this is
another place where using subclasses is going to help us A LOT.  Most of your code will
go into the Lane class.  All of the other classes will inherit from this class, and
you will only need to add a few additional methods.

If you are working on extra credit, you might want to add additional lanes (a beach lane?
a snow lane?). Any of those classes should go in this file.  However, if you need additional
obstacles for an existing lane, those go in models.py instead.  If you are going to write
extra classes and are now sure where they would go, ask on Piazza and we will answer.

Name: Jane Lee (jyl99)
Date: 12/19/2020
"""
from game2d import *
from consts import *
from models import *

# PRIMARY RULE: Lanes are not allowed to access anything in any level.py or app.py.
# They can only access models.py and const.py. If you need extra information from the
# level object (or the app), then it should be a parameter in your method.

class Lane(object):         # You are permitted to change the parent class if you wish
    """
    Parent class for an arbitrary lane.

    Lanes include grass, road, water, and the exit hedge.  We could write a class for
    each one of these four (and we will have classes for THREE of them).  But when you
    write the classes, you will discover a lot of repeated code.  That is the point of
    a subclass.  So this class will contain all of the code that lanes have in common,
    while the other classes will contain specialized code.

    Lanes should use the GTile class and to draw their background.  Each lane should be
    GRID_SIZE high and the length of the window wide.  You COULD make this class a
    subclass of GTile if you want.  This will make collisions easier.  However, it can
    make drawing really confusing because the Lane not only includes the tile but also
    all of the objects in the lane (cars, logs, etc.)
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # Attribute _laneDict: a dictionary of the given lane
    # Invariant: is a valid JSON dictionary for the game with lane objects

    # Attribute _width: width of lane
    # Invariant: is an int >= 0

    # Attribute _index: number of the lane from the bottom up
    # Invariant: is an int >= 0. Is the length of the dictionary lane key.

    # Attribute _objs: list of the obstacles in the lane in specific index
    # Invariant: is a list of GImage objects

    # Attribute _tile: object that allows for drawing of the lane
    # Invariant: is a GTile object of the lane

    # Attribute _safeFrog: contains the blue (safe) frogs in the exits
    # Precondition: is a list of GImage objects of FROG_SAFE images

    # Attribute _isnotsafe: determines whether the frog is safe or not on road
    # Precondition: is a bool


    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getHBDict(self):
        return self._hitboxdict

    def getTile(self):
        """
        Returns the Gtile object (a lane)
        """
        return self._tile

    def getObjs(self):
        """
        Returns the list of objects (logs/vehicles/lilypads) on the lane
        """
        return self._objs

    def getWidth(self):
        """
        Returns the width of the game window
        """
        return self._width

    def getSafeFrog(self):
        """
        Returns the list of safe (blue) frogs that have been drawn
        """
        return self._safeFrog

    # INITIALIZER TO SET LANE POSITION, BACKGROUND,AND OBJECTS
    def __init__(self,laneDict,width,index,hitbox):
        """
        Initializes the lane objects

        Parameter laneDict: is a dictionary that
        Precondition: is a valid dictionary for a lane object

        Parameter width: is the width of the game window
        Precondition: is an int >= 10*GRID_SIZE

        Paramter index: is the index of the lane in list of values for the
                        'lanes' key in the JSON dictionary for the given level
        Precondition: is an int >= 0 and int <= length of the list of values for
                        the 'lanes' key
        """
        self._hitboxdict = hitbox
        self._laneDict = laneDict
        self._width = width
        self._index = index
        self._objs = []
        self._objCreator(laneDict,index)
        self._tile = (GTile(left=0,width=self._width,height=GRID_SIZE,
            source=str(laneDict['type'])+'.png',bottom=GRID_SIZE*self._index))
        self._safeFrog = []
        self._isnotsafe = False

    # ADDITIONAL METHODS (DRAWING, COLLISIONS, MOVEMENT, ETC)
    def draw(self,view):
        """
        Draws the game objects to the view.

        Parameter view: The view window
        Precondition: view is a GView.
        """
        # Drawing the lanes
        self._tile.draw(view)
        for i in range(len(self._objs)):
            if self._objs[i] != []:
                self._objs[i].draw(view)

    def update(self,dt,buff=None,frog=None):
        """
        This method should move all of the obstacles in the lane.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)

        Paramter buff: buffer value that keeps the obstacles loop over without
                        shortening the gap between them
        Precondition: is a number or None

        Parameter frog: the frog that is moving
        Precondition: is a valid Frog (class) object or None
        """
        if 'speed' in self._laneDict:
            for obstacle in self._objs:
                obstacle.x += dt*self._laneDict['speed']
                if frog!= None:
                    frog.x += dt*self._laneDict['speed']
                if buff!= None:
                    if self._laneDict['speed'] < 0:
                        d = obstacle.x - (-buff*GRID_SIZE)
                        if obstacle.x < -buff*GRID_SIZE:
                            obstacle.x = self.getWidth() + buff*GRID_SIZE - d
                    if self._laneDict['speed'] > 0:
                        d = obstacle.x - (self.getWidth()+buff*GRID_SIZE)
                        if obstacle.x > self.getWidth() +buff*GRID_SIZE:
                            obstacle.x = -buff*GRID_SIZE + d

    def check(self,frog,last):
        """
        Method that checks if the user-controlled frog is running into an exit
        or hedge. If the frog is entering a hedge, it returns True. If the frog
        is running into a lilypad (exit) it returns False while also modifying
        the dictionary that checks if an exit is already occupied. If the frog
        is running into an opening (open) on the hedge, it returns False.

        This method also makes sure that the frog does not enter any of the
        exits from the West, East, North side – the only opening is via the
        South entrance.

        Parameter frog: the frog that is moving
        Precondition: is a valid Frog (class) object

        Parameter last: the arrow that was just clicked by the user
        Precondition: is a valid string ('up', 'down', 'left', or 'right')
        """
        # if isinstance(frog,GObject):
        if self.getTile().collides(frog):
            exits = self.getExitDict()

            # Checks if frog is running into a lilypad
            for lily in exits:
                if lily.source == 'open.png':
                    if lily.contains((frog.x,frog.y)):
                        return False
                if lily.source == 'exit.png':
                    if lily.contains((frog.x,frog.y)):
                        if self.getExitDict()[lily] == False:
                            if last == 'up':
                                self._safeFrog.append(GImage(x=lily.x,y=lily.y,source=FROG_SAFE))
                                return False
            # Returns True if frog is running into a hedge
            return True

    def isNotSafe(self,frog):
        """
        Is a method that determines whether the frog is safe on the road or not.
        If the frog crashes into a vehicle, the method returns True. Else, False

        Parameter frog: the frog that is moving
        Precondition: is a valid Frog (class) object or None
        """
        self._isnotsafe = False
        for car in self._objs:
            if isinstance(frog,GObject):
                if car.collides(frog):
                    self._isnotsafe = True
        return self._isnotsafe

    # Hidden method
    def _objCreator(self,laneDict,index):
        """
        Helper function to initialize the objects (obstacles) in each of the
        lanes

        Parameter laneDict: dictionary of
        Precondition: is a valid lane dictionary containing type (and obstacles)

        Parameter index: is the index of the lane from the bottom, up
        Precondition: is an int >= 0
        """
        if 'objects' in laneDict:
            for x in range(len(laneDict['objects'])):
                pX = (laneDict['objects'][x]['position']+0.5)*GRID_SIZE
                image = GImage(x=pX,y=GRID_SIZE*index+GRID_SIZE/2,
                        source=str(laneDict['objects'][x]['type'])+'.png')
                if 'speed' in laneDict and laneDict['speed'] < 0:
                    image.angle=180
                self._objs.append(image)


class Grass(Lane):                           # We recommend AGAINST changing this one
    """
    A class representing a 'safe' grass area.

    You will NOT need to actually do anything in this class.  You will only do anything
    with this class if you are adding additional features like a snake in the grass
    (which the original Frogger does on higher difficulties).
    """
    def __init__(self,laneDict,width,index,hitbox):
        """
        Initializes the exit hedge

        Parameter laneDict: is a dictionary that
        Precondition: is a valid dictionary for a lane object

        Parameter width: is the width of the game window
        Precondition: is an int >= 10*GRID_SIZE

        Paramter index: is the index of the lane in list of values for the
                        'lanes' key in the JSON dictionary for the given level
        Precondition: is an int >= 0 and int <= length of the list of values for
                        the 'lanes' key
        """
        super().__init__(laneDict, width, index, hitbox)


class Road(Lane):                           # We recommend AGAINST changing this one
    """
    A class representing a roadway with cars.

    If you implement Lane correctly, you do really need many methods here (not even an
    initializer) as this class will inherit everything.  However, roads are different
    than other lanes as they have cars that can kill the frog. Therefore, this class
    does need a method to tell whether or not the frog is safe.
    """
    def __init__(self,laneDict,width,index, hitbox):
        """
        Initializes the exit hedge

        Parameter laneDict: is a dictionary that
        Precondition: is a valid dictionary for a lane object

        Parameter width: is the width of the game window
        Precondition: is an int >= 10*GRID_SIZE

        Paramter index: is the index of the lane in list of values for the
                        'lanes' key in the JSON dictionary for the given level
        Precondition: is an int >= 0 and int <= length of the list of values for
                        the 'lanes' key
        """
        super().__init__(laneDict, width, index, hitbox)


class Water(Lane):
    """
    A class representing a waterway with logs.

    If you implement Lane correctly, you do really need many methods here (not even an
    initializer) as this class will inherit everything.  However, water is very different
    because it is quite hazardous. The frog will die in water unless the (x,y) position
    of the frog (its center) is contained inside of a log. Therefore, this class needs a
    method to tell whether or not the frog is safe.

    In addition, the logs move the frog. If the frog is currently in this lane, then the
    frog moves at the same rate as all of the logs.
    """
    def __init__(self,laneDict,width,index, hitbox):
        """
        Initializes the exit hedge

        Parameter laneDict: is a dictionary that
        Precondition: is a valid dictionary for a lane object

        Parameter width: is the width of the game window
        Precondition: is an int >= 10*GRID_SIZE

        Paramter index: is the index of the lane in list of values for the
                        'lanes' key in the JSON dictionary for the given level
        Precondition: is an int >= 0 and int <= length of the list of values for
                        the 'lanes' key
        """
        super().__init__(laneDict, width, index, hitbox)

    def onLog(self,frog):
        """
        Method that returns True if the frog is sitting inside a log

        Parameter frog: the frog that the game player is moving around
        Precondition: is a valid GImage for the game
        """
        if frog != None:
            logs = self.getObjs()
            for log in logs:
                if log.contains((frog.x,frog.y)) == True:
                    return True

class Hedge(Lane):
    """
    A class representing the exit hedge.

    This class is a subclass of lane because it does want to use a lot of the features
    of that class. But there is a lot more going on with this class, and so it needs
    several more methods.  First of all, hedges are the win condition. They contain exit
    objects (which the frog is trying to reach). When a frog reaches the exit, it needs
    to be replaced by the blue frog image and that exit is now "taken", never to be used
    again.

    That means this class needs methods to determine whether or not an exit is taken.
    It also need to take the (x,y) position of the frog and use that to determine which
    exit (if any) the frog has reached. Finally, it needs a method to determine if there
    are any available exits at all; once they are taken the game is over.

    These exit methods will require several additional attributes. That means this class
    (unlike Road and Water) will need an initializer. Remember to user super() to combine
    it with the initializer for the Lane.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    #
    # Attribute _exits: list of exits on the hedges
    # Invariant: a nonempty list of GImage objects
    #
    # Attribute _exitDict: A dictionary that places the key as the exit GImage
    #           object and the value as True (if the frog lands in the exit) or
    #           or False (if the frog has not yet landed in the exit, in which
    #           case the user can still move the frog into the specific exit)
    # Invariant: is a dictionary where type(key) == GImage and type(value)==bool
    #
    # Attribute _occList: Accumulates a list of bool determining whether a safe
    #                   frog is already in the exit
    # Invariant: is a list of bool

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getExits(self):
        """
        Returns the list of exits
        """
        return self._exits

    def getExitDict(self):
        """
        Returns the exit dictionary that tells which exits have already been
        occupied
        """
        return self._exitDict

    # INITIALIZER TO SET ADDITIONAL EXIT INFORMATION
    def __init__(self,laneDict,width,index, hitbox):
        """
        Initializes the exit hedge

        Parameter laneDict: is a dictionary that
        Precondition: is a valid dictionary for a lane object

        Parameter width: is the width of the game window
        Precondition: is an int >= 10*GRID_SIZE

        Paramter index: is the index of the lane in list of values for the
                        'lanes' key in the JSON dictionary for the given level
        Precondition: is an int >= 0 and int <= length of the list of values for
                        the 'lanes' key
        """
        super().__init__(laneDict, width, index, hitbox)
        self._exits = self.getObjs()
        self._exitDict = self._safeDict(self.getObjs())
        self._occList = []

    # ANY ADDITIONAL METHODS
    def allOccupied(self):
        """
        Method that determines whether all the exits in the hedge are all
        occupied. Returns True if all the exits are occupied by blue frog.
        If not, returns False.
        """
        self._occList = []
        for key in self._exitDict:
            if key.source == 'exit.png':
                if self._exitDict[key] == False:
                    self._occList.append(False)
        if False in self._occList:
            return False
        else:
            return True

    def isInExit(self,frog):
        """
        This is a method that can tell whether a frog has landed in a
        liliypad (an exit).

        Parameter frog: the frog that is moving
        Precondition: is a valid Frog (class) object or None
        """
        for i in range(len(self._exits)):
            if self._exits[i].contains((frog.x,frog.y)):
                if self._exits[i].source == 'exit.png':
                    self._exitDict[self._exits[i]] = True
                    return True

    def alrOcc(self,frog):
        """
        Method that returns False if a blue frog is already occupying a lilypad.
        Else, returns True

        Parameter frog: the frog that is moving
        Precondition: is a valid Frog (class) object or None
        """
        for i in range(len(self._exits)):
            if (self._exitDict[self._exits[i]] == True and
                        self._exits[i].contains((frog.x,frog.y))):
                return True
            elif (self._exitDict[self._exits[i]] == False and
                        self._exits[i].contains((frog.x,frog.y))):
                return False

# IF YOU NEED ADDITIONAL LANE CLASSES, THEY GO HERE
    def _safeDict(self,exits):
        """
        Helper function that creates a dictionary of exits that meet the
        precondition of _exitDict

        Parameter exits: a list of exits on the Hedge
        Precondition: is a nonempty list of GImage objects
        """
        a = {}
        for lily in exits:
            a[lily] = False
        return a
