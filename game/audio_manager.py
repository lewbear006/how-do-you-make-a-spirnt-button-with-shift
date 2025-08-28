"""
Audio Manager for Rent Quest
Handles all sound effects and music
"""

import pygame
from typing import Dict, Optional

class AudioManager:
    """Manages all audio for the game"""
    
    def __init__(self):
        """Initialize audio manager"""
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Audio storage
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.current_music = None
        
        # Load audio files (placeholder for now)
        self._load_audio()
        
    def _load_audio(self):
        """Load all audio files"""
        # For now, we'll create placeholder sounds
        # In a full game, you'd load actual audio files
        
        # Create simple sound effects using pygame
        try:
            # Create a simple beep sound for button clicks
            self._create_beep_sound("button_click", 440, 0.1)
            self._create_beep_sound("gun_shot", 220, 0.05)
            self._create_beep_sound("monster_death", 110, 0.2)
            self._create_beep_sound("pickup", 880, 0.1)
            
        except Exception as e:
            print(f"Warning: Could not create audio: {e}")
            
    def _create_beep_sound(self, name: str, frequency: int, duration: float):
        """Create a simple beep sound"""
        try:
            import numpy as np
            
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            # Generate sine wave
            for i in range(frames):
                wave = np.sin(2 * np.pi * frequency * i / sample_rate)
                # Apply envelope to avoid clicks
                envelope = 1.0
                if i < frames * 0.1:  # Fade in
                    envelope = i / (frames * 0.1)
                elif i > frames * 0.8:  # Fade out
                    envelope = (frames - i) / (frames * 0.2)
                
                arr[i] = [wave * envelope * 0.3, wave * envelope * 0.3]
                
            # Convert to pygame sound
            arr = (arr * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(arr)
            self.sounds[name] = sound
        except ImportError:
            # Create empty sound if numpy is not available
            sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 1024)
            self.sounds[name] = sound
        
    def play_sound(self, sound_name: str, volume: Optional[float] = None):
        """Play a sound effect"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume * self.sfx_volume)
            else:
                sound.set_volume(self.sfx_volume)
            sound.play()
        else:
            print(f"Warning: Sound '{sound_name}' not found")
            
    def play_music(self, music_file: str, loop: bool = True):
        """Play background music"""
        try:
            if self.current_music != music_file:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = music_file
        except Exception as e:
            print(f"Warning: Could not play music '{music_file}': {e}")
            
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def update(self):
        """Update audio manager (called each frame)"""
        # Handle any audio updates needed
        pass