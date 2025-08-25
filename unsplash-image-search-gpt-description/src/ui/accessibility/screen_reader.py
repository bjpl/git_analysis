"""
Screen reader support for Tkinter applications.
Provides text-to-speech announcements and integration with system screen readers.
"""

import tkinter as tk
from typing import Optional, Dict, Any
import platform
import subprocess
import threading
import time


class ScreenReaderSupport:
    """
    Screen reader integration and text-to-speech support.
    Provides announcements and accessible content reading.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.system = platform.system().lower()
        self.tts_available = False
        self.screen_reader_detected = False
        
        # Initialize TTS engine
        self._init_tts()
        
        # Detect system screen reader
        self._detect_screen_reader()
        
        # Live region for announcements (Windows NVDA/JAWS compatible)
        self.live_region = None
        self._setup_live_region()
    
    def _init_tts(self):
        """Initialize text-to-speech engine."""
        try:
            if self.system == "windows":
                # Use Windows SAPI
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self._configure_tts_engine()
                self.tts_available = True
                print("TTS: Windows SAPI initialized")
            
            elif self.system == "darwin":  # macOS
                # macOS has built-in 'say' command
                result = subprocess.run(['which', 'say'], capture_output=True)
                if result.returncode == 0:
                    self.tts_available = True
                    print("TTS: macOS 'say' command available")
            
            elif self.system == "linux":
                # Try espeak or festival
                for cmd in ['espeak', 'festival', 'spd-say']:
                    result = subprocess.run(['which', cmd], capture_output=True)
                    if result.returncode == 0:
                        self.tts_command = cmd
                        self.tts_available = True
                        print(f"TTS: Linux '{cmd}' available")
                        break
        
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            self.tts_available = False
    
    def _configure_tts_engine(self):
        """Configure TTS engine settings."""
        if hasattr(self, 'tts_engine') and self.tts_engine:
            try:
                # Set speech rate (words per minute)
                self.tts_engine.setProperty('rate', 200)
                
                # Set volume (0.0 to 1.0)
                self.tts_engine.setProperty('volume', 0.8)
                
                # Try to set a clear voice
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available (often clearer)
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            except Exception as e:
                print(f"TTS configuration error: {e}")
    
    def _detect_screen_reader(self):
        """Detect if a screen reader is running."""
        try:
            if self.system == "windows":
                # Check for common Windows screen readers
                import psutil
                processes = [p.name().lower() for p in psutil.process_iter()]
                
                screen_readers = [
                    'nvda.exe', 'jaws.exe', 'windoweyes.exe',
                    'supernova.exe', 'dolphin.exe', 'narrator.exe'
                ]
                
                for sr in screen_readers:
                    if sr in processes:
                        self.screen_reader_detected = True
                        print(f"Screen reader detected: {sr}")
                        break
            
            elif self.system == "darwin":
                # Check if VoiceOver is running
                result = subprocess.run(
                    ['launchctl', 'list', 'com.apple.VoiceOver'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.screen_reader_detected = True
                    print("Screen reader detected: VoiceOver")
            
            elif self.system == "linux":
                # Check for Orca
                result = subprocess.run(['pgrep', 'orca'], capture_output=True)
                if result.returncode == 0:
                    self.screen_reader_detected = True
                    print("Screen reader detected: Orca")
        
        except Exception as e:
            print(f"Screen reader detection failed: {e}")
    
    def _setup_live_region(self):
        """Setup live region for screen reader announcements."""
        try:
            # Create a hidden label that screen readers can monitor
            self.live_region = tk.Label(
                text="",
                fg="white",
                bg="white",
                width=1,
                height=1,
                font=("Arial", 1)
            )
            # Position off-screen but still accessible
            self.live_region.place(x=-1000, y=-1000)
            
        except Exception as e:
            print(f"Live region setup failed: {e}")
    
    def announce(self, message: str, priority: str = "polite", interrupt: bool = False):
        """
        Announce message to screen readers and TTS.
        
        Args:
            message: Text to announce
            priority: "polite" (default) or "assertive" 
            interrupt: Whether to interrupt current speech
        """
        if not message.strip():
            return
        
        # Clean and format message
        clean_message = self._clean_message(message)
        
        # Thread the announcement to avoid blocking UI
        threading.Thread(
            target=self._do_announce,
            args=(clean_message, priority, interrupt),
            daemon=True
        ).start()
    
    def _do_announce(self, message: str, priority: str, interrupt: bool):
        """Internal method to handle announcement."""
        try:
            # Update live region for screen readers
            if self.live_region:
                self.live_region.configure(text=message)
                # Clear after a moment to allow re-announcing same message
                self.live_region.after(100, lambda: self.live_region.configure(text=""))
            
            # Use TTS if no screen reader detected or explicitly requested
            if self.tts_available and (not self.screen_reader_detected or priority == "assertive"):
                self._speak_tts(message, interrupt)
            
            # Also try system-specific screen reader integration
            self._system_announce(message, priority)
        
        except Exception as e:
            print(f"Announcement failed: {e}")
    
    def _clean_message(self, message: str) -> str:
        """Clean message for better speech synthesis."""
        # Remove excessive punctuation
        import re
        message = re.sub(r'[^\w\s.,!?-]', ' ', message)
        
        # Replace common UI terms with more speakable versions
        replacements = {
            'btn': 'button',
            'lbl': 'label',
            'txt': 'text',
            'chk': 'checkbox',
            'rad': 'radio button',
            'lst': 'list',
            'cmb': 'combo box',
            'dlg': 'dialog',
            'frm': 'form',
            'tab': 'tab',
            'pg': 'page',
            '&': 'and',
            '@': 'at',
            '#': 'number',
            '%': 'percent',
            '$': 'dollar'
        }
        
        for abbrev, full in replacements.items():
            message = message.replace(abbrev, full)
        
        # Normalize whitespace
        message = ' '.join(message.split())
        
        return message
    
    def _speak_tts(self, message: str, interrupt: bool = False):
        """Speak message using TTS engine."""
        try:
            if self.system == "windows" and hasattr(self, 'tts_engine'):
                if interrupt:
                    self.tts_engine.stop()
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            
            elif self.system == "darwin":
                cmd = ['say', message]
                if interrupt:
                    # Kill existing say processes
                    subprocess.run(['killall', 'say'], capture_output=True)
                subprocess.run(cmd, capture_output=True)
            
            elif self.system == "linux" and hasattr(self, 'tts_command'):
                if self.tts_command == 'espeak':
                    cmd = ['espeak', message]
                elif self.tts_command == 'festival':
                    cmd = ['festival', '--tts']
                    subprocess.run(cmd, input=message, text=True, capture_output=True)
                    return
                elif self.tts_command == 'spd-say':
                    cmd = ['spd-say', message]
                
                if interrupt:
                    # Kill existing TTS processes
                    subprocess.run(['killall', self.tts_command], capture_output=True)
                subprocess.run(cmd, capture_output=True)
        
        except Exception as e:
            print(f"TTS speech failed: {e}")
    
    def _system_announce(self, message: str, priority: str):
        """Use system-specific announcement methods."""
        try:
            if self.system == "windows":
                # Windows: Try to use UI Automation announcements
                self._windows_announce(message, priority)
            
            elif self.system == "darwin":
                # macOS: Use AppleScript to announce
                script = f'''
                tell application "System Events"
                    set output volume 50
                end tell
                do shell script "say '{message}'"
                '''
                subprocess.run(['osascript', '-e', script], capture_output=True)
            
            elif self.system == "linux":
                # Linux: Try AT-SPI announcements
                self._linux_announce(message, priority)
        
        except Exception as e:
            print(f"System announcement failed: {e}")
    
    def _windows_announce(self, message: str, priority: str):
        """Windows-specific announcement using UI Automation."""
        try:
            # Try using Windows UI Automation for NVDA/JAWS compatibility
            import ctypes
            from ctypes import wintypes
            
            # Use Windows API to create announcement
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            # Create a temporary message-only window for announcements
            # This is compatible with NVDA's UI Automation support
            pass  # Implementation would require more complex Windows API calls
        
        except Exception as e:
            print(f"Windows announcement failed: {e}")
    
    def _linux_announce(self, message: str, priority: str):
        """Linux-specific announcement using AT-SPI."""
        try:
            # Try using speech-dispatcher
            subprocess.run(['spd-say', '-p', priority, message], capture_output=True)
        except Exception:
            # Fallback to simple TTS
            pass
    
    def read_widget_info(self, widget: tk.Widget) -> str:
        """Generate readable description of widget for screen readers."""
        try:
            widget_class = widget.__class__.__name__
            
            # Get basic widget info
            info_parts = []
            
            # Widget type
            readable_type = self._get_readable_widget_type(widget_class)
            info_parts.append(readable_type)
            
            # Widget text/value
            text = self._get_widget_text(widget)
            if text:
                info_parts.append(text)
            
            # Widget state
            state = self._get_widget_state(widget)
            if state:
                info_parts.append(state)
            
            # Accessibility attributes if present
            if hasattr(widget, '_accessibility'):
                acc = widget._accessibility
                if acc._accessible_name:
                    info_parts.insert(0, acc._accessible_name)
                if acc._accessible_description:
                    info_parts.append(acc._accessible_description)
            
            return ", ".join(info_parts)
        
        except Exception as e:
            print(f"Widget info reading failed: {e}")
            return f"{widget.__class__.__name__}"
    
    def _get_readable_widget_type(self, widget_class: str) -> str:
        """Convert widget class name to readable type."""
        type_map = {
            'Button': 'button',
            'Label': 'text',
            'Entry': 'text input',
            'Text': 'text area',
            'Listbox': 'list',
            'Checkbutton': 'checkbox',
            'Radiobutton': 'radio button',
            'Scale': 'slider',
            'Scrollbar': 'scrollbar',
            'Frame': 'group',
            'LabelFrame': 'group',
            'Toplevel': 'dialog',
            'Canvas': 'canvas',
            'Menu': 'menu',
            'Menubutton': 'menu button',
            'OptionMenu': 'dropdown',
            'PanedWindow': 'paned window',
            'Spinbox': 'spin box',
            'Combobox': 'combo box',
            'Treeview': 'tree view',
            'Notebook': 'tabs',
            'Progressbar': 'progress bar',
            'Separator': 'separator'
        }
        
        return type_map.get(widget_class, widget_class.lower())
    
    def _get_widget_text(self, widget: tk.Widget) -> str:
        """Extract readable text from widget."""
        try:
            # Try common text properties
            for prop in ['text', 'textvariable']:
                if hasattr(widget, prop):
                    value = getattr(widget, prop)
                    if value:
                        if hasattr(value, 'get'):  # StringVar
                            text = value.get()
                        else:
                            text = str(value)
                        if text.strip():
                            return text.strip()
            
            # Special cases
            if hasattr(widget, 'get'):
                try:
                    value = widget.get()
                    if isinstance(value, str) and value.strip():
                        return value.strip()
                except:
                    pass
            
            return ""
        except:
            return ""
    
    def _get_widget_state(self, widget: tk.Widget) -> str:
        """Get widget state description."""
        try:
            state_info = []
            
            # Check if disabled
            if hasattr(widget, 'cget'):
                try:
                    state = widget.cget('state')
                    if state == 'disabled':
                        state_info.append('disabled')
                    elif state == 'readonly':
                        state_info.append('read only')
                except:
                    pass
            
            # Check selection state for checkboxes/radio buttons
            if hasattr(widget, 'cget'):
                try:
                    var = widget.cget('variable')
                    if var and hasattr(var, 'get'):
                        value = var.get()
                        if widget.__class__.__name__ in ['Checkbutton', 'Radiobutton']:
                            if value:
                                state_info.append('checked')
                            else:
                                state_info.append('unchecked')
                except:
                    pass
            
            return ", ".join(state_info)
        except:
            return ""
    
    def stop_speech(self):
        """Stop all current speech output."""
        try:
            if self.tts_available:
                if hasattr(self, 'tts_engine'):
                    self.tts_engine.stop()
                
                if self.system == "darwin":
                    subprocess.run(['killall', 'say'], capture_output=True)
                
                elif self.system == "linux" and hasattr(self, 'tts_command'):
                    subprocess.run(['killall', self.tts_command], capture_output=True)
        
        except Exception as e:
            print(f"Stop speech failed: {e}")
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if screen reader support is available."""
        instance = cls()
        return instance.tts_available or instance.screen_reader_detected