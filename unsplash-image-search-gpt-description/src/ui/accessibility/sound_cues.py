"""
Sound cues and audio feedback system for accessibility.
Provides audio notifications and feedback for user actions.
"""

import tkinter as tk
from typing import Dict, Optional, Any
import threading
import time
import platform
import os
import tempfile
from io import BytesIO


class SoundManager:
    """
    Manages sound cues and audio feedback for accessibility.
    Provides various sound types for different user interactions.
    """
    
    def __init__(self):
        self.enabled = True
        self.volume = 0.7  # 0.0 to 1.0
        self.sound_cache: Dict[str, Any] = {}
        self.system = platform.system().lower()
        
        # Initialize audio backend
        self.audio_backend = self._init_audio_backend()
        
        # Generate sound cues
        self._generate_sound_cues()
    
    def _init_audio_backend(self) -> Optional[str]:
        """Initialize audio backend based on platform and available libraries."""
        backends_to_try = []
        
        if self.system == "windows":
            backends_to_try = ['winsound', 'pygame', 'pydub']
        elif self.system == "darwin":  # macOS
            backends_to_try = ['pygame', 'pydub', 'system']
        else:  # Linux
            backends_to_try = ['pygame', 'pydub', 'system']
        
        for backend in backends_to_try:
            if self._test_backend(backend):
                print(f"Audio backend: {backend}")
                return backend
        
        print("No audio backend available")
        return None
    
    def _test_backend(self, backend: str) -> bool:
        """Test if audio backend is available."""
        try:
            if backend == 'winsound':
                import winsound
                return True
            elif backend == 'pygame':
                import pygame
                pygame.mixer.init()
                return True
            elif backend == 'pydub':
                from pydub import AudioSegment
                from pydub.playback import play
                return True
            elif backend == 'system':
                return True  # System commands are usually available
            
        except ImportError:
            return False
        except Exception:
            return False
        
        return False
    
    def _generate_sound_cues(self):
        """Generate various sound cues programmatically."""
        # Only generate if we have an audio backend
        if not self.audio_backend:
            return
        
        try:
            if self.audio_backend == 'pygame':
                self._generate_pygame_sounds()
            elif self.audio_backend == 'pydub':
                self._generate_pydub_sounds()
            else:
                self._use_system_sounds()
        
        except Exception as e:
            print(f"Sound generation failed: {e}")
            self._use_system_sounds()
    
    def _generate_pygame_sounds(self):
        """Generate sounds using pygame."""
        try:
            import pygame
            import numpy as np
            
            # Initialize mixer with specific settings
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            
            sample_rate = 22050
            
            def generate_tone(frequency, duration, volume=0.5):
                """Generate a tone using numpy."""
                frames = int(duration * sample_rate)
                arr = np.zeros((frames, 2), dtype=np.int16)
                
                # Generate sine wave
                wave_array = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
                wave_array = (wave_array * 32767 * volume).astype(np.int16)
                
                # Stereo
                arr[:, 0] = wave_array
                arr[:, 1] = wave_array
                
                return pygame.sndarray.make_sound(arr)
            
            def generate_chord(frequencies, duration, volume=0.3):
                """Generate a chord from multiple frequencies."""
                frames = int(duration * sample_rate)
                arr = np.zeros((frames, 2), dtype=np.float32)
                
                for freq in frequencies:
                    wave = np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
                    arr[:, 0] += wave
                    arr[:, 1] += wave
                
                # Normalize and convert
                arr = arr / len(frequencies)
                arr = (arr * 32767 * volume).astype(np.int16)
                
                return pygame.sndarray.make_sound(arr)
            
            # Generate various sound cues
            self.sound_cache['success'] = generate_chord([523, 659, 784], 0.5)  # C major chord
            self.sound_cache['error'] = generate_tone(200, 0.8, 0.6)  # Low tone
            self.sound_cache['warning'] = generate_tone(800, 0.3, 0.5)  # High tone
            self.sound_cache['info'] = generate_tone(440, 0.2, 0.4)  # A note
            self.sound_cache['click'] = generate_tone(1000, 0.1, 0.3)  # Short click
            self.sound_cache['focus'] = generate_tone(660, 0.15, 0.2)  # Focus sound
            self.sound_cache['notification'] = generate_chord([440, 554, 659], 0.3)  # Pleasant chord
            
            print("Generated pygame sound cues")
            
        except ImportError:
            print("Pygame not available for sound generation")
            self._use_system_sounds()
        except Exception as e:
            print(f"Pygame sound generation failed: {e}")
            self._use_system_sounds()
    
    def _generate_pydub_sounds(self):
        """Generate sounds using pydub."""
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine, Square
            
            # Generate various tones
            self.sound_cache['success'] = (
                Sine(523).to_audio_segment(duration=200) +  # C
                Sine(659).to_audio_segment(duration=200) +  # E
                Sine(784).to_audio_segment(duration=300)    # G
            )
            
            self.sound_cache['error'] = Square(200).to_audio_segment(duration=800)
            self.sound_cache['warning'] = Sine(800).to_audio_segment(duration=300)
            self.sound_cache['info'] = Sine(440).to_audio_segment(duration=200)
            self.sound_cache['click'] = Sine(1000).to_audio_segment(duration=100)
            self.sound_cache['focus'] = Sine(660).to_audio_segment(duration=150)
            
            # Notification - ascending tones
            self.sound_cache['notification'] = (
                Sine(440).to_audio_segment(duration=150) +
                Sine(554).to_audio_segment(duration=150) +
                Sine(659).to_audio_segment(duration=200)
            )
            
            print("Generated pydub sound cues")
            
        except ImportError:
            print("Pydub not available for sound generation")
            self._use_system_sounds()
        except Exception as e:
            print(f"Pydub sound generation failed: {e}")
            self._use_system_sounds()
    
    def _use_system_sounds(self):
        """Use system default sounds."""
        # Map to system sound events
        if self.system == "windows":
            self.sound_cache = {
                'success': 'SystemAsterisk',
                'error': 'SystemHand',
                'warning': 'SystemExclamation',
                'info': 'SystemDefault',
                'click': 'SystemDefault',
                'focus': 'MenuCommand',
                'notification': 'SystemAsterisk'
            }
        else:
            # For non-Windows systems, use simple bell
            self.sound_cache = {
                'success': 'bell',
                'error': 'bell',
                'warning': 'bell',
                'info': 'bell',
                'click': 'bell',
                'focus': 'bell',
                'notification': 'bell'
            }
    
    def play_sound(self, sound_type: str):
        """
        Play a sound cue.
        
        Args:
            sound_type: Type of sound ('success', 'error', 'warning', 'info', 'click', 'focus', 'notification')
        """
        if not self.enabled or not self.audio_backend:
            return
        
        if sound_type not in self.sound_cache:
            sound_type = 'info'  # Default fallback
        
        # Play sound in background thread to avoid blocking UI
        threading.Thread(
            target=self._play_sound_threaded,
            args=(sound_type,),
            daemon=True
        ).start()
    
    def _play_sound_threaded(self, sound_type: str):
        """Play sound in background thread."""
        try:
            sound_data = self.sound_cache[sound_type]
            
            if self.audio_backend == 'pygame':
                import pygame
                if isinstance(sound_data, pygame.mixer.Sound):
                    sound_data.set_volume(self.volume)
                    sound_data.play()
                
            elif self.audio_backend == 'pydub':
                from pydub.playback import play
                from pydub import AudioSegment
                if isinstance(sound_data, AudioSegment):
                    # Adjust volume
                    volume_db = 20 * (self.volume - 1)  # Convert to dB
                    adjusted_sound = sound_data + volume_db
                    play(adjusted_sound)
                
            elif self.audio_backend == 'winsound':
                import winsound
                if isinstance(sound_data, str):
                    if sound_data.startswith('System'):
                        # Play system sound
                        winsound.PlaySound(sound_data, winsound.SND_ALIAS | winsound.SND_ASYNC)
                    else:
                        # Play default sound
                        winsound.MessageBeep(winsound.MB_OK)
                
            elif self.audio_backend == 'system':
                if self.system == "darwin":  # macOS
                    if sound_type == 'error':
                        os.system('afplay /System/Library/Sounds/Basso.aiff &')
                    elif sound_type == 'success':
                        os.system('afplay /System/Library/Sounds/Glass.aiff &')
                    elif sound_type == 'warning':
                        os.system('afplay /System/Library/Sounds/Funk.aiff &')
                    else:
                        os.system('afplay /System/Library/Sounds/Pop.aiff &')
                
                elif self.system == "linux":
                    # Use system bell or paplay/aplay
                    try:
                        if sound_type == 'error':
                            os.system('paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null &')
                        else:
                            os.system('echo -e "\a" &')  # Bell sound
                    except:
                        pass
                
                else:  # Windows fallback
                    import winsound
                    winsound.MessageBeep(winsound.MB_OK)
        
        except Exception as e:
            print(f"Sound playback failed: {e}")
    
    # Convenience methods for common sounds
    def play_success(self):
        """Play success sound."""
        self.play_sound('success')
    
    def play_error(self):
        """Play error sound."""
        self.play_sound('error')
    
    def play_warning(self):
        """Play warning sound."""
        self.play_sound('warning')
    
    def play_info(self):
        """Play information sound."""
        self.play_sound('info')
    
    def play_click(self):
        """Play click sound for button presses."""
        self.play_sound('click')
    
    def play_focus(self):
        """Play focus sound for navigation."""
        self.play_sound('focus')
    
    def play_notification(self):
        """Play notification sound."""
        self.play_sound('notification')
    
    def set_volume(self, volume: float):
        """Set volume level (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sound cues."""
        self.enabled = enabled
    
    def is_available(self) -> bool:
        """Check if sound system is available."""
        return self.audio_backend is not None
    
    def test_sounds(self):
        """Test all sound types."""
        if not self.enabled:
            print("Sound cues are disabled")
            return
        
        sound_types = ['success', 'error', 'warning', 'info', 'click', 'focus', 'notification']
        
        for sound_type in sound_types:
            print(f"Playing {sound_type} sound...")
            self.play_sound(sound_type)
            time.sleep(1)  # Wait between sounds
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            if self.audio_backend == 'pygame':
                import pygame
                pygame.mixer.quit()
        except:
            pass
        
        self.sound_cache.clear()


class AudioFeedback:
    """
    High-level audio feedback system for user interface events.
    Provides contextual audio cues for accessibility.
    """
    
    def __init__(self, sound_manager: Optional[SoundManager] = None):
        self.sound_manager = sound_manager or SoundManager()
        self.feedback_enabled = True
        self.last_feedback_time = {}
        self.min_feedback_interval = 0.1  # Minimum time between same sound types
    
    def button_clicked(self):
        """Audio feedback for button clicks."""
        if self._should_play_feedback('click'):
            self.sound_manager.play_click()
    
    def element_focused(self):
        """Audio feedback for element focus changes."""
        if self._should_play_feedback('focus'):
            self.sound_manager.play_focus()
    
    def form_submitted(self):
        """Audio feedback for successful form submission."""
        if self._should_play_feedback('success'):
            self.sound_manager.play_success()
    
    def validation_error(self):
        """Audio feedback for validation errors."""
        if self._should_play_feedback('error'):
            self.sound_manager.play_error()
    
    def field_warning(self):
        """Audio feedback for field warnings."""
        if self._should_play_feedback('warning'):
            self.sound_manager.play_warning()
    
    def information_displayed(self):
        """Audio feedback for information messages."""
        if self._should_play_feedback('info'):
            self.sound_manager.play_info()
    
    def notification_received(self):
        """Audio feedback for notifications."""
        if self._should_play_feedback('notification'):
            self.sound_manager.play_notification()
    
    def page_loaded(self):
        """Audio feedback for page/dialog loading."""
        if self._should_play_feedback('success'):
            self.sound_manager.play_success()
    
    def action_completed(self):
        """Audio feedback for completed actions."""
        if self._should_play_feedback('success'):
            self.sound_manager.play_success()
    
    def action_cancelled(self):
        """Audio feedback for cancelled actions."""
        if self._should_play_feedback('warning'):
            self.sound_manager.play_warning()
    
    def search_completed(self, has_results: bool):
        """Audio feedback for search completion."""
        if has_results:
            self.information_displayed()
        else:
            self.field_warning()
    
    def menu_opened(self):
        """Audio feedback for menu opening."""
        if self._should_play_feedback('info'):
            self.sound_manager.play_info()
    
    def dialog_opened(self):
        """Audio feedback for dialog opening."""
        if self._should_play_feedback('info'):
            self.sound_manager.play_info()
    
    def tab_changed(self):
        """Audio feedback for tab changes."""
        if self._should_play_feedback('click'):
            self.sound_manager.play_click()
    
    def _should_play_feedback(self, feedback_type: str) -> bool:
        """Check if feedback should be played (rate limiting)."""
        if not self.feedback_enabled or not self.sound_manager.enabled:
            return False
        
        current_time = time.time()
        last_time = self.last_feedback_time.get(feedback_type, 0)
        
        if current_time - last_time >= self.min_feedback_interval:
            self.last_feedback_time[feedback_type] = current_time
            return True
        
        return False
    
    def set_enabled(self, enabled: bool):
        """Enable or disable audio feedback."""
        self.feedback_enabled = enabled
    
    def set_feedback_rate(self, interval: float):
        """Set minimum interval between feedback sounds."""
        self.min_feedback_interval = max(0.05, interval)


# Widget integration helpers
def add_audio_feedback_to_widget(widget: tk.Widget, feedback: AudioFeedback):
    """Add audio feedback to a widget's events."""
    widget_class = widget.__class__.__name__
    
    if widget_class in ['Button', 'Checkbutton', 'Radiobutton']:
        # Add click feedback
        original_command = widget.cget('command')
        
        def enhanced_command():
            feedback.button_clicked()
            if original_command:
                original_command()
        
        widget.configure(command=enhanced_command)
    
    # Add focus feedback
    widget.bind('<FocusIn>', lambda e: feedback.element_focused(), add='+')
    
    # Add context-specific feedback
    if widget_class == 'Entry':
        widget.bind('<Return>', lambda e: feedback.form_submitted(), add='+')
        widget.bind('<KeyRelease>', lambda e: _validate_entry_field(widget, feedback), add='+')
    
    elif widget_class == 'Text':
        widget.bind('<Control-Return>', lambda e: feedback.form_submitted(), add='+')


def _validate_entry_field(entry: tk.Entry, feedback: AudioFeedback):
    """Validate entry field and provide audio feedback."""
    try:
        value = entry.get()
        
        # Example validation - customize as needed
        if hasattr(entry, '_validation_pattern'):
            import re
            if not re.match(entry._validation_pattern, value):
                feedback.validation_error()
        
        elif hasattr(entry, '_required') and entry._required:
            if not value.strip():
                feedback.field_warning()
    
    except Exception:
        pass