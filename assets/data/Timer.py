import pygame
import sys
import random

class Timer:
    """
    A non-blocking timer class for Pygame that uses milliseconds (ms).

    This timer allows the main game loop to continue running (handling input, 
    drawing, etc.) while waiting for a specific duration to pass.
    """

    def __init__(self, duration_ms: int):
        """
        Initializes the timer with the target duration.

        Args:
            duration_ms: The length of the timer in milliseconds (e.g., 1000 for 1 second).
        """
        self.duration_ms = duration_ms
        self.start_time = 0
        self.running = False

    def start(self):
        """Starts the timer by recording the current system time."""
        self.start_time = pygame.time.get_ticks()
        self.running = True

    def stop(self):
        """Stops the timer and resets its state."""
        self.running = False
        self.start_time = 0

    def is_finished(self) -> bool:
        """
        Checks if the required duration has passed since the timer started.

        Returns:
            True if the timer is running and the duration is met or exceeded.
        """
        if not self.running:
            return False

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= self.duration_ms:
            # Optionally, you might want to automatically stop/reset here,
            # but usually, it's better to let the calling code handle the reset.
            return True
        return False