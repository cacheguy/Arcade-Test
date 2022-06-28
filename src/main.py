import arcade
import tkinter as tk
from pyglet import clock
from math import floor
from time import sleep

from player import PlayerSprite, RobotEnemySprite
from constants import *
import sounds

# TODO Update all libraries (especially arcade)

class UknownEnemyError(Exception): pass


class UknownTileTypeError(Exception): pass


class Game(arcade.Window):
    """Main game application."""

    def __init__(self):
        """Initialize the game"""

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, center_window=True)

        self.dt = 0
        self.fps = 0
        self.tilemap = None
        self.scene = None
        self.player = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.draw_debug_text = True
        self.debug_text_y = 10
        self.moved_camera = False
        self.was_touching_jump_pads: list[arcade.Sprite] = list()

        self.score = 0
        self.level = 1
        self.god_mode = False

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        #self.set_update_rate(1/500)

    def setup(self):
        """Set up the game here. Call this method to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        
        # Map name 
        map_name = r"src\assets\tilemap_project\tilemaps\basic_tilemap_2.tmx"

        # Layer specific options for the tilemap
        layer_options = {
            PLATFORMS_LAYER: {
                "use_spatial_hash": True
            },
            MOVING_PLATFORMS_LAYER: {
                "use_spatial_hash": False
            },
            OBJECTS_LAYER: {
                "use_spatial_hash": True
            },
            ENEMIES_LAYER: {
                "use_spatial_hash": False
            }
        }

        # Load in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.scene.add_sprite_list(LADDERS_LAYER, True)
        self.scene.add_sprite_list(COINS_LAYER, True)
        self.scene.add_sprite_list(DANGER_LAYER, True)
        self.scene.add_sprite_list(GOAL_LAYER, True)
        self.scene.add_sprite_list(JUMP_PADS_LAYER, True)
        self.scene.add_sprite_list(PLAYER_LAYER, False)

        for tile in self.scene[OBJECTS_LAYER]:
            try:
                ttype = tile.properties["type"]
            except KeyError:
                raise UknownTileTypeError()
            for key in TYPES_TO_PLAYER.keys():
                if ttype in key:
                    self.scene.add_sprite(name=TYPES_TO_PLAYER[key], sprite=tile)
        
        self.scene.remove_sprite_list_by_name(OBJECTS_LAYER)

        # Set up the player, specifically placing it at these coordinates.
        self.player = PlayerSprite()
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.scene.add_sprite(PLAYER_LAYER, self.player)

        # Add enemies
        enemies_layer = self.tile_map.object_lists[ENEMIES_LAYER]

        for enemy_object in enemies_layer:
            cartesian = self.tile_map.get_cartesian(*enemy_object.shape)
            enemy_type = enemy_object.properties["type"]
            if enemy_type == "robot":
                enemy = RobotEnemySprite()
            else:
                raise UknownEnemyError(f"Unknown enemy type: {enemy_type}.")

            enemy.center_x = floor(cartesian[0] * self.tile_map.tile_width * TILE_SCALING)
            enemy.center_y = floor((cartesian[1] + 1) * self.tile_map.tile_height * TILE_SCALING)

            if "boundary_left" in enemy_object.properties:
                enemy.boundary_left = enemy_object.properties["boundary_left"] * TILE_SCALING
            if "boundary_right" in enemy_object.properties:
                enemy.boundary_right = enemy_object.properties["boundary_right"] * TILE_SCALING
            if "change_x" in enemy_object.properties:
                enemy.change_x = enemy_object.properties["change_x"]

            self.scene.add_sprite(ENEMIES_LAYER, enemy)

        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, 
            gravity_constant=GRAVITY, 
            walls=self.scene[PLATFORMS_LAYER], 
            platforms=self.scene[MOVING_PLATFORMS_LAYER],
            ladders=self.scene[LADDERS_LAYER]
        )
        self.player.register_one_physics_engine(self.physics_engine)

        self.score = 0

    def on_draw(self):
        """Clear, then render the screen."""
        
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
        self.debug_text("FPS", self.fps)
        if self.draw_debug_text:
            self.debug_text("Score", self.score)
            self.debug_text("God Mode", self.god_mode)

            # self.debug_text("Right Key", self.player.right_pressed)
            # self.debug_text("Left Key", self.player.left_pressed)
            # self.debug_text("Up Key", self.player.up_pressed)
            # self.debug_text("Down Key", self.player.down_pressed)
            # self.debug_text("Player y", self.player.center_y)
            # self.debug_text("Player x", self.player.center_x)
            self.debug_text("Change y", self.player.change_y)
            # self.debug_text("Change x", self.player.change_x)
            self.debug_text("Can Jump", self.physics_engine.can_jump())
            self.debug_text("Stop Jump", self.player.stop_jump)
            self.debug_text("Jump Count", self.player.jump_count)
            # self.debug_text("Was Touching Jump Pads", self.was_touching_jump_pads)
    
    def debug_text(self, item, value):
        """Adds debug text to the top of the previous debug text."""
        text = f"{item}: {value}"
        arcade.draw_text(text=text, start_x=10, start_y=self.debug_text_y, color=arcade.csscolor.WHITE, font_size=18)
        self.debug_text_y += 30

    def reset_debug_text(self):
        """Resets the debug text's position. You should call this every frame before you call self.debug_text()"""
        self.debug_text_y = 10
      
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        elif key == arcade.key.G:
            self.god_mode = not self.god_mode

        elif key == arcade.key.F:
            self.draw_debug_text = not self.draw_debug_text

        elif key == arcade.key.Q:
            arcade.exit()

    def on_key_release(self, key, modifers):
        """Called when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def center_camera_to_player(self, camera_speed: float):
        """Moved the camera to the player, specifically, the player's center position.

        If self.moved_camera equals True, this method will do nothing. In order for it to work, you must reset
        self.moved_camera to False.

        camera_speed is the speed in which the camera moves to the player. It is passed to the arcade.Camera.move_to()
        function
        """
        if self.moved_camera:
            return
        screen_center_x = self.player.center_x - self.camera.viewport_width / 2
        screen_center_y = self.player.center_y - self.camera.viewport_height / 2

        # Dont let camera travel past 0
        #if screen_center_x < 0: screen_center_x = 0
        #if screen_center_y < 0: screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered, speed=camera_speed)
        self.moved_camera = True

    def kill_player(self):
        """Resets the player's position and kills the player."""
        self.player.stop()
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        sounds.game_over_sound.play()
        # We want the camera to immediately arrive to the player, not slowly glide to the player
        # So, we set camera_speed to 1.0 for that
        self.center_camera_to_player(camera_speed=1.0)

    def check_player_collisions(self, spritelist_name: str):
        hit_list = arcade.check_for_collision_with_list(self.player, self.scene[spritelist_name])
        if hit_list:
            if spritelist_name == COINS_LAYER:
                # Better to do this than to play a sound for every single coin
                sounds.collect_coin_sound.play()
                for coin in hit_list:
                    coin.remove_from_sprite_lists()
                    self.score += 1
            elif spritelist_name == DANGER_LAYER:
                if hit_list:
                    self.kill_player()
            elif spritelist_name == GOAL_LAYER:
                # Advance to the next level
                self.level += 1
                # Load the next level
                self.setup()
                sounds.goal_sound.play()
            elif spritelist_name == JUMP_PADS_LAYER:
                for jump_pad in hit_list:
                    if not jump_pad in self.was_touching_jump_pads:
                        # This part might be confusing, so let me explain.
                        # For consistency, we want the player to jump FROM THE TOP of the jump pad, instead of from
                        # their current position.
                        # However, each type of jump pad has different heights.
                        # This means the player will jump at a different height, because it will jump from a different 
                        # position, due to the different jump pad heights.
                        # So, using this piece of code, we can get the height of the tile of the jump pad (which is 
                        # always consistent), instead of the height of the jump pad itself.
                        # It's not that big of a problem, but it helps to have a solution.
                        jump_pad_cartesian_y = (self.tile_map.get_cartesian(jump_pad.center_x, jump_pad.center_y))[1]
                        self.player.bottom = jump_pad_cartesian_y * GRID_PIXEL_SIZE
                        self.player.change_y = JUMP_PAD_BOOST_SPEED
                        sounds.jump_pad_sound.play()
                        self.was_touching_jump_pads.append(jump_pad)

    def on_update(self, delta_time):
        """Movement and game logic."""
        self.dt = delta_time * TARGET_FPS
        self.fps = 1 / delta_time
        self.moved_camera = False

        # If god mode is enabled, set gravity to 0. This will allow the player to fly around.
        if self.god_mode:
            self.physics_engine.gravity_constant = 0
        else:
            self.physics_engine.gravity_constant = GRAVITY

        self.player.set_physics_state(
            up_pressed=self.up_pressed,
            down_pressed=self.down_pressed,
            right_pressed=self.right_pressed,
            left_pressed=self.left_pressed,
            god_mode=self.god_mode
        )

        for enemy in self.scene[ENEMIES_LAYER]:
            if (enemy.boundary_right and enemy.right > enemy.boundary_right and enemy.change_x > 0):
                enemy.change_x *= -1

            if (enemy.boundary_left and enemy.left < enemy.boundary_left and enemy.change_x < 0):
                enemy.change_x *= -1

            enemy.change_y -= GRAVITY
            solid_platforms = [self.scene[PLATFORMS_LAYER], self.scene[MOVING_PLATFORMS_LAYER]]
            arcade.physics_engines._move_sprite(enemy, solid_platforms, ramp_up=True)
        
        for jump_pad in self.was_touching_jump_pads:
            if not arcade.check_for_collision(self.player, jump_pad):
                self.was_touching_jump_pads.remove(jump_pad)

        if self.player.center_y < -500:
            self.kill_player()

        for spritelist in self.scene.name_mapping.keys():
            self.check_player_collisions(spritelist)

        self.scene.on_update(delta_time=self.dt)
        self.scene.update_animation(delta_time=self.dt)

        self.physics_engine.update()
        self.center_camera_to_player(camera_speed=CAMERA_SPEED)
        clock.tick()
        #sleep(0.05)
                

def main():
    """Main function."""
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
