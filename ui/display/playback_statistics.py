import time

class PlaybackStatistics:
    def __init__(self):
        self.start_time = 0
        self.playback_time = 0.0
        self.displayed_frames = 0
        self.playing = False

    def format_stats(self):
        if self.start_time == 0:
            return "00:00:00.00 | Total frames: 0 (0.0/s)"
        
        elapsed = time.time() - self.start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        display_fps = self.displayed_frames / max(elapsed, 0.001)

        return (
            f"{int(hours):02}:{int(minutes):02}:{seconds:05.2f} | "
            f"Total frames: {self.displayed_frames} ({display_fps:.1f}/s)"
        )

    def update_display_frame(self):
        self.displayed_frames += 1
       
    def start_playback(self, start_time=None):
        if start_time is not None:
            self.start_time = start_time
        elif self.start_time == 0:
            self.start_time = time.time()
        self.playing = True

    def pause_playback(self):
        self.playing = False
