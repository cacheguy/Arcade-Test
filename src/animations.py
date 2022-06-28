from math import floor

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