"""
EyeSpy - Accessibility Assistant
A visual aid application with color detection and accessibility features
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import sys

# Try to import pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not available. Install with: pip install pyautogui")

# -------------------------------
# Constants
# -------------------------------

class Theme:
    """Theme constants for normal and high contrast modes"""
    NORMAL = {
        'bg': '#e8f1ff',
        'fg': '#000000',
        'button_bg': '#4a90e2',
        'button_fg': '#ffffff',
        'accent': '#2c5aa0'
    }
    HIGH_CONTRAST = {
        'bg': '#000000',
        'fg': '#ffff00',
        'button_bg': '#ffff00',
        'button_fg': '#000000',
        'accent': '#ffffff'
    }

class FontSize:
    """Font size constants"""
    SMALL = ('Arial', 10)
    NORMAL = ('Arial', 12)
    LARGE = ('Arial', 16)
    XLARGE = ('Arial', 20)
    TITLE_NORMAL = ('Arial', 24, 'bold')
    TITLE_LARGE = ('Arial', 28, 'bold')

# -------------------------------
# Settings Manager
# -------------------------------

class SettingsManager:
    """Manages user preferences and persistence"""
    
    def __init__(self, filename='eyespy_settings.json'):
        self.filename = filename
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or return defaults"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return self.get_defaults()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_defaults(self):
        """Return default settings"""
        return {
            'vision_type': '',
            'large_text': False,
            'screen_reader': False,
            'high_contrast': False,
            'activities': {
                'gaming': {
                    'enabled': False,
                    'colorblind_mode': False,
                    'audio_cues': False,
                    'enlarged_ui': False
                },
                'studying': {
                    'enabled': False,
                    'reading_guide': False,
                    'gentle_reminders': False,
                    'text_to_speech': False,
                    'dyslexia_font': False
                },
                'browsing': {
                    'enabled': False,
                    'auto_captions': False,
                    'reduce_motion': False,
                    'link_highlighting': False
                }
            },
            'color_identifier': True
        }
    
    def update(self, key, value):
        """Update a setting"""
        self.settings[key] = value
        self.save_settings()
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

# -------------------------------
# Main Application
# -------------------------------

class EyeSpyApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("EyeSpy - Accessibility Assistant")
        self.root.geometry("700x850")
        
        # Prevent window from being too small
        self.root.minsize(600, 700)
        
        # Settings manager
        self.settings = SettingsManager()
        
        # App state
        self.current_activity_index = 0
        self.selected_activities = []
        
        # Get theme
        self.update_theme()
        
        # Configure root window
        self.root.configure(bg=self.current_theme['bg'])
        
        # Create menu bar
        self.create_menu()
        
        # Container for frames
        self.container = tk.Frame(self.root, bg=self.current_theme['bg'])
        self.container.pack(fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create frames
        self.frames = {}
        self.create_frames()
        
        # Bind keyboard shortcuts (multiple bindings for compatibility)
        self.bind_shortcuts()
        
        # Show appropriate frame
        if not self.settings.get('vision_type'):
            self.show_frame('survey')
        else:
            self.show_frame('home')
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_theme(self):
        """Update current theme based on settings"""
        self.current_theme = Theme.HIGH_CONTRAST if self.settings.get('high_contrast') else Theme.NORMAL
    
    def create_menu(self):
        """Create menu bar for navigation"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Home", command=lambda: self.show_frame('home'), accelerator="Ctrl+H")
        file_menu.add_command(label="Settings", command=lambda: self.show_frame('survey'), accelerator="Ctrl+,")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Color Identifier", command=self.open_accessibility_window, accelerator="Ctrl+I")
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts with multiple variations for compatibility"""
        # Home shortcuts
        self.root.bind('<Control-h>', lambda e: self.show_frame('home'))
        self.root.bind('<Control-H>', lambda e: self.show_frame('home'))
        
        # Settings shortcuts (using comma like many apps)
        self.root.bind('<Control-comma>', lambda e: self.show_frame('survey'))
        self.root.bind('<Control-s>', lambda e: self.show_frame('survey'))
        self.root.bind('<Control-S>', lambda e: self.show_frame('survey'))
        
        # Color Identifier shortcuts (I for Identifier, avoiding C for copy)
        self.root.bind('<Control-i>', lambda e: self.open_accessibility_window())
        self.root.bind('<Control-I>', lambda e: self.open_accessibility_window())
        
        # Quit shortcuts
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-Q>', lambda e: self.on_closing())
        
        # Platform-specific shortcuts
        if sys.platform == 'darwin':  # macOS
            self.root.bind('<Command-h>', lambda e: self.show_frame('home'))
            self.root.bind('<Command-comma>', lambda e: self.show_frame('survey'))
            self.root.bind('<Command-i>', lambda e: self.open_accessibility_window())
            self.root.bind('<Command-q>', lambda e: self.on_closing())
    
    def create_frames(self):
        """Create all application frames"""
        try:
            self.frames['survey'] = SurveyFrame(self.container, self)
            self.frames['home'] = HomeFrame(self.container, self)
            self.frames['gaming'] = GamingFrame(self.container, self)
            self.frames['studying'] = StudyingFrame(self.container, self)
            self.frames['browsing'] = BrowsingFrame(self.container, self)
            
            # Grid all frames in same location
            for frame in self.frames.values():
                frame.grid(row=0, column=0, sticky='nsew')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create frames: {e}")
            print(f"Frame creation error: {e}")
    
    def show_frame(self, frame_name):
        """Show a specific frame"""
        try:
            frame = self.frames.get(frame_name)
            if frame:
                frame.tkraise()
                frame.focus_set()
            else:
                print(f"Warning: Frame '{frame_name}' not found")
        except Exception as e:
            print(f"Error showing frame {frame_name}: {e}")
    
    def apply_theme(self):
        """Apply current theme to all widgets"""
        self.update_theme()
        self.root.configure(bg=self.current_theme['bg'])
        self.container.configure(bg=self.current_theme['bg'])
        
        # Reapply theme to all frames
        for frame in self.frames.values():
            if hasattr(frame, 'apply_theme'):
                frame.apply_theme()
    
    def get_font(self, style='normal'):
        """Get font based on user preference and style"""
        if self.settings.get('large_text'):
            if style == 'title':
                return FontSize.TITLE_LARGE
            return FontSize.LARGE
        else:
            if style == 'title':
                return FontSize.TITLE_NORMAL
            return FontSize.NORMAL
    
    def open_accessibility_window(self):
        """Open the accessibility tools window"""
        if not PYAUTOGUI_AVAILABLE:
            messagebox.showwarning(
                "PyAutoGUI Not Available",
                "Color identifier requires pyautogui.\n\nInstall with:\npip install pyautogui"
            )
            return
        try:
            AccessibilityWindow(self.root, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open accessibility tools: {e}")
            print(f"Accessibility window error: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        try:
            self.settings.save_settings()
            self.root.quit()
            self.root.destroy()
        except:
            self.root.destroy()

# -------------------------------
# Base Frame Class
# -------------------------------

class BaseFrame(tk.Frame):
    """Base frame with common functionality"""
    
    def __init__(self, parent, app):
        self.app = app
        theme = app.current_theme
        super().__init__(parent, bg=theme['bg'])
        self.widgets = []  # Track widgets for theme updates
    
    def create_label(self, text, font_style='normal', **kwargs):
        """Create a themed label"""
        theme = self.app.current_theme
        font = self.app.get_font(font_style)
        
        # Remove font from kwargs if present to avoid conflict
        kwargs.pop('font', None)
        
        label = tk.Label(
            self,
            text=text,
            font=font,
            bg=theme['bg'],
            fg=theme['fg'],
            **kwargs
        )
        self.widgets.append(label)
        return label
    
    def create_button(self, text, command, **kwargs):
        """Create a themed button"""
        theme = self.app.current_theme
        font = self.app.get_font()
        
        # Remove conflicting kwargs if present
        kwargs.pop('font', None)
        kwargs.pop('bg', None)
        kwargs.pop('fg', None)
        kwargs.pop('activebackground', None)
        kwargs.pop('activeforeground', None)
        
        button = tk.Button(
            self,
            text=text,
            command=command,
            font=font,
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['accent'],
            activeforeground=theme['button_fg'],
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            cursor='hand2',
            **kwargs
        )
        self.widgets.append(button)
        return button
    
    def create_checkbutton(self, text, variable, **kwargs):
        """Create a themed checkbutton"""
        theme = self.app.current_theme
        font = self.app.get_font()
        
        # Remove conflicting kwargs if present
        kwargs.pop('font', None)
        kwargs.pop('bg', None)
        kwargs.pop('fg', None)
        kwargs.pop('selectcolor', None)
        kwargs.pop('activebackground', None)
        kwargs.pop('activeforeground', None)
        
        check = tk.Checkbutton(
            self,
            text=text,
            variable=variable,
            bg=theme['bg'],
            fg=theme['fg'],
            selectcolor=theme['bg'],
            font=font,
            activebackground=theme['bg'],
            activeforeground=theme['fg'],
            **kwargs
        )
        self.widgets.append(check)
        return check
    
    def apply_theme(self):
        """Apply theme to frame and children"""
        theme = self.app.current_theme
        self.configure(bg=theme['bg'])
        
        # Update all tracked widgets
        for widget in self.widgets:
            try:
                if isinstance(widget, tk.Label):
                    widget.configure(bg=theme['bg'], fg=theme['fg'], font=self.app.get_font())
                elif isinstance(widget, tk.Button):
                    widget.configure(
                        bg=theme['button_bg'], 
                        fg=theme['button_fg'],
                        font=self.app.get_font()
                    )
                elif isinstance(widget, tk.Checkbutton):
                    widget.configure(
                        bg=theme['bg'], 
                        fg=theme['fg'],
                        selectcolor=theme['bg'],
                        font=self.app.get_font()
                    )
            except Exception as e:
                print(f"Error applying theme to widget: {e}")
        
        # Update all child widgets recursively
        for widget in self.winfo_children():
            try:
                if isinstance(widget, tk.Radiobutton):
                    widget.configure(
                        bg=theme['bg'], 
                        fg=theme['fg'],
                        selectcolor=theme['bg'],
                        font=self.app.get_font()
                    )
                elif isinstance(widget, tk.LabelFrame):
                    widget.configure(bg=theme['bg'], fg=theme['fg'], font=self.app.get_font())
                elif isinstance(widget, tk.Frame):
                    widget.configure(bg=theme['bg'])
            except Exception as e:
                print(f"Error updating child widget: {e}")

# -------------------------------
# Survey Frame
# -------------------------------

class SurveyFrame(BaseFrame):
    """Initial survey to collect user preferences"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        self.vision_type = tk.StringVar(value=app.settings.get('vision_type', ''))
        self.large_text = tk.BooleanVar(value=app.settings.get('large_text', False))
        self.screen_reader = tk.BooleanVar(value=app.settings.get('screen_reader', False))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create survey widgets"""
        # Title
        title = self.create_label("Welcome to EyeSpy", font_style='title')
        title.pack(pady=20)
        
        # Subtitle
        subtitle = self.create_label(
            "Please complete this survey to customize\nthe app for your needs.",
            justify='center'
        )
        subtitle.pack(pady=10)
        
        # Main survey container
        survey_container = tk.Frame(self, bg=self.app.current_theme['bg'])
        survey_container.pack(pady=20, padx=50, fill='both', expand=True)
        
        # Vision type
        vision_label = self.create_label("What best describes your vision?")
        vision_label.pack(in_=survey_container, anchor='w', pady=(10, 5))
        
        vision_frame = tk.Frame(survey_container, bg=self.app.current_theme['bg'])
        vision_frame.pack(fill='x', pady=5)
        
        vision_options = ["Low vision", "Blind", "Color blindness", "Typical vision", "Other"]
        for option in vision_options:
            rb = tk.Radiobutton(
                vision_frame,
                text=option,
                variable=self.vision_type,
                value=option,
                bg=self.app.current_theme['bg'],
                fg=self.app.current_theme['fg'],
                selectcolor=self.app.current_theme['bg'],
                font=self.app.get_font(),
                activebackground=self.app.current_theme['bg'],
                activeforeground=self.app.current_theme['fg']
            )
            rb.pack(anchor='w', padx=20, pady=2)
        
        # Text size preference
        text_label = self.create_label("Do you prefer larger text?")
        text_label.pack(in_=survey_container, anchor='w', pady=(20, 5))
        
        text_check = self.create_checkbutton(
            "Yes, use larger text throughout the app",
            self.large_text
        )
        text_check.pack(in_=survey_container, anchor='w', padx=20, pady=2)
        
        # Screen reader
        sr_label = self.create_label("Do you use a screen reader?")
        sr_label.pack(in_=survey_container, anchor='w', pady=(20, 5))
        
        sr_check = self.create_checkbutton(
            "Yes, I use a screen reader",
            self.screen_reader
        )
        sr_check.pack(in_=survey_container, anchor='w', padx=20, pady=2)
        
        # Submit button
        submit_btn = self.create_button("Save Preferences", self.submit_survey)
        submit_btn.pack(pady=30)
    
    def submit_survey(self):
        """Save survey results"""
        if not self.vision_type.get():
            messagebox.showerror("Incomplete", "Please select your vision type.")
            return
        
        try:
            # Save settings
            self.app.settings.update('vision_type', self.vision_type.get())
            self.app.settings.update('large_text', self.large_text.get())
            self.app.settings.update('screen_reader', self.screen_reader.get())
            
            # Apply theme changes
            self.app.apply_theme()
            
            messagebox.showinfo(
                "Settings Saved",
                "Your preferences have been saved!\nYou can change them anytime from the File menu."
            )
            
            self.app.show_frame('home')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            print(f"Survey submission error: {e}")

# -------------------------------
# Home Frame
# -------------------------------

class HomeFrame(BaseFrame):
    """Home screen for selecting activities"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        activities = app.settings.get('activities', {})
        self.gaming = tk.BooleanVar(value=activities.get('gaming', {}).get('enabled', False))
        self.studying = tk.BooleanVar(value=activities.get('studying', {}).get('enabled', False))
        self.browsing = tk.BooleanVar(value=activities.get('browsing', {}).get('enabled', False))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create home screen widgets"""
        # Title
        title = self.create_label("EyeSpy Accessibility Assistant", font_style='title')
        title.pack(pady=20)
        
        # Instructions
        instructions = self.create_label(
            "Select the activities you use your device for.\nWe'll customize accessibility features for each.",
            justify='center'
        )
        instructions.pack(pady=10)
        
        # Keyboard shortcut help
        shortcut_help = self.create_label(
            "Tip: Press Ctrl+I to open Color Identifier anytime",
            justify='center'
        )
        shortcut_help.pack(pady=5)
        
        # Activity selection
        activity_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        activity_frame.pack(pady=30, fill='both', expand=True)
        
        activities = [
            (self.gaming, "Gaming", "Optimize for gaming with colorblind modes,\naudio cues, and enlarged UI elements"),
            (self.studying, "Studying / Reading", "Reading guides, gentle reminders,\ntext-to-speech, and dyslexia-friendly fonts"),
            (self.browsing, "Browsing / Watching", "Auto-captions, reduced motion,\nand enhanced link visibility")
        ]
        
        for var, title_text, description in activities:
            frame = tk.LabelFrame(
                activity_frame,
                text=title_text,
                bg=self.app.current_theme['bg'],
                fg=self.app.current_theme['fg'],
                font=self.app.get_font(),
                padx=15,
                pady=10
            )
            frame.pack(fill='x', padx=50, pady=10)
            
            check = self.create_checkbutton(description, var, justify='left')
            check.pack(in_=frame, anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        button_frame.pack(pady=20)
        
        tools_btn = self.create_button("Open Color Identifier (Ctrl+I)", self.app.open_accessibility_window)
        tools_btn.pack(side='left', padx=10)
        
        next_btn = self.create_button("Configure Activities", self.save_and_continue)
        next_btn.pack(side='left', padx=10)
    
    def save_and_continue(self):
        """Save activity selections and move to configuration"""
        try:
            self.app.selected_activities = []
            
            if self.gaming.get():
                self.app.selected_activities.append('gaming')
            if self.studying.get():
                self.app.selected_activities.append('studying')
            if self.browsing.get():
                self.app.selected_activities.append('browsing')
            
            if not self.app.selected_activities:
                messagebox.showwarning("No Selection", "Please select at least one activity.")
                return
            
            # Save enabled status
            for activity in ['gaming', 'studying', 'browsing']:
                self.app.settings.settings['activities'][activity]['enabled'] = activity in self.app.selected_activities
            self.app.settings.save_settings()
            
            self.app.current_activity_index = 0
            self.show_next_activity()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save activities: {e}")
            print(f"Activity save error: {e}")
    
    def show_next_activity(self):
        """Show next activity configuration screen"""
        try:
            if self.app.current_activity_index >= len(self.app.selected_activities):
                messagebox.showinfo(
                    "Setup Complete",
                    "Your activity preferences have been configured!\nClick OK to open Color Identifier."
                )
                self.app.open_accessibility_window()
                return
            
            activity = self.app.selected_activities[self.app.current_activity_index]
            self.app.current_activity_index += 1
            self.app.show_frame(activity)
        except Exception as e:
            messagebox.showerror("Error", f"Navigation error: {e}")
            print(f"Activity navigation error: {e}")

# -------------------------------
# Gaming Frame
# -------------------------------

class GamingFrame(BaseFrame):
    """Gaming accessibility configuration"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        settings = app.settings.get('activities', {}).get('gaming', {})
        self.colorblind_mode = tk.BooleanVar(value=settings.get('colorblind_mode', False))
        self.audio_cues = tk.BooleanVar(value=settings.get('audio_cues', False))
        self.enlarged_ui = tk.BooleanVar(value=settings.get('enlarged_ui', False))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create gaming configuration widgets"""
        title = self.create_label("Gaming Accessibility", font_style='title')
        title.pack(pady=20)
        
        subtitle = self.create_label(
            "Select features to enhance your gaming experience",
            justify='center'
        )
        subtitle.pack(pady=10)
        
        options_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        options_frame.pack(pady=30, padx=50, fill='both', expand=True)
        
        options = [
            (self.colorblind_mode, "Colorblind Mode",
             "Adjust color schemes for better visibility\n(Protanopia, Deuteranopia, Tritanopia support)"),
            (self.audio_cues, "Enhanced Audio Cues",
             "Add audio feedback for visual events\nand important game information"),
            (self.enlarged_ui, "Enlarged UI Elements",
             "Increase size of menus, buttons,\nand HUD elements for better visibility")
        ]
        
        for var, title_text, description in options:
            frame = tk.LabelFrame(
                options_frame,
                text=title_text,
                bg=self.app.current_theme['bg'],
                fg=self.app.current_theme['fg'],
                font=self.app.get_font(),
                padx=15,
                pady=10
            )
            frame.pack(fill='x', pady=10)
            
            check = self.create_checkbutton(description, var, justify='left')
            check.pack(in_=frame, anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        button_frame.pack(pady=20)
        
        back_btn = self.create_button("Back", lambda: self.app.show_frame('home'))
        back_btn.pack(side='left', padx=10)
        
        next_btn = self.create_button("Continue", self.save_and_continue)
        next_btn.pack(side='left', padx=10)
    
    def save_and_continue(self):
        """Save gaming settings"""
        try:
            self.app.settings.settings['activities']['gaming']['colorblind_mode'] = self.colorblind_mode.get()
            self.app.settings.settings['activities']['gaming']['audio_cues'] = self.audio_cues.get()
            self.app.settings.settings['activities']['gaming']['enlarged_ui'] = self.enlarged_ui.get()
            self.app.settings.save_settings()
            
            # Continue to next activity
            home_frame = self.app.frames['home']
            home_frame.show_next_activity()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save gaming settings: {e}")
            print(f"Gaming save error: {e}")

# -------------------------------
# Studying Frame
# -------------------------------

class StudyingFrame(BaseFrame):
    """Studying/Reading accessibility configuration"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        settings = app.settings.get('activities', {}).get('studying', {})
        self.reading_guide = tk.BooleanVar(value=settings.get('reading_guide', False))
        self.gentle_reminders = tk.BooleanVar(value=settings.get('gentle_reminders', False))
        self.text_to_speech = tk.BooleanVar(value=settings.get('text_to_speech', False))
        self.dyslexia_font = tk.BooleanVar(value=settings.get('dyslexia_font', False))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create studying configuration widgets"""
        title = self.create_label("Studying / Reading Accessibility", font_style='title')
        title.pack(pady=20)
        
        subtitle = self.create_label(
            "Select features to enhance reading and studying",
            justify='center'
        )
        subtitle.pack(pady=10)
        
        options_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        options_frame.pack(pady=30, padx=50, fill='both', expand=True)
        
        options = [
            (self.reading_guide, "Reading Guide",
             "Highlight current line or paragraph\nfor easier text tracking"),
            (self.gentle_reminders, "Break Reminders",
             "Gentle notifications to take breaks\nafter extended reading sessions"),
            (self.text_to_speech, "Text-to-Speech",
             "Read selected text aloud\nwith adjustable speed and voice"),
            (self.dyslexia_font, "Dyslexia-Friendly Font",
             "Use OpenDyslexic or similar fonts\nfor improved readability")
        ]
        
        for var, title_text, description in options:
            frame = tk.LabelFrame(
                options_frame,
                text=title_text,
                bg=self.app.current_theme['bg'],
                fg=self.app.current_theme['fg'],
                font=self.app.get_font(),
                padx=15,
                pady=10
            )
            frame.pack(fill='x', pady=10)
            
            check = self.create_checkbutton(description, var, justify='left')
            check.pack(in_=frame, anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        button_frame.pack(pady=20)
        
        back_btn = self.create_button("Back", lambda: self.app.show_frame('home'))
        back_btn.pack(side='left', padx=10)
        
        next_btn = self.create_button("Continue", self.save_and_continue)
        next_btn.pack(side='left', padx=10)
    
    def save_and_continue(self):
        """Save studying settings"""
        try:
            self.app.settings.settings['activities']['studying']['reading_guide'] = self.reading_guide.get()
            self.app.settings.settings['activities']['studying']['gentle_reminders'] = self.gentle_reminders.get()
            self.app.settings.settings['activities']['studying']['text_to_speech'] = self.text_to_speech.get()
            self.app.settings.settings['activities']['studying']['dyslexia_font'] = self.dyslexia_font.get()
            self.app.settings.save_settings()
            
            # Continue to next activity
            home_frame = self.app.frames['home']
            home_frame.show_next_activity()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save studying settings: {e}")
            print(f"Studying save error: {e}")

# -------------------------------
# Browsing Frame
# -------------------------------

class BrowsingFrame(BaseFrame):
    """Browsing/Watching accessibility configuration"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        settings = app.settings.get('activities', {}).get('browsing', {})
        self.auto_captions = tk.BooleanVar(value=settings.get('auto_captions', False))
        self.reduce_motion = tk.BooleanVar(value=settings.get('reduce_motion', False))
        self.link_highlighting = tk.BooleanVar(value=settings.get('link_highlighting', False))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create browsing configuration widgets"""
        title = self.create_label("Browsing / Watching Accessibility", font_style='title')
        title.pack(pady=20)
        
        subtitle = self.create_label(
            "Select features for web browsing and media consumption",
            justify='center'
        )
        subtitle.pack(pady=10)
        
        options_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        options_frame.pack(pady=30, padx=50, fill='both', expand=True)
        
        options = [
            (self.auto_captions, "Auto-Captions",
             "Automatically enable captions\nfor video content when available"),
            (self.reduce_motion, "Reduce Motion",
             "Minimize animations and auto-playing videos\nfor easier viewing"),
            (self.link_highlighting, "Enhanced Link Visibility",
             "Increase contrast and size of links\nfor easier identification")
        ]
        
        for var, title_text, description in options:
            frame = tk.LabelFrame(
                options_frame,
                text=title_text,
                bg=self.app.current_theme['bg'],
                fg=self.app.current_theme['fg'],
                font=self.app.get_font(),
                padx=15,
                pady=10
            )
            frame.pack(fill='x', pady=10)
            
            check = self.create_checkbutton(description, var, justify='left')
            check.pack(in_=frame, anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self, bg=self.app.current_theme['bg'])
        button_frame.pack(pady=20)
        
        back_btn = self.create_button("Back", lambda: self.app.show_frame('home'))
        back_btn.pack(side='left', padx=10)
        
        finish_btn = self.create_button("Finish Setup", self.save_and_continue)
        finish_btn.pack(side='left', padx=10)
    
    def save_and_continue(self):
        """Save browsing settings"""
        try:
            self.app.settings.settings['activities']['browsing']['auto_captions'] = self.auto_captions.get()
            self.app.settings.settings['activities']['browsing']['reduce_motion'] = self.reduce_motion.get()
            self.app.settings.settings['activities']['browsing']['link_highlighting'] = self.link_highlighting.get()
            self.app.settings.save_settings()
            
            # Continue to next activity
            home_frame = self.app.frames['home']
            home_frame.show_next_activity()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save browsing settings: {e}")
            print(f"Browsing save error: {e}")

# -------------------------------
# Accessibility Tools Window
# -------------------------------

class AccessibilityWindow:
    """Standalone accessibility tools window"""
    
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Color Identifier")
        self.window.geometry("500x650")
        self.window.minsize(450, 600)
        
        self.is_running = True
        self.update_job = None  # Track the scheduled update job
        
        # Settings
        self.show_color = tk.BooleanVar(value=app.settings.get('color_identifier', True))
        self.high_contrast = tk.BooleanVar(value=app.settings.get('high_contrast', False))
        
        self.create_widgets()
        
        if PYAUTOGUI_AVAILABLE:
            self.update_color()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """Create accessibility tool widgets"""
        theme = self.app.current_theme
        
        # Title
        title = tk.Label(
            self.window,
            text="Color Identifier",
            font=self.app.get_font('title'),
            bg=theme['bg'],
            fg=theme['fg']
        )
        title.pack(pady=15)
        
        # Color identifier section
        color_frame = tk.LabelFrame(
            self.window,
            text="Hover to Identify Colors",
            font=self.app.get_font(),
            bg=theme['bg'],
            fg=theme['fg'],
            padx=15,
            pady=15
        )
        color_frame.pack(pady=10, padx=20, fill='x')
        
        self.color_label = tk.Label(
            color_frame,
            text="Move your mouse anywhere on the screen",
            font=self.app.get_font(),
            bg=theme['bg'],
            fg=theme['fg'],
            wraplength=400,
            justify='center'
        )
        self.color_label.pack(pady=5)
        
        self.color_box = tk.Label(
            color_frame,
            width=20,
            height=3,
            bg="#000000",
            relief='solid',
            bd=2
        )
        self.color_box.pack(pady=10)
        
        # Settings section
        settings_frame = tk.LabelFrame(
            self.window,
            text="Settings",
            font=self.app.get_font(),
            bg=theme['bg'],
            fg=theme['fg'],
            padx=15,
            pady=15
        )
        settings_frame.pack(pady=10, padx=20, fill='x')
        
        color_check = tk.Checkbutton(
            settings_frame,
            text="Enable color identification",
            variable=self.show_color,
            font=self.app.get_font(),
            bg=theme['bg'],
            fg=theme['fg'],
            selectcolor=theme['bg'],
            activebackground=theme['bg'],
            activeforeground=theme['fg'],
            command=self.save_color_setting
        )
        color_check.pack(anchor='w', pady=5)
        
        contrast_check = tk.Checkbutton(
            settings_frame,
            text="High contrast mode (affects entire app)",
            variable=self.high_contrast,
            font=self.app.get_font(),
            bg=theme['bg'],
            fg=theme['fg'],
            selectcolor=theme['bg'],
            activebackground=theme['bg'],
            activeforeground=theme['fg'],
            command=self.toggle_high_contrast
        )
        contrast_check.pack(anchor='w', pady=5)
        
        # Info section
        info_frame = tk.LabelFrame(
            self.window,
            text="Keyboard Shortcuts",
            font=self.app.get_font(),
            bg=theme['bg'],
            fg=theme['fg'],
            padx=15,
            pady=15
        )
        info_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        shortcuts = [
            "Ctrl+H (or Cmd+H on Mac): Go to Home",
            "Ctrl+, (or Cmd+,): Open Settings",
            "Ctrl+I (or Cmd+I): Open Color Identifier",
            "Ctrl+Q (or Cmd+Q): Quit Application"
        ]
        
        for shortcut in shortcuts:
            label = tk.Label(
                info_frame,
                text=shortcut,
                font=self.app.get_font(),
                bg=theme['bg'],
                fg=theme['fg'],
                anchor='w'
            )
            label.pack(anchor='w', pady=2)
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="Close",
            command=self.on_close,
            font=self.app.get_font(),
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            padx=20,
            pady=10
        )
        close_btn.pack(pady=15)
    
    def closest_color(self, rgb):
        """Find the closest named color using HSV-aware detection"""
        r, g, b = rgb
        
        # Convert to 0-1 range for HSV calculation
        r_norm, g_norm, b_norm = r/255.0, g/255.0, b/255.0
        
        # Calculate HSV values
        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val
        
        # Value (brightness)
        v = max_val
        
        # Saturation
        s = 0 if max_val == 0 else diff / max_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r_norm:
            h = (60 * ((g_norm - b_norm) / diff) + 360) % 360
        elif max_val == g_norm:
            h = (60 * ((b_norm - r_norm) / diff) + 120) % 360
        else:
            h = (60 * ((r_norm - g_norm) / diff) + 240) % 360
        
        # GRAYSCALE DETECTION (low saturation)
        if s < 0.10:
            if v < 0.10: return "Black"
            elif v < 0.30: return "Dark Gray"
            elif v < 0.55: return "Gray"  
            elif v < 0.80: return "Silver"
            elif v < 0.93: return "Light Gray"
            else: return "White"
        
        # LOW SATURATION COLORS (pastels, tans, beiges)
        elif s < 0.30:
            if v > 0.88:
                if 0 <= h < 30 or 330 <= h < 360: return "Light Pink"
                elif 30 <= h < 60: return "Cream"
                elif 60 <= h < 85: return "Light Yellow"
                elif 85 <= h < 150: return "Mint"
                elif 150 <= h < 210: return "Light Blue"
                elif 210 <= h < 280: return "Lavender"
                elif 280 <= h < 320: return "Lavender"
                else: return "Light Pink"
            elif v > 0.70:
                if 0 <= h < 40 or 320 <= h < 360: return "Beige"
                elif 40 <= h < 80: return "Tan"
                elif 80 <= h < 150: return "Sage"
                else: return "Light Gray"
            else:
                return "Gray"
        
        # CHROMATIC COLORS (good saturation)
        else:
            if v < 0.20:
                if 0 <= h < 30 or 330 <= h < 360: return "Dark Red"
                elif 30 <= h < 70: return "Dark Brown"
                elif 70 <= h < 160: return "Dark Green"
                elif 160 <= h < 250: return "Navy"
                elif 250 <= h < 290: return "Dark Purple"
                else: return "Dark Purple"
            
            elif v < 0.45:
                if 0 <= h < 20 or 340 <= h < 360: return "Dark Red"
                elif 20 <= h < 50: return "Brown"
                elif 50 <= h < 80: return "Olive"
                elif 80 <= h < 160: return "Forest Green"
                elif 160 <= h < 210: return "Teal"
                elif 210 <= h < 250: return "Navy"
                elif 250 <= h < 295: return "Purple"
                elif 295 <= h < 330: return "Dark Magenta"
                else: return "Maroon"
            
            elif v < 0.75:
                if 0 <= h < 12 or 348 <= h < 360: return "Red"
                elif 12 <= h < 35: return "Orange Red"
                elif 35 <= h < 50: return "Orange"
                elif 50 <= h < 75: return "Gold"
                elif 75 <= h < 160: return "Green"
                elif 160 <= h < 190: return "Cyan"
                elif 190 <= h < 215: return "Sky Blue"
                elif 215 <= h < 255: return "Blue"
                elif 255 <= h < 285: return "Purple"
                elif 285 <= h < 315: return "Magenta"
                elif 315 <= h < 335: return "Pink"
                else: return "Pink"
            
            else:
                if 0 <= h < 10 or 350 <= h < 360: return "Red"
                elif 10 <= h < 25: return "Red Orange"
                elif 25 <= h < 45: return "Orange"
                elif 45 <= h < 65: return "Yellow Orange"
                elif 65 <= h < 85: return "Yellow"
                elif 85 <= h < 110: return "Yellow Green"
                elif 110 <= h < 140: return "Green"
                elif 140 <= h < 165: return "Lime"
                elif 165 <= h < 195: return "Cyan"
                elif 195 <= h < 215: return "Sky Blue"
                elif 215 <= h < 245: return "Blue"
                elif 245 <= h < 270: return "Blue Violet"
                elif 270 <= h < 290: return "Violet"
                elif 290 <= h < 320: return "Magenta"
                elif 320 <= h < 340: return "Hot Pink"
                else: return "Pink"
    
    def update_color(self):
        """Update color identification"""
        if not self.is_running or not PYAUTOGUI_AVAILABLE:
            return
        
        try:
            if self.show_color.get():
                x, y = pyautogui.position()
                pixel = pyautogui.screenshot().getpixel((x, y))
                color_name = self.closest_color(pixel)
                hex_color = '#%02x%02x%02x' % pixel
                
                self.color_label.config(
                    text=f"Color: {color_name}\nRGB: {pixel}\nHex: {hex_color}\nPosition: ({x}, {y})"
                )
                self.color_box.config(bg=hex_color)
            else:
                self.color_label.config(text="Color identification disabled\n(Enable it in settings below)")
                self.color_box.config(bg=self.app.current_theme['bg'])
        except Exception as e:
            self.color_label.config(text=f"Error detecting color:\n{str(e)[:50]}")
        
        # Schedule next update
        if self.is_running:
            self.update_job = self.window.after(300, self.update_color)
    
    def save_color_setting(self):
        """Save color identifier setting"""
        try:
            self.app.settings.update('color_identifier', self.show_color.get())
        except Exception as e:
            print(f"Error saving color setting: {e}")
    
    def toggle_high_contrast(self):
        """Toggle high contrast mode"""
        try:
            self.app.settings.update('high_contrast', self.high_contrast.get())
            self.app.apply_theme()
            
            # Recreate this window with new theme
            self.on_close()
            self.app.open_accessibility_window()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle high contrast: {e}")
            print(f"High contrast toggle error: {e}")
    
    def on_close(self):
        """Handle window close"""
        self.is_running = False
        
        # Cancel any pending updates
        if self.update_job:
            try:
                self.window.after_cancel(self.update_job)
            except:
                pass
        
        try:
            self.window.destroy()
        except:
            pass

# -------------------------------
# Main Entry Point
# -------------------------------

def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = EyeSpyApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
