import sys

import pygame

from project.config import BACKGROUND_COLOR, FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from project.ui.scenes.base_scene import BaseScene
from project.ui.scenes.menu_scene import MenuScene


class GameApp:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.current_scene: BaseScene = MenuScene()

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)

            self._handle_events()
            self._update()
            self._render()

        pygame.quit()
        sys.exit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                continue
            self.current_scene.handle_event(event)

    def _update(self) -> None:
        self.current_scene.update()

    def _render(self) -> None:
        self.current_scene.render(self.screen)
        pygame.display.flip()
