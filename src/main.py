import arcade
import tkinter as tk
from pyglet import clock
from math import floor
from time import sleep

from player import PlayerSprite, BattleBotEnemy, MissleBotEnemy
from constants import *
import custom_tilemap
import sounds
import cProfile
import pstats

# TODO Update all libraries (especially arcade)

TYPES_TO_LAYER = {
    ("ladder",): LADDERS_LAYER,
    ("coin",): COINS_LAYER,
    ("lava",): DANGER_LAYER,
    ("goal",): GOAL_LAYER,
    ("blue_jump_pad", "green_jump_pad"): JUMP_PADS_LAYER
}

TYPES_TO_ENEMY = {
    ("battle_bot",): BattleBotEnemy,
    ("missle_bot",): MissleBotEnemy
}

MAP_NAME = "basic_tilemap_1"

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

        # self.times = 0
        # self.max_times = 60
        #self.set_update_rate(1/500)

    def setup(self):
        """Set up the game here. Call this method to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        
        map_path = f"src/assets/tilemap_project/tilemaps/{MAP_NAME}.tmx"

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
        self.tile_map = custom_tilemap.load_tilemap(map_path, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        for layer in ALL_LAYERS:
            if not self.scene.name_mapping.get(layer):
                self.scene.add_sprite_list(layer, use_spatial_hash=layer_options[layer]["use_spatial_hash"])

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
            for key in TYPES_TO_LAYER.keys():
                if ttype in key:
                    self.scene.add_sprite(name=TYPES_TO_LAYER[key], sprite=tile)
        
        # Delete OBJECTS_LAYER. Since we have split all of the tiles in OBJECTS_LAYER into seperate spritelists, we have
        # no more use for it.
        self.scene.remove_sprite_list_by_name(OBJECTS_LAYER)

        # Set up the player, specifically placing it at these coordinates.
        self.player = PlayerSprite()
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.scene.add_sprite(PLAYER_LAYER, self.player)

        self.add_enemies_to_scene()

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

    def add_enemies_to_scene(self):
        """Add enemies to the scene. Assumes that self.tile_map and self.scene are already created."""
        enemies_layer = self.tile_map.object_lists[ENEMIES_LAYER]
        id_to_enemies = dict()
        for enemy_object in enemies_layer:
            # Checks if enemy_object has the "type" property
            # If it does, then it is an enemy
            # If it doesn't, it is just a point. A point is used by enemy objects to indicate specific coordinates, like
            # boundaries.
            enemy_type = enemy_object.properties.get("type")
            if enemy_type is not None:  
                enemy_cartesian_pos = self.tile_map.get_cartesian(*enemy_object.shape)

                if enemy_type in ("battle_bot", "missle_bot"):
                    center_x = floor(enemy_cartesian_pos[0] * GRID_PIXEL_SIZE)
                    center_y = floor((enemy_cartesian_pos[1] + 1) * GRID_PIXEL_SIZE)
                    boundary_left_obj = self.tile_map._get_object_by_id(enemy_object.properties["boundary_left"])
                    boundary_right_obj = self.tile_map._get_object_by_id(enemy_object.properties["boundary_right"])
                    boundary_left = boundary_left_obj.shape[0] * TILE_SCALING
                    boundary_right = boundary_right_obj.shape[0] * TILE_SCALING

                    kwargs = {
                        "center_x": center_x,
                        "center_y": center_y,
                        "boundary_left": boundary_left,
                        "boundary_right": boundary_right
                    }

                elif enemy_type == "drone_bot":
                    raise NotImplementedError("drone_bot is not implemented into the game yet.")

                elif enemy_type == "assassin_bot":
                    raise NotImplementedError("assassin_bot is not implemented into the game yet.")

                else:
                    raise UknownEnemyError(f"Unknown enemy type: {enemy_type}.")

                TYPES_TO_ENEMY = {
                    "battle_bot": BattleBotEnemy,
                    "missle_bot": MissleBotEnemy,
                }
                try:
                    enemy = TYPES_TO_ENEMY[enemy_type](**kwargs)
                except KeyError:
                    raise UknownEnemyError(f"Unknown enemy type: {enemy_type}.")

                self.scene.add_sprite(ENEMIES_LAYER, enemy)

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
            self.debug_text("Change x", self.player.change_x)
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
                        # For consistency, we want the player to jump FROM THE TOP of the jump pad, instead of from
                        # their current y position.
                        # However, each type of jump pad has different heights.
                        # This means the player will jump at a different height, because it will jump from a different 
                        # position, due to the different jump pad heights.
                        # Using this piece of code, we can get the height of the tile of the jump pad (which is 
                        # always consistent), instead of the height of the jump pad itself.
                        jump_pad_cartesian_y = (self.tile_map.get_cartesian(jump_pad.center_x, jump_pad.center_y))[1]
                        self.player.bottom = jump_pad_cartesian_y * GRID_PIXEL_SIZE
                        if jump_pad.properties["type"] == "blue_jump_pad":
                            self.player.change_y = BLUE_JUMP_PAD_BOOST_SPEED
                            sounds.blue_jump_pad_sound.play()
                        elif jump_pad.properties["type"] == "green_jump_pad":
                            self.player.change_y = GREEN_JUMP_PAD_BOOST_SPEED
                            sounds.green_jump_pad_sound.play()
                        self.was_touching_jump_pads.append(jump_pad)

    def on_update(self, delta_time):
        """Movement and game logic."""
        # self.times += 1
        # if self.times > self.max_times:
        #     self.close()
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
        
        for jump_pad in self.was_touching_jump_pads:
            if not arcade.check_for_collision(self.player, jump_pad):
                self.was_touching_jump_pads.remove(jump_pad)

        if self.player.center_y < -500:
            self.kill_player()

        for spritelist in self.scene.name_mapping.keys():
            self.check_player_collisions(spritelist)

        self.scene.on_update(delta_time=self.dt)
        self.scene.update_animation(delta_time=self.dt)

        # Update physics on everything
        self.physics_engine.update()
        for enemy in self.scene[ENEMIES_LAYER]:
            enemy.change_y -= GRAVITY
            solid_platforms = [self.scene[PLATFORMS_LAYER], self.scene[MOVING_PLATFORMS_LAYER]]
            arcade.physics_engines._move_sprite(enemy, solid_platforms, ramp_up=True)

        self.center_camera_to_player(camera_speed=CAMERA_SPEED)
        clock.tick()
        #sleep(0.05)
                

def main():
    """Main function."""
    window = Game()
    window.setup()
    # pr = cProfile.Profile()
    # pr.enable()
    # arcade.run()
    # pr.disable()
    # stats = pstats.Stats(pr)
    # stats.sort_stats("time").print_stats("src")
    arcade.run()

if __name__ == "__main__":
    main()
