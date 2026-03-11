import pygame

from project.config import BACKGROUND_COLOR
from project.ui.scenes.base_scene import BaseScene
from project.ui.widgets.button import Button


class MenuScene(BaseScene):

    def __init__(self) -> None:
        pygame.font.init()

        self.title_font = pygame.font.SysFont("arial", 72)
        self.button_font = pygame.font.SysFont("arial", 36)

        self.play_button = Button(
            pygame.Rect(380, 300, 200, 60),
            "PLAY",
            self.button_font,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.play_button.is_clicked(event):
            print("PLAY clicked")

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(BACKGROUND_COLOR)

        title_surface = self.title_font.render(
            "Adaptive Chess AI",
            True,
            (230, 230, 230),
        )

        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(title_surface, title_rect)

        self.play_button.draw(screen)