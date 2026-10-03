import pygame
import time


class TextInput:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        font,
        placeholder="Type here...",
        initial_text="",
        max_length=15,
        uppercase=False
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.placeholder = placeholder
        self.text = initial_text
        self.max_length = max_length
        self.uppercase = uppercase

        self.active = False
        self.cursor_visible = True
        self.last_blink = time.time()

        # Colors matching the game's clean UI palette
        self.bg_color = (235, 235, 235)
        self.border_normal = (160, 160, 160)
        self.border_active = (70, 140, 240)
        self.text_color = (25, 25, 30)
        self.placeholder_color = (140, 140, 140)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return None

        if not self.active or event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            return "submit"
        else:
            if len(self.text) < self.max_length:
                char = event.unicode
                if char.isprintable() and char != "":
                    if self.uppercase:
                        char = char.upper()
                    self.text += char

        return None

    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect)

        # Border
        border_color = self.border_active if self.active else self.border_normal
        border_width = 3 if self.active else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width)

        # Text rendering
        display_text = self.text
        if not display_text and not self.active:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
        else:
            text_surface = self.font.render(display_text, True, self.text_color)

        text_rect = text_surface.get_rect(
            midleft=(self.rect.x + 15, self.rect.centery)
        )
        screen.blit(text_surface, text_rect)

        # Blinking cursor when active
        if self.active:
            now = time.time()
            if now - self.last_blink > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.last_blink = now

            if self.cursor_visible:
                cursor_x = text_rect.right + 2 if display_text else self.rect.x + 15
                cursor_top = self.rect.y + 10
                cursor_bottom = self.rect.bottom - 10
                pygame.draw.line(
                    screen,
                    self.text_color,
                    (cursor_x, cursor_top),
                    (cursor_x, cursor_bottom),
                    2
                )
