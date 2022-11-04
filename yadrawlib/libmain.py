import logging
import threading
import time
import attrs
from typing import Tuple, List, Union

import pygame

"""
Window is a unique singular parent for all graphics.
Window can have multiple areas. In order to draw to a certain area you need to select it.
Area types:
    1. None (default) - draw directly to the window, no scaling.
    2. Fixed - no scaling, but has offset and borders.
    3. Scaled - has scaling, offset and borders.
"""


def log_function(func):
    def logged_function(*args, **kwargs):
        logging.debug(f"{func.__name__} started")
        result = func(*args, **kwargs)
        logging.debug(f"{func.__name__} finished")
        return result

    return logged_function


@attrs.define(kw_only=True)
class YaDrawArea:
    x0: int = attrs.field(init=True, default=0)  # Top left corner on the screen
    y0: int = attrs.field(init=True, default=0)  # Top left corner on the screen
    w: int = attrs.field(init=True, default=800)  # Width/Height
    h: int = attrs.field(init=True, default=800)  # Width/Height
    xc: int = attrs.field(init=True, default=0)  # Coord of zero-point on the surface
    yc: int = attrs.field(init=True, default=0)  # Coord of zero-point on the surface
    xs: float = attrs.field(init=True, default=1)  # Scale
    ys: float = attrs.field(init=True, default=1)  # Scale
    surface: pygame.Surface = attrs.field(init=False, default=None)

    @log_function
    def __attrs_post_init__(self):
        self.surface = pygame.Surface((self.w, self.h))

    @log_function
    def circle(self, center: Tuple[float, float], radius: float, color: Tuple[int, int, int] = (0, 0, 0)):
        if self.xs != self.ys:
            logging.error("Unimplemented: Circle: different x and y scales.")
            return
        pygame.draw.circle(self.surface,
                           color=color,
                           center=[self.xc + self.xs * center[0], self.yc + self.ys * center[1]],
                           radius=self.xs * radius)

    @log_function
    def fill(self, color: Tuple[int, int, int] = (0, 0, 0)):
        self.surface.fill(color)


@attrs.define(kw_only=True)
class YaDrawWindow(YaDrawArea):
    """
    Main YaDraw class. Represent a single window.
    Only one window is supported.

    The usage:

    # Create the window
    window = yd.YaDrawWindow()

    # Start new loop thread
    loop_thread = threading.Thread(target=window.start_main_loop)
    loop_thread.start()

    # Draw and update
    window.circle(center=(100, 100), radius=50, color=(0, 0, 255))
    window.flip()

    # Stop main loop
    window.main_loop_running = False
    loop_thread.join()
    """
    screen: pygame.Surface = attrs.field(init=False, default=None)  # Main screen handler
    areas: List[YaDrawArea] = attrs.field(init=True, default=[])  # Areas list to automatically redraw
    continue_running_main_loop: bool = attrs.field(init=True, default=False)
    main_loop_thread: Union[threading.Thread, None] = attrs.field(init=True, default=None)
    gui_initialized: bool = attrs.field(init=False, default=False)

    @log_function
    def __attrs_post_init__(self):
        super(YaDrawWindow, self).__attrs_post_init__()
        self._start_main_loop()

    @log_function
    def __del__(self):
        if self.main_loop_thread is not None:
            self.main_loop_thread.join()
            self.main_loop_thread = None
            logging.info('Forcefully joined gui thread')
        pygame.quit()

    """ Public methods """

    @log_function
    def update(self):
        self.screen.blit(self.surface, (self.x0, self.y0))
        for area in self.areas:
            self.screen.blit(area.surface, (area.x0, area.y0))
        pygame.display.flip()

    @log_function
    def close(self):
        self._stop_main_loop()

    """ Private methods """

    @log_function
    def _start_main_loop(self):
        self.main_loop_thread = threading.Thread(target=self._main_loop)
        self.gui_initialized = False
        self.continue_running_main_loop = True
        self.main_loop_thread.start()
        logging.info('Started gui thread')
        logging.debug('Main thread: waiting for gui to initialize')
        while not self.gui_initialized:
            pass
        logging.debug('Main thread: continue')

    @log_function
    def _stop_main_loop(self):
        self.continue_running_main_loop = False
        self.main_loop_thread.join()
        self.main_loop_thread = None
        logging.info('Joined gui thread')

    """ In-thread methods """
    @log_function
    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode([self.w, self.h])
        self.gui_initialized = True

    @log_function
    def _main_loop(self):
        self.init()
        while self.continue_running_main_loop:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    logging.info("pygame.MOUSEBUTTONUP message received.")
                if event.type == pygame.QUIT:
                    logging.info("pygame.QUIT message received.")
                    self.continue_running_main_loop = False
