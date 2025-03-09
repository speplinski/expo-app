import sdl2
import ctypes

from config.modules_configs.display_config import DisplayConfig


class SDLApp:
    def __init__(self, monitor_index: int, config: DisplayConfig):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise Exception(sdl2.SDL_GetError())

        self.config = config
        self.window, self.renderer = self._create_window_and_renderer(monitor_index)

    def _create_window_and_renderer(self, monitor_index):
        num_displays = sdl2.SDL_GetNumVideoDisplays()
        if monitor_index >= num_displays:
            print(f"Warning: Monitor {monitor_index} not found. Using monitor 0.")
            monitor_index = 0

        display_bounds = sdl2.SDL_Rect()
        sdl2.SDL_GetDisplayBounds(monitor_index, ctypes.byref(display_bounds))

        window = sdl2.SDL_CreateWindow(
            b"The Most Polish Landscape",
            display_bounds.x,
            display_bounds.y,
            display_bounds.w if self.config.full_screen_mode else display_bounds.w // 2,
            display_bounds.h if self.config.full_screen_mode else display_bounds.h // 2,
            sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP if self.config.full_screen_mode else sdl2.SDL_WINDOW_METAL
        )

        if not window:
            raise Exception(sdl2.SDL_GetError())

        renderer = sdl2.SDL_CreateRenderer(
            window, -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        )

        if not renderer:
            raise Exception(sdl2.SDL_GetError())

        renderer_info = sdl2.SDL_RendererInfo()
        sdl2.SDL_GetRendererInfo(renderer, renderer_info)
        if not (renderer_info.flags & sdl2.SDL_RENDERER_PRESENTVSYNC):
            print("Warning: VSYNC not available")

        sdl2.SDL_RenderSetLogicalSize(
            renderer, 
            self.config.resolution[0],
            self.config.resolution[1]
        )

        return window, renderer

    def close(self):
        if hasattr(self, 'renderer') and self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if hasattr(self, 'window') and self.window:
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()