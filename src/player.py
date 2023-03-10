import arcade

from animations import Animation, WalkingAnimation
from constants import *
import sounds


def load_texture_pair(file_name):
    """Load two textures from the filename, the first texture NOT flipped, the second texture flipped"""
    return (
        arcade.load_texture(file_name=file_name),
        arcade.load_texture(file_name=file_name, flipped_horizontally=True)
    )


class UknownAnimationCaseError(Exception): pass

    
class Entity(arcade.Sprite):
    def __init__(self, images_path):
        super().__init__()

        self.face_direction = RIGHT_FACING
        self.scale = CHARACTER_SCALING
        self.state = "idle"
        self.dt = 0

        # ---- Load Textures ----

        self.idle_texture_pair = load_texture_pair(f"{images_path}/idle1.png")

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

    def get_state(self):
        return "idle"

    def prepare_animations(self):
        """Call this before every update_animation method"""
        self.old_state = self.state
        if self.change_x < 0 and self.face_direction == RIGHT_FACING:
            self.face_direction = LEFT_FACING
        elif self.change_x > 0 and self.face_direction == LEFT_FACING:
            self.face_direction = RIGHT_FACING

        self.state = self.get_state()

    def update_animation(self, delta_time=1/60):
        self.prepare_animations()

    def on_update(self, delta_time):
        self.dt = delta_time


class EnemySprite(Entity):
    def __init__(self, images_path):
        super().__init__(images_path)
        self.fall_texture_pair = load_texture_pair(f"{images_path}/fall1.png")
        self.walk_textures = [load_texture_pair(f"{images_path}/walk{i+1}.png") for i in range(8)]

        self.walk_anim = WalkingAnimation(self.walk_textures, max_player_speed=3)

    def get_state(self):
        if abs(self.change_y) > 0:
            return "fall"

        if self.change_x == 0:
            return "idle"

        if abs(self.change_x) > 0:
            return "walk"

        raise UknownAnimationCaseError("There has been an unknown animation case. In other words, the program can't \
                                        figure out which animation to use.")

    def update_animation(self, delta_time=1/60):
        self.prepare_animations()

        if self.state == "idle":
            self.texture = self.idle_texture_pair[self.face_direction]

        elif self.state == "fall":
            self.texture = self.fall_texture_pair[self.face_direction]

        elif self.state == "walk":
            if not self.state == self.old_state:
                self.walk_anim.reset()
            self.texture = self.walk_anim.get_current_frame(self.face_direction)
            self.walk_anim.update(self.change_x, self.dt)


class BattleBotEnemy(EnemySprite):
    def __init__(self, boundary_right, boundary_left, center_x, center_y):
        images_path = f"src/assets/images/battle_bot"
        super().__init__(images_path)
        self.speed = 3
        self.change_x = self.speed
        self.boundary_right = boundary_right
        self.boundary_left = boundary_left
        self.center_x = center_x
        self.center_y = center_y
        # Override EnemySprite animation to replace the max_player_speed parameter.
        self.walk_anim = WalkingAnimation(self.walk_textures, max_player_speed=self.speed)  

    def on_update(self, delta_time):
        if (self.right > self.boundary_right and self.change_x > 0):
            self.change_x = -self.speed  # Turn left

        if (self.left < self.boundary_left and self.change_x < 0):
            self.change_x = self.speed  # Turn right


class MissleBotEnemy(EnemySprite):
    def __init__(self, boundary_right, boundary_left, center_x, center_y):
        images_path = f"src/assets/images/missle_bot"
        super().__init__(images_path)
        self.speed = 3
        self.change_x = self.speed
        self.boundary_right = boundary_right
        self.boundary_left = boundary_left
        self.center_x = center_x
        self.center_y = center_y
        self.walk_anim = WalkingAnimation(self.walk_textures, max_player_speed=self.speed)

    def on_update(self, delta_time):
        # TODO Make the missle_bot shoot missles
        if (self.right > self.boundary_right and self.change_x > 0):
            self.change_x = -self.speed  # Turn left

        if (self.left < self.boundary_left and self.change_x < 0):
            self.change_x = self.speed  # Turn right
            

class PlayerSprite(Entity):
    def __init__(self):
        images_path = "src/assets/images/player"
        super().__init__(images_path)

        self.jump_count = 0
        self.climbing = False
        self.jump_count = 0
        self.stop_jump = False

        self.jump_texture_pair = load_texture_pair(f"{images_path}/jump1.png")
        self.fall_texture_pair = load_texture_pair(f"{images_path}/fall1.png")
        self.walk_textures = [load_texture_pair(f"{images_path}/walk{i+1}.png") for i in range(8)]
        self.climb_textures = [arcade.load_texture(f"{images_path}/climb{i+1}.png") for i in range(4)]

        self.walk_anim = WalkingAnimation(self.walk_textures)
        self.climb_anim = Animation(self.climb_textures, use_right_left=False)

        # Set default physic states
        self.set_physics_state(
            up_pressed=False,
            down_pressed=False,
            right_pressed=False,
            left_pressed=False,
            god_mode=False
        )

    def register_one_physics_engine(self, physics_engine):
        self.physics_engine: arcade.PhysicsEnginePlatformer = physics_engine

    def set_physics_state(self, up_pressed, down_pressed, right_pressed, left_pressed, god_mode):
        self.up_pressed = up_pressed
        self.down_pressed = down_pressed
        self.right_pressed = right_pressed
        self.left_pressed = left_pressed
        self.god_mode = god_mode

    def get_state(self):
        if self.god_mode:
            return "fall"

        if self.climbing:
            return "climb"

        # This means the player is in the air
        if (not self.physics_engine.can_jump()) and (not self.physics_engine.is_on_ladder()):
            if self.change_y > 0:
                return "jump"
            else:
                return "fall"

        if self.change_x == 0:
            return "idle"

        if abs(self.change_x) > 0:
            return "walk"

        raise UknownAnimationCaseError("There has been an unknown animation case. In other words, the program can't \
                                        figure out which animation to use.")

    def on_update(self, delta_time):
        """Handle the player's movement based on the pressed keys."""
        self.dt = delta_time
        if self.god_mode:
            self.update_god_mode_physics()
        else:
            # This piece of code stops the player from jumping in the air 
            # When the up key is released (not pressed)
            if not self.up_pressed:
                # If on the ground
                if self.physics_engine.can_jump():
                    # Allow the player to jump again
                    self.stop_jump = False
                    self.jump_count = 0
                # Else, if in the air
                else:
                    # Stop the player from jumping in the air
                    self.stop_jump = True

            if self.physics_engine.is_on_ladder():
                if self.up_pressed and not self.down_pressed:
                    self.change_y = PLAYER_MOVEMENT_SPEED
                    self.jump_count = MAX_JUMP_COUNT
                elif self.down_pressed and not self.up_pressed:
                    self.change_y = -PLAYER_MOVEMENT_SPEED
                else:
                    self.change_y = 0

            elif (self.physics_engine.can_jump() or self.jump_count > 0) \
                 and self.jump_count < MAX_JUMP_COUNT \
                 and self.up_pressed \
                 and not self.stop_jump:
                self.change_y = PLAYER_JUMP_SPEED
                self.jump_count += 1
                if self.jump_count == 1:
                    sounds.jump_sound.play()
            
            # Apply acceleration based on the keys pressed
            if self.left_pressed and not self.right_pressed:
                self.change_x += -ACCELERATION_RATE
            elif self.right_pressed and not self.left_pressed:
                self.change_x += ACCELERATION_RATE
            else:
                if self.change_x > 0:
                    self.change_x -= FRICTION
                    if self.change_x < 0:
                        self.change_x = 0
                elif self.change_x < 0:
                    self.change_x += FRICTION
                    if self.change_x > 0:
                        self.change_x = 0
            
            # Ensure player speed does not exceed max speed
            if self.change_x > MAX_SPEED:
                self.change_x = MAX_SPEED
            elif self.change_x < -MAX_SPEED:
                self.change_x = -MAX_SPEED

    def update_god_mode_physics(self):
        """God mode physics"""

        if self.left_pressed and not self.right_pressed:
            self.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.change_x = PLAYER_MOVEMENT_SPEED
        else:
            self.change_x = 0

        if self.up_pressed and not self.down_pressed:
            self.change_y = PLAYER_MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            self.change_y = 0

    def update_animation(self, delta_time = 1/60):
        self.prepare_animations()

        if self.physics_engine.is_on_ladder() and (self.up_pressed or self.down_pressed):
            self.climbing = True
        elif not self.physics_engine.is_on_ladder():
            self.climbing = False
        if self.state == "idle":
            self.texture = self.idle_texture_pair[self.face_direction]

        elif self.state == "jump":
            self.texture = self.jump_texture_pair[self.face_direction]

        elif self.state == "fall":
            self.texture = self.fall_texture_pair[self.face_direction]

        elif self.state == "walk":
            if not self.state == self.old_state:
                self.walk_anim.reset()
            self.texture = self.walk_anim.get_current_frame(self.face_direction)
            self.walk_anim.update(self.change_x, self.dt)

        elif self.state == "climb":
            if not self.state == self.old_state:
                self.climb_anim.reset()
            self.texture = self.climb_anim.get_current_frame()
            # If the player is moving, update the climbing animation, to make the player climb.
            if (abs(self.change_x) > 0) or (abs(self.change_y) > 0):
                self.climb_anim.update(self.dt)