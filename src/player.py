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


class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # ---- Load Textures ----

        main_path = r"src\assets\images\player"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}/idle1.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}/jump1.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}/fall1.png")

        # Load textures for walking
        self.walk_textures = [load_texture_pair(f"{main_path}/walk{i+1}.png") for i in range(8)]

        # Load textures for climbing
        # TODO Add textures for climbing. For now, just use the idle textures
        self.climbing_textures = self.idle_texture_pair

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

    def animation(self, frames, speed=0.25, loop=False):
        # TODO Add times parameter that allows the animation to be repeated multiple times.
        while True:
            frame = 0
            while frame < 8:
                yield frames[floor(frame)][self.face_direction]
                frame += speed
            if not loop:
                break

    def walk_animation(self):
        yield from self.animation(self.walk_textures, 0.25, loop=True)

    def update_animation(self, delta_time):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 0.25
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[floor(self.cur_texture)][self.character_face_direction]

    def on_update(self, delta_time):
        self.dt = delta_time
        self.position = [
            self._position[0] + self.change_x,
            self._position[1] + self.change_y,
        ]
        self.angle += self.change_angle