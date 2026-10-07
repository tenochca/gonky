"""GlobalConkySettings dataclass"""

from dataclasses import dataclass

@dataclass
class GlobalConkySettings:
   # placement
   alignment: str = "top_left"
   gap_x: int = 10
   gap_y: int = 10

   # window
   window_width: int = 300 # conky.config.minimum_width
   window_height: int = 0 # conky.config.minimum_height
   own_window: bool = True
   own_window_type: str = "desktop"
   own_window_transparent: bool = True
   own_window_argb_visual: bool = True
   background: bool = False
   border_width: int = 0

   # font 
   default_font: str = "DejaVu Sans Mono" # font and size grouped in conky.config.font
   default_font_size: int = 10
   default_color: str = "white"


   # misc 
   double_buffer: bool = True
   update_interval: float = 1.0
   cpu_avg_samples: int = 2
   net_avg_samples: int = 2
   extra_lua: str = "" # raw lua added to conky file