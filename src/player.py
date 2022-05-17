import arcade
from math import floor

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

CHARACTER_SCALING = 4


def load_texture_pair(file_name):
    """Load two textures from the filename, the first texture NOT flipped, the second texture flipped"""
    return (
        arcade.load_texture(file_name=file_name),
        arcade.load_texture(file_name=file_name, flipped_horizontally=True)
    )


class UknownAnimationCaseError(Exception): pass


class Animation():
    def __init__(self, frames, speed=0.25, use_right_left=True):
        self.frames = frames
        self.speed = speed
        self.use_right_left = use_right_left
        self._frame_num = 0

    @property
    def frame_num(self):
        return self._frame_num

    @frame_num.setter
    def frame_num(self, value):
        self._frame_num = value
        if self.frame_num >= len(self.frames):
            self.reset()

    def reset(self):
        self._frame_num = 0

    def update(self, delta_time):
        self.frame_num += self.speed

    def get_current_frame(self, direction=None):
        if self.use_right_left:
            current_frame = self.frames[floor(self.frame_num)][direction]
        else:
            current_frame = self.frames[floor(self.frame_num)]
        return current_frame

class WalkingAnimation(Animation):
    def __init__(self, frames, max_player_speed=5, speed=0.25, use_right_left=True):
        super().__init__(frames=frames, speed=speed, use_right_left=use_right_left)
        self.max_player_speed = max_player_speed

    def update(self, player_speed, delta_time):
        self.frame_num += abs((self.speed * (player_speed / self.max_player_speed)))


class PlayerSprite(arcade.Sprite):
    def __init__(self, physics_engine=None):
        super().__init__()

        self.face_direction = RIGHT_FACING
        self.physics_engine = physics_engine

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # ---- Load Textures ----

        main_path = r"src\assets\images\player"

        self.idle_texture_pair = load_texture_pair(f"{main_path}/idle1.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}/jump1.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}/fall1.png")
        self.walk_textures = [load_texture_pair(f"{main_path}/walk{i+1}.png") for i in range(8)]
        self.climb_textures = [arcade.load_texture(f"{main_path}/climb{i+1}.png") for i in range(4)]

        self.walk_anim = WalkingAnimation(self.walk_textures)
        self.climb_anim = Animation(self.climb_textures, use_right_left=False)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

        self.state = "idle"

    def set_physics_state(self, is_on_ladder, can_jump, up_pressed, down_pressed, right_pressed, left_pressed):
        self.is_on_ladder = is_on_ladder
        self.can_jump = can_jump
        self.up_pressed = up_pressed
        self.down_pressed = down_pressed
        self.right_pressed = right_pressed
        self.left_pressed = left_pressed

    def get_state(self):
        if self.climbing:
            return "climb"

        if (not self.can_jump) and (not self.is_on_ladder):  # This means the player is in the air
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

    def update_animation(self, delta_time = 1/60):
        self.dt = delta_time
        old_state = self.state
        if self.change_x < 0 and self.face_direction == RIGHT_FACING:
            self.face_direction = LEFT_FACING
        elif self.change_x > 0 and self.face_direction == LEFT_FACING:
            self.face_direction = RIGHT_FACING

        if self.is_on_ladder and (self.up_pressed or self.down_pressed):
            self.climbing = True
        elif not self.is_on_ladder:
            self.climbing = False
            
        self.state = self.get_state()

        if self.state == "idle":
            self.texture = self.idle_texture_pair[self.face_direction]

        elif self.state == "jump":
            self.texture = self.jump_texture_pair[self.face_direction]

        elif self.state == "fall":
            self.texture = self.fall_texture_pair[self.face_direction]

        elif self.state == "walk":
            if not self.state == old_state:
                self.walk_anim.reset()
            self.texture = self.walk_anim.get_current_frame(self.face_direction)
            self.walk_anim.update(self.change_x, self.dt)

        elif self.state == "climb":
            if not self.state == old_state:
                self.climb_anim.reset()
            self.texture = self.climb_anim.get_current_frame()
            # If the player is moving, update the climbing animation, to make the player climb.
            if (abs(self.change_x) > 0) or (abs(self.change_y) > 0):
                self.climb_anim.update(self.dt)
            

    def on_update(self, delta_time):
        self.dt = delta_time
        self.position = [
            self._position[0] + self.change_x,
            self._position[1] + self.change_y,
        ]
        self.angle += self.change_angle