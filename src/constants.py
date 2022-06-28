"""Just a way to store constants globally across files"""

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"
TARGET_FPS = 60
CAMERA_SPEED = 0.15  # The speed at which the camera moves to the player

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 4
TILE_SCALING = 4
COIN_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 15
MAX_SPEED = 5  # Speed limit
ACCELERATION_RATE = 0.7  # How fast we accelearte
FRICTION = 0.7  # How fast to slow down after we let off the key
MAX_JUMP_COUNT = 8
JUMP_PAD_BOOST_SPEED = 27

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Player starting position
PLAYER_START_X = 64
PLAYER_START_Y = 500

# Layer Names from our TileMap
PLATFORMS_LAYER = "Platforms"
MOVING_PLATFORMS_LAYER = "Moving Platforms"
LADDERS_LAYER = "Ladders"
COINS_LAYER = "Coins"
#FOREGROUND_LAYER = "Foreground"
#BACKGROUND_LAYER = "Background"
DANGER_LAYER = "Dangers"
GOAL_LAYER = "Goal"
ENEMIES_LAYER = "Enemies"
JUMP_PADS_LAYER = "Jump Pads"
PLAYER_LAYER = "Player"
OBJECTS_LAYER = "Objects"
ALL_LAYERS = (PLATFORMS_LAYER, MOVING_PLATFORMS_LAYER, LADDERS_LAYER, COINS_LAYER, DANGER_LAYER, GOAL_LAYER, 
              ENEMIES_LAYER, JUMP_PADS_LAYER, PLAYER_LAYER)

TYPES_TO_PLAYER = {
    ("ladder",): LADDERS_LAYER,
    ("coin",): COINS_LAYER,
    ("lava",): DANGER_LAYER,
    ("goal",): GOAL_LAYER,
    ("blue_jump_pad", "green_jump_pad"): JUMP_PADS_LAYER
}