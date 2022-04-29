import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 4
TILE_SCALING = 4
COIN_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Player starting position
PLAYER_START_X = 64
PLAYER_START_Y = 500

# Layer Names from our TileMap
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"

class Game(arcade.Window):
    """Main game application."""

    def __init__(self):
        """Initialize the game"""

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.tilemap = None
        self.scene = None
        self.player = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.debug_text_y = 10

        self.score = 0
        self.level = 1
        self.god_mode = False

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

        arcade.enable_timings()

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        
        # Map name 
        # map_name = f":resources:tiled_maps/map2_level_{self.level}.json"\
        map_name = r"src\assets\tilemaps\Basic Tilemap.tmx"

        # Layer specific options for the tilemap
        layer_options  = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True
            },
            LAYER_NAME_DONT_TOUCH: {
                "use_spatial_hash": True
            }
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        image_source = "src/assets/images/player.png"
        self.player = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player)

        # --- Load in a map from the tiled editor ---

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=GRAVITY, walls=self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_draw(self):
        """Render the screen."""
        
        # Clear the screen to the background color
        self.clear()

        # Activate our Camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw(pixelated=True)

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()
        
        # Draw our score on the screen, scrolling it with the viewport
        # Also draw some debug stuff
        self.reset_debug_text()
        self.debug_text("Score", self.score)
        self.debug_text("FPS", arcade.get_fps())
        self.debug_text("God Mode", self.god_mode)

        self.debug_text("Right Key", self.right_pressed)
        self.debug_text("Left Key", self.left_pressed)
        self.debug_text("Up Key", self.up_pressed)
        self.debug_text("Down Key", self.down_pressed)
        self.debug_text("Change x", self.player.change_x)
        self.debug_text("Change y", self.player.change_y)
        self.debug_text("Can Jump", self.physics_engine.can_jump())
    
    def debug_text(self, item, value):
        text = f"{item}: {value}"
        arcade.draw_text(text=text, start_x=10, start_y=self.debug_text_y, color=arcade.csscolor.WHITE, font_size=18)
        self.debug_text_y += 30

    def reset_debug_text(self):
        self.debug_text_y = 10

    def update_player_speed(self):
        """Calculate speed based on the keys pressed."""
        if self.god_mode:
            if self.up_pressed and not self.down_pressed:
                self.player.change_y = PLAYER_MOVEMENT_SPEED
            elif self.down_pressed and not self.up_pressed:
                self.player.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            if self.up_pressed:
                if self.physics_engine.can_jump():
                    self.player.change_y = PLAYER_JUMP_SPEED
                    arcade.play_sound(self.jump_sound)

        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED

        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_MOVEMENT_SPEED

        else:
            self.player.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
            
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

        elif key == arcade.key.G:
            self.god_mode = not self.god_mode

    def on_key_release(self, key, modifers):
        """Called when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
            
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()

    def center_camera_to_player(self):
        screen_center_x = self.player.center_x -(self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        # Dont let camera travel past 0
        # if screen_center_x < 0: screen_center_x = 0
        if screen_center_y < 0: screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic."""

        # If god mode is enabled, set gravity to 0. This will allow the player to fly around.
        if self.god_mode:
            self.physics_engine.gravity_constant = 0
        else:
            self.physics_engine.gravity_constant = GRAVITY

        # Move the player with the physics engine
        self.physics_engine.update()

        # See if we hit the coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])

        # Loop through each coin if we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        # Did the player fall of the map?
        if self.player.center_y < -100:
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y

            arcade.play_sound(self.game_over)

        # Did the player touch something they sould not
        if arcade.check_for_collision_with_list(self.player, self.scene[LAYER_NAME_DONT_TOUCH]):
            self.player.change_x = 0
            self.player.change_y = 0
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y

            arcade.play_sound(self.game_over)

        # See if the user got to the end of the level
        if self.player.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1

            # Load the next level
            self.setup()

        # Position the camera
        self.center_camera_to_player()
        

def main():
    """Main function."""
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()