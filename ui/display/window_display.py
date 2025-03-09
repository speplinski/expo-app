import logging
import sys
import time

import cv2
import sdl2
import ctypes

import numpy as np
import numpy.typing as npt
from sdl2.ext import Texture
from textual.app import App

from config.modules_configs.display_config import DisplayConfig
from ui.display.playback_statistics import PlaybackStatistics
from ui.display.sdl_app import SDLApp

class WindowDisplay:
    def __init__(self, config: DisplayConfig, app: App):
        self.config = config

        self.logger = logging.getLogger()

        self.app = app

        self.sdl_app = SDLApp(config.monitor_index, config)

        self.rendering_texture = None

        self.main_rect = sdl2.SDL_Rect(
            0, 
            config.vertical_resolution_offset,
            config.model_resolution[0],
            config.model_resolution[1]
        )

        self.stats = PlaybackStatistics()

    def process_frame(self, image: npt.NDArray[np.uint8]):
        try:
            self._handle_events()

            self._render(image)
        except Exception as e:
            self.logger.error(f"Error in render loop: {e}")

    def _handle_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl2.SDL_QUIT:
                self.app.action_quit()
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym in (sdl2.SDLK_ESCAPE, sdl2.SDLK_q):
                    self.app.action_quit()

    def _render(self, image: npt.NDArray[np.uint8]):
        image_texture = self._get_image_texture(image)

        if self.rendering_texture:
            sdl2.SDL_DestroyTexture(self.rendering_texture)
        self.rendering_texture = image_texture

        self.stats.update_display_frame()
        if not self.stats.start_time:
            self.stats.start_playback(time.time())

        sdl2.SDL_SetRenderDrawColor(self.sdl_app.renderer, 0, 0, 0, 255)
        sdl2.SDL_RenderClear(self.sdl_app.renderer)

        if self.rendering_texture:
            sdl2.SDL_RenderCopy(
                self.sdl_app.renderer,
                self.rendering_texture,
                None,
                self.main_rect
            )

        sdl2.SDL_RenderPresent(self.sdl_app.renderer)

    def _get_image_texture(self, opencv_image: npt.NDArray[np.uint8]) -> Texture:
        rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)

        height, width = rgb_image.shape[:2]
        depth = 24  # RGB - 8 bits per channel
        if sys.byteorder == 'little':
            rmask, gmask, bmask = 0x000000FF, 0x0000FF00, 0x00FF0000
        else:
            rmask, gmask, bmask = 0xFF000000, 0x00FF0000, 0x0000FF00
        amask = 0

        surface = sdl2.SDL_CreateRGBSurface(
            0, width, height, depth,
            rmask, gmask, bmask, amask
        )

        if not surface:
            raise Exception("Could not create SDL surface: " + sdl2.SDL_GetError().decode())

        sdl2.SDL_LockSurface(surface)

        image_pixels = rgb_image.tobytes()
        ctypes.memmove(surface.contents.pixels, image_pixels, len(image_pixels))
        sdl2.SDL_UnlockSurface(surface)

        texture = sdl2.SDL_CreateTextureFromSurface(self.sdl_app.renderer, surface)

        sdl2.SDL_FreeSurface(surface)

        if not texture:
            raise Exception("Failed to create texture: " + sdl2.SDL_GetError().decode())

        return texture

    def cleanup(self):
        self.sdl_app.close()

        if self.rendering_texture:
            sdl2.SDL_DestroyTexture(self.rendering_texture)
            self.rendering_texture = None
