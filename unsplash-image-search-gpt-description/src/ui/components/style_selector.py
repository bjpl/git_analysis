"""
UI component for selecting description styles.
Provides a panel for choosing between Academic, Poetic, and Technical styles.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.features.description_styles import (
        DescriptionStyleManager, 
        DescriptionStyle, 
        VocabularyLevel
    )
except ImportError:
    # Fallback for when running standalone or imports fail
    class DescriptionStyle:
        ACADEMIC = "academic"
        POETIC = "poetic"
        TECHNICAL = "technical"
    
    class VocabularyLevel:
        BEGINNER = "beginner"
        INTERMEDIATE = "intermediate"
        ADVANCED = "advanced"
        NATIVE = "native"
    
    class DescriptionStyleManager:
        def __init__(self):
            self.current_style = DescriptionStyle.ACADEMIC
            self.current_level = VocabularyLevel.INTERMEDIATE


class StyleSelectorPanel(ttk.LabelFrame):
    """
    A panel widget for selecting description styles and vocabulary levels.
    Can be embedded in any tkinter application.
    """
    
    def __init__(self, parent, style_manager: Optional[DescriptionStyleManager] = None,
                 on_style_change: Optional[Callable] = None, **kwargs):
        """
        Initialize the style selector panel.
        
        Args:
            parent: Parent tkinter widget
            style_manager: DescriptionStyleManager instance
            on_style_change: Callback function when style changes
            **kwargs: Additional arguments for ttk.LabelFrame
        """
        super().__init__(parent, text="📝 Description Style", padding="10", **kwargs)
        
        self.style_manager = style_manager or DescriptionStyleManager()
        self.on_style_change = on_style_change
        
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        """Create the panel widgets."""
        # Style selection frame
        style_frame = ttk.Frame(self)
        style_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(style_frame, text="Style:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Style radio buttons
        self.style_var = tk.StringVar(value=self.style_manager.current_style.value
                                      if hasattr(self.style_manager.current_style, 'value')
                                      else str(self.style_manager.current_style))
        
        styles = [
            ("📚 Academic/Neutral", DescriptionStyle.ACADEMIC),
            ("🎨 Poetic/Literary", DescriptionStyle.POETIC),
            ("🔬 Technical/Scientific", DescriptionStyle.TECHNICAL)
        ]
        
        for label, style in styles:
            style_value = style.value if hasattr(style, 'value') else style
            rb = ttk.Radiobutton(
                style_frame,
                text=label,
                variable=self.style_var,
                value=style_value,
                command=self.on_style_selected
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Vocabulary level frame
        level_frame = ttk.Frame(self)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(level_frame, text="Vocabulary Level:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Level dropdown
        self.level_var = tk.StringVar()
        self.level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.level_var,
            values=["Beginner", "Intermediate", "Advanced", "Native"],
            state="readonly",
            width=15
        )
        self.level_combo.pack(side=tk.LEFT, padx=5)
        self.level_combo.bind("<<ComboboxSelected>>", self.on_level_selected)
        
        # Set default level
        current_level = self.style_manager.current_level.value if hasattr(self.style_manager.current_level, 'value') else str(self.style_manager.current_level)
        self.level_combo.set(current_level.capitalize())
        
        # Description preview frame
        preview_frame = ttk.LabelFrame(self, text="Style Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            preview_frame,
            height=4,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Arial', 9)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
    
    def on_style_selected(self):
        """Handle style selection change."""
        style_value = self.style_var.get()
        
        # Convert string to DescriptionStyle enum
        for style in [DescriptionStyle.ACADEMIC, DescriptionStyle.POETIC, DescriptionStyle.TECHNICAL]:
            if (hasattr(style, 'value') and style.value == style_value) or str(style) == style_value:
                self.style_manager.current_style = style
                break
        
        self.update_display()
        
        if self.on_style_change:
            self.on_style_change(self.style_manager.current_style, self.style_manager.current_level)
    
    def on_level_selected(self, event=None):
        """Handle vocabulary level selection change."""
        level_str = self.level_var.get().lower()
        
        # Convert string to VocabularyLevel enum
        for level in [VocabularyLevel.BEGINNER, VocabularyLevel.INTERMEDIATE, 
                     VocabularyLevel.ADVANCED, VocabularyLevel.NATIVE]:
            if (hasattr(level, 'value') and level.value == level_str) or str(level) == level_str:
                self.style_manager.current_level = level
                break
        
        self.update_display()
        
        if self.on_style_change:
            self.on_style_change(self.style_manager.current_style, self.style_manager.current_level)
    
    def update_display(self):
        """Update the preview display with current style information."""
        style = self.style_manager.current_style
        level = self.style_manager.current_level
        
        # Get style name
        style_name = style.value if hasattr(style, 'value') else str(style)
        level_name = level.value if hasattr(level, 'value') else str(level)
        
        # Create preview text based on style
        previews = {
            "academic": {
                "beginner": "Ejemplo: 'En la imagen se observa un paisaje natural. Los colores principales son verde y azul.'",
                "intermediate": "Ejemplo: 'Cabe destacar que la composición presenta elementos contrastantes que sugieren una narrativa visual.'",
                "advanced": "Ejemplo: 'La yuxtaposición de elementos arquitectónicos evidencia una dialéctica entre tradición y modernidad.'",
                "native": "Ejemplo: 'Es menester señalar que la semiótica visual trasciende la mera representación figurativa.'"
            },
            "poetic": {
                "beginner": "Ejemplo: 'Los colores bailan como mariposas. La luz abraza suavemente cada rincón.'",
                "intermediate": "Ejemplo: 'El lienzo respira historias susurradas por el viento, tejiendo memorias en cada trazo.'",
                "advanced": "Ejemplo: 'Como un palimpsesto de emociones, la imagen despliega sus alas oníricas hacia el infinito.'",
                "native": "Ejemplo: 'En el crisol de lo inefable, la epifanía cromática trasciende los límites de la percepción.'"
            },
            "technical": {
                "beginner": "Ejemplo: 'El objeto mide aproximadamente 2 metros. El material parece ser metal con acabado mate.'",
                "intermediate": "Ejemplo: 'Las propiedades ópticas indican una reflexión especular del 30%. La estructura muestra simetría bilateral.'",
                "advanced": "Ejemplo: 'El índice de refracción sugiere un coeficiente de 1.52, compatible con vidrio borosilicato.'",
                "native": "Ejemplo: 'Los vectores compositivos convergen según principios de la geometría fractal con dimensión de Hausdorff aproximada de 1.7.'"
            }
        }
        
        # Get preview text
        preview = previews.get(style_name, {}).get(level_name, "Preview not available")
        
        # Update preview text widget
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, f"Style: {style_name.capitalize()} - {level_name.capitalize()}\n\n")
        self.preview_text.insert(tk.END, preview)
        self.preview_text.config(state=tk.DISABLED)
    
    def get_current_style(self) -> tuple:
        """
        Get the current style and level.
        
        Returns:
            Tuple of (DescriptionStyle, VocabularyLevel)
        """
        return (self.style_manager.current_style, self.style_manager.current_level)
    
    def set_style(self, style: DescriptionStyle, level: VocabularyLevel):
        """
        Set the style and level programmatically.
        
        Args:
            style: The description style
            level: The vocabulary level
        """
        self.style_manager.current_style = style
        self.style_manager.current_level = level
        
        # Update UI
        style_value = style.value if hasattr(style, 'value') else str(style)
        level_value = level.value if hasattr(level, 'value') else str(level)
        
        self.style_var.set(style_value)
        self.level_combo.set(level_value.capitalize())
        
        self.update_display()


class StyleSelectorDialog(tk.Toplevel):
    """
    A dialog window for selecting description styles.
    Can be used as a standalone dialog.
    """
    
    def __init__(self, parent, style_manager: Optional[DescriptionStyleManager] = None):
        """
        Initialize the style selector dialog.
        
        Args:
            parent: Parent window
            style_manager: DescriptionStyleManager instance
        """
        super().__init__(parent)
        
        self.title("Select Description Style")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.style_manager = style_manager or DescriptionStyleManager()
        self.result = None
        
        self.create_widgets()
        
        # Center on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Choose Your Description Style",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Style selector panel
        self.selector_panel = StyleSelectorPanel(
            main_frame,
            self.style_manager,
            on_style_change=self.on_style_change
        )
        self.selector_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Apply",
            command=self.apply_selection
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side=tk.RIGHT)
    
    def on_style_change(self, style, level):
        """Handle style change from selector panel."""
        # Could add additional handling here
        pass
    
    def apply_selection(self):
        """Apply the selected style and close dialog."""
        self.result = self.selector_panel.get_current_style()
        self.destroy()
    
    def cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.destroy()


# Demo application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Style Selector Demo")
    root.geometry("600x500")
    
    # Create style manager
    style_manager = DescriptionStyleManager()
    
    def on_style_change(style, level):
        print(f"Style changed to: {style} - {level}")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add style selector panel
    selector = StyleSelectorPanel(
        main_frame,
        style_manager,
        on_style_change=on_style_change
    )
    selector.pack(fill=tk.X, pady=(0, 20))
    
    # Add button to open dialog
    def open_dialog():
        dialog = StyleSelectorDialog(root, style_manager)
        root.wait_window(dialog)
        if dialog.result:
            print(f"Dialog result: {dialog.result}")
    
    ttk.Button(
        main_frame,
        text="Open Style Dialog",
        command=open_dialog
    ).pack()
    
    root.mainloop()