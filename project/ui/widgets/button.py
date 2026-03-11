import pygame

class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font) -> None:
        self.rect = rect
        self.text = text
        self.font = font

        self.bg_color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = (230, 230, 230)

    def draw(self, screen: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()

        color = self.bg_color
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color

        pygame.draw.rect(screen, color, self.rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)

        screen.blit(text_surface, text_rect)

    def is_clicked(self, event: pygame.event.Event)-> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
            return False