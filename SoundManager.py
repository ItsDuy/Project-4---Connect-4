import os
from typing import Optional

import pygame


class SoundManager:
    """
    Simple sound manager for Connect Four.

    - Plays background music (BGM) on loop using pygame.mixer.music
    - Plays a short sound effect (SFX) on each valid move
    - Supports adjusting BGM and SFX volumes separately as percentages (0 - 100)

    Notes:
      - Public API now uses percent-based volumes (ints/floats in range 0..100).
      - Internally converted to pygame's 0.0..1.0 when setting mixer volume.
      - Setters remain backward-compatible: if a value <= 1.0 is provided,
        it is treated as a normalized 0.0..1.0 volume and converted to percent.

    Default file resolution tries these locations:
      assets/bgm.wav, bgm.wav
      assets/sfx_move.wav, sfx_move.wav
    """

    def __init__(
        self,
        bgm_path: Optional[str] = None,
        sfx_path: Optional[str] = None,
        bgm_volume: float = 100,
        sfx_volume: float = 100,
    ) -> None:
        self.bgm_path = bgm_path or self._find_default("bgm.wav")
        self.sfx_path = sfx_path or self._find_default("sfx_move.wav")
        # Store as percent 0..100
        self.bgm_volume = self._to_percent(bgm_volume)
        self.sfx_volume = self._to_percent(sfx_volume)

        self._sfx: Optional[pygame.mixer.Sound] = None
        self._mixer_ready: bool = False

    def _find_default(self, filename: str) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base, "assets", filename),
            os.path.join(base, filename),
        ]
        for p in candidates:
            if os.path.isfile(p):
                return p
        return candidates[0]

    def init(self) -> None:
        """Initialize mixer and load audio files if available."""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"[SoundManager] Failed to init mixer: {e}")
                return
        self._mixer_ready = True

        # Load BGM
        if self.bgm_path and os.path.isfile(self.bgm_path):
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(self._percent_to_norm(self.bgm_volume))
            except Exception as e:
                print(f"[SoundManager] Failed to load BGM '{self.bgm_path}': {e}")
        else:
            print(f"[SoundManager] BGM file not found at '{self.bgm_path}'")

        # Load SFX
        if self.sfx_path and os.path.isfile(self.sfx_path):
            try:
                self._sfx = pygame.mixer.Sound(self.sfx_path)
                self._sfx.set_volume(self._percent_to_norm(self.sfx_volume))
            except Exception as e:
                print(f"[SoundManager] Failed to load SFX '{self.sfx_path}': {e}")
        else:
            print(f"[SoundManager] SFX file not found at '{self.sfx_path}'")

    def play_bgm(self, loops: int = -1, fade_ms: int = 500) -> None:
        if not self._mixer_ready:
            self.init()
        try:
            if pygame.mixer.music.get_busy():
                return
            pygame.mixer.music.set_volume(self._percent_to_norm(self.bgm_volume))
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        except Exception as e:
            print(f"[SoundManager] Failed to play BGM: {e}")

    def stop_bgm(self, fade_ms: int = 500) -> None:
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception as e:
            print(f"[SoundManager] Failed to stop BGM: {e}")

    def play_sfx(self) -> None:
        if not self._mixer_ready:
            self.init()
        try:
            if self._sfx is not None:
                self._sfx.play()
        except Exception as e:
            print(f"[SoundManager] Failed to play SFX: {e}")

    def set_bgm_volume(self, volume: float) -> None:
        """Set BGM volume.

        Accepts either percent (0..100) or normalized (0.0..1.0). Values <= 1.0
        are treated as normalized and converted to percent. Stored value is percent.
        """
        self.bgm_volume = self._to_percent(volume)
        try:
            pygame.mixer.music.set_volume(self._percent_to_norm(self.bgm_volume))
        except Exception:
            pass

    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume.

        Accepts either percent (0..100) or normalized (0.0..1.0). Values <= 1.0
        are treated as normalized and converted to percent. Stored value is percent.
        """
        self.sfx_volume = self._to_percent(volume)
        if self._sfx is not None:
            try:
                self._sfx.set_volume(self._percent_to_norm(self.sfx_volume))
            except Exception:
                pass

    def cleanup(self) -> None:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass

        self._mixer_ready = False

    @staticmethod
    def _percent_to_norm(p: float) -> float:
        """Convert 0..100 percent to pygame 0.0..1.0 range."""
        try:
            return max(0.0, min(1.0, float(p) / 100.0))
        except Exception:
            return 1.0

    @staticmethod
    def _clamp_percent(p: float) -> float:
        try:
            x = float(p)
        except Exception:
            x = 100.0
        return max(0.0, min(100.0, x))

    def _to_percent(self, v: float) -> float:
        """Interpret value as percent unless it's <= 1.0 (normalized)."""
        try:
            x = float(v)
        except Exception:
            x = 100.0
        if 0.0 <= x <= 1.0:
            return self._clamp_percent(x * 100.0)
        return self._clamp_percent(x)
