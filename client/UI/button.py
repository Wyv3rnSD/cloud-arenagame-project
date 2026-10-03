import pygame


class Button:

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font
    ):

        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

        self.text = text
        self.font = font

        self.normal_color = (
            195,
            195,
            195
        )

        self.hover_color = (
            220,
            220,
            220
        )

        self.text_color = (
            25,
            25,
            30
        )


    # Hover
    def is_hovered(self):

        return self.rect.collidepoint(
            pygame.mouse.get_pos()
        )


    # Click
    def is_clicked(self, event):

        return (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.is_hovered()
        )


    # Draw
    def draw(self, screen):

        if self.is_hovered():

            color = self.hover_color

        else:

            color = self.normal_color


        pygame.draw.rect(
            screen,
            color,
            self.rect
        )


        text_surface = self.font.render(
            self.text,
            True,
            self.text_color
        )

        text_rect = (
            text_surface.get_rect(
                center=self.rect.center
            )
        )

        screen.blit(
            text_surface,
            text_rect
        )