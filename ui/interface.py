# ┌────────────────────────────────────────────────────────────────────────────┐
# │ EyeSpeak Assist - Blink-Based Communication System                         │
# │ © 2025 Blake Kemp                                                          │
# ├────────────────────────────────────────────────────────────────────────────┤
# │ Licensed under the Creative Commons Attribution-NonCommercial 4.0         │
# │ International License (CC BY-NC 4.0).                                      │
# │                                                                            │
# │ You are free to:                                                           │
# │  • Share — copy and redistribute the material in any medium or format      │
# │  • Adapt — remix, transform, and build upon the material                   │
# │                                                                            │
# │ Under the following terms:                                                 │
# │  • Attribution — You must give appropriate credit and indicate changes     │
# │  • NonCommercial — You may not use the material for commercial purposes    │
# │                                                                            │
# │ License Info: https://creativecommons.org/licenses/by-nc/4.0/              │
# │ Commercial Use: Contact blakekemp01@gmail.com                               │
# └────────────────────────────────────────────────────────────────────────────┘

import cv2
import os
import yaml
import time

class EyeSpeakInterface:
    def __init__(self):
        self.layout = [
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM./-"),
        ]
        self.special_buttons = ["PHRASES", "QUIT"]
        self.cell_width = 60
        self.cell_height = 60
        self.text_buffer = ""
        self.blink_cooldown = 0
        self.selection_mode = False
        self.pending_char = None
        self.confirm_options = ["YES", "NO"]
        self.confirm_index = 0
        self.key_index = 0
        self.in_phrase_panel = False
        self.just_spoke_phrase = False
        self.phrase_index = 0
        self.phrase_scroll_offset = 0
        self.visible_phrase_rows = 5
        self.visible_phrase_cols = 3
        self.visible_phrases = self.visible_phrase_rows * self.visible_phrase_cols
        self.words = self.load_dictionary()
        self.valid_keys = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ./-")
        self.phrases = self.load_phrases()
        self.quit_confirm = False
        self.quit_index = 0
        self.linger_mode = False
        self.linger_started_at = 0
        self.linger_phase = "green"
        self.last_highlighted_index = None
        self.key_order = self.generate_key_order()

    def get_highlight_color(self, current_index, default_color=(0, 255, 0)):
        if self.linger_mode and self.last_highlighted_index == current_index:
            if self.linger_phase == "green":
                return default_color  # solid green
            elif self.linger_phase == "flash":
                flash_cycle = int((time.time() * 6) % 2)
                return (0, 255, 255) if flash_cycle == 0 else (255, 255, 255)
        return default_color

    def load_phrases(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, "phrases.yml")
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return [str(p) for p in data.get("phrases", [])]
        except Exception as e:
            print(f" [ERROR] Could not load phrases.yml: {e}")
            return []

    def load_dictionary(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dict_path = os.path.join(current_dir, "..", "assets", "dict", "american-english")

        if os.path.exists(dict_path):
            with open(dict_path, "r") as f:
                return set(word.strip().upper() for word in f if word.strip().isalpha())

        print("⚠️ Dictionary not found. Falling back to defaults.")
        return {"HELLO", "YES", "NO", "PLEASE", "THANK", "YOU", "HELP", "STOP", "GO", "LOVE"}

    def update_valid_keys(self):
        # Look at the raw text buffer, don't strip or rstrip
        if self.text_buffer.endswith(" "):
            # User just typed space — treat it as a word boundary
            self.valid_keys = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ./-")
            return

        # Otherwise calculate next valid letters based on last word
        partial = self.text_buffer.split(" ")[-1].upper()
        next_keys = set()
        for word in self.words:
            if word.startswith(partial) and len(word) > len(partial):
                next_keys.add(word[len(partial)])

        self.valid_keys = next_keys.union({".", "/", "-"}) if next_keys else set("ABCDEFGHIJKLMNOPQRSTUVWXYZ./-")

    def generate_key_order(self):
        order = []
        for row in self.layout:
            for key in row:
                order.append(("KEY", key))
            order.append(("SPECIAL", "PHRASES"))
        order.append(("SPECIAL", "QUIT"))
        return order

    def draw_ui(self, frame):       
        if self.quit_confirm:
            overlay = frame.copy()
            prompt =  "Are you sure you want to quit? YES / NO"
            cv2.putText(overlay, prompt, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            for idx, option in enumerate (["YES", "NO"]):
                x = 50 + idx * 160
                y = 150
                color = (0, 255, 0) if self.quit_index == idx else (255, 255, 255)
                cv2.rectangle(overlay, (x, y), (x + 120, y +60), color, 2)
                cv2.putText(overlay, option, (x + 20, y +40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            return overlay

        h, w, _ = frame.shape
        offset_x = (w - self.cell_width * 10) // 2
        offset_y = h - self.cell_height * 5 - 30

        self.update_valid_keys()

        if self.selection_mode:
            return self.draw_confirm_ui(frame, offset_x, offset_y)

        if self.in_phrase_panel:
            return self.draw_phrase_panel(frame, offset_x, offset_y)
        phrase_button_coords = (offset_x + 4 * self.cell_width, offset_y)
        phrase_color = self.get_highlight_color(("SPECIAL", "PHRASES")) if self.is_phrase_selected() else (255, 255, 255)
        cv2.rectangle(frame, phrase_button_coords, 
                      (phrase_button_coords[0] + 2 * self.cell_width, phrase_button_coords[1] + self.cell_height), 
                      phrase_color, 2)
        cv2.putText(frame, "PHRASES", (phrase_button_coords[0] + 2, phrase_button_coords[1] + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, phrase_color, 2)

        for row_idx, row in enumerate(self.layout):
            for col_idx, char in enumerate(row):
                x1 = offset_x + col_idx * self.cell_width
                y1 = offset_y + (row_idx + 1) * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                highlighted = self.key_order[self.key_index] == ("KEY", char)
                enabled = char.upper() in self.valid_keys
                if highlighted and enabled:
                    color = self.get_highlight_color(("KEY", char))
                elif not enabled:
                    color = (100, 100, 100)
                else:
                    color = (255, 255, 255)
                thickness = 2 if enabled else 1
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3 if highlighted and enabled else thickness)
                cv2.putText(frame, char, (x1 + 15, y1 + 45), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw QUIT button
        x = offset_x + 8 * self.cell_width
        y = offset_y - self.cell_height
        highlighted = self.key_order[self.key_index] == ("SPECIAL", "QUIT")
        color = self.get_highlight_color(("SPECIAL", "QUIT")) if highlighted else (255, 255, 255)
        cv2.rectangle(frame, (x, y), (x + 2 * self.cell_width, y + self.cell_height), color, 2)
        cv2.putText(frame, "QUIT", (x + 5, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.putText(frame, self.text_buffer, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
        return frame

    def draw_phrase_panel(self, frame, offset_x, offset_y):
        title = "Select a Phrase:"
        font_scale = 0.6
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2
        (text_width, _), _ = cv2.getTextSize(title, font, font_scale, thickness)
        center_x = frame.shape[1] // 2
        title_x = center_x - text_width // 2
        title_y = offset_y - 10
        w = frame.shape[1]
        columns = 3
        col_spacing = 230
        row_spacing = 50
        box_width = 180
        box_height = 48
        panel_width = (columns - 1) * col_spacing + box_width
        offset_x = (w - panel_width) // 2

        cv2.putText(frame, title, (title_x, title_y),
                    font, font_scale, (255, 255, 0), thickness)

        if not self.phrases:
            cv2.putText(frame, "⚠ No phrases found.", (offset_x, offset_y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return frame

        max_rows_per_col = 5
        total_visible = max_rows_per_col * columns

        start_index = self.phrase_scroll_offset
        end_index = min(start_index + total_visible, len(self.phrases))
        visible_items = self.phrases[start_index:end_index]

        has_prev_page = self.phrase_scroll_offset > 0
        has_next_page = end_index < len(self.phrases)

        highlight_index = self.phrase_index

        # BACK button
        back_x = offset_x
        back_y = offset_y - 70
        back_color = self.get_highlight_color(("PHRASE", -1)) if highlight_index == -1 else (255, 255, 255)
        cv2.rectangle(frame, (back_x, back_y), (back_x + box_width, back_y + box_height), back_color, 2)
        cv2.putText(frame, "BACK", (back_x + 10, back_y + 25), font, 0.6, back_color, 2)

        # Phrase buttons
        for i, phrase in enumerate(visible_items):
            col = i // max_rows_per_col
            row = i % max_rows_per_col
            x = offset_x + col * col_spacing
            y = offset_y + row * row_spacing
            color = self.get_highlight_color(("PHRASE", i)) if highlight_index == i else (255, 255, 255)
            cv2.rectangle(frame, (x, y), (x + box_width, y + box_height), color, 2)

            # Word wrapping
            words = phrase.split()
            line1, line2 = "", ""
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                (text_width, _), _ = cv2.getTextSize(test_line, font, font_scale, 1)
                if text_width < box_width - 10:
                    current_line = test_line
                elif not line1:
                    line1 = current_line
                    current_line = word
                else:
                    line2 = current_line
                    break

            if not line1:
                line1 = current_line
                line2 = ""
            elif not line2:
                line2 = current_line
            else:
                line2 = line2[:max(0, len(line2) - 3)] + "..."

            cv2.putText(frame, line1.strip(), (x + 5, y + 18), font, font_scale, color, 1)
            if line2.strip():
                cv2.putText(frame, line2.strip(), (x + 5, y + 35), font, font_scale, color, 1)

        # NEXT PAGE button
        if has_next_page:
            next_index = len(visible_items)
            next_x = offset_x + (columns - 1) * col_spacing
            next_y = offset_y + max_rows_per_col * row_spacing + 10
            next_color = self.get_highlight_color(("PHRASE", next_index)) if highlight_index == next_index else (255, 255, 255)
            cv2.rectangle(frame, (next_x, next_y), (next_x + 100, next_y + 40), next_color, 2)
            cv2.putText(frame, "NEXT", (next_x + 10, next_y + 28), font, 0.8, next_color, 2)

        return frame

    def draw_confirm_ui(self, frame, offset_x, offset_y):
        prompt = f"Select '{self.pending_char}'? YES / NO"
        cv2.putText(frame, prompt, (offset_x, offset_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        for idx, option in enumerate(self.confirm_options):
            x1 = offset_x + idx * (self.cell_width + 20)
            y1 = offset_y
            x2 = x1 + self.cell_width
            y2 = y1 + self.cell_height
            color = (0, 255, 0) if idx == self.confirm_index else (255, 255, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, option, (x1 + 5, y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return frame

    def advance_key(self):
        now = time.time()
        if self.linger_mode:
            # Stay in green phase for 1s before starting to flash
            if self.linger_phase == "green":
                if now - self.linger_started_at >= 1.0:
                    self.linger_phase = "flash"
                return
            elif self.linger_phase == "flash":
                # After 1.5s of flashing, advance
                if now - self.linger_started_at >= 2.5:
                    self.linger_mode = False
                    self.linger_phase = "green"
                    return

        if self.quit_confirm:
            self.quit_index = (self.quit_index + 1) % 2
            self.last_highlighted_index = ("SPECIAL", "QUIT")
            self.linger_mode = True  # NEXT frame will flash
            self.linger_started_at = now
            self.linger_phase = "green"
            return

        if self.selection_mode:
            return

        if self.in_phrase_panel:
            max_visible = self.visible_phrase_rows * self.visible_phrase_cols
            total_phrases = len(self.phrases)
            start_index = self.phrase_scroll_offset
            visible_count = min(max_visible, total_phrases - start_index)
            total_options = visible_count + 2

            self.phrase_index += 1
            if self.phrase_index >= total_options:
                self.phrase_index = -1  # wrap to BACK

            self.last_highlighted_index = ("PHRASE", self.phrase_index)
            self.linger_mode = True  # First frame = solid green
            self.linger_started_at = now
            self.linger_phase = "green"
        else:
            tries = 0
            while tries < len(self.key_order):
                self.key_index = (self.key_index + 1) % len(self.key_order)
                kind, value = self.key_order[self.key_index]
                if kind == "SPECIAL" or value in self.valid_keys:
                    break
                tries += 1

            self.last_highlighted_index = self.key_order[self.key_index]
            self.linger_mode = True  # First frame = solid green
            self.linger_started_at = now
            self.linger_phase = "green"

    def blink_triggered(self):
        self.linger_mode = False

        if self.quit_confirm:
            if self.quit_index == 0:
                exit(0)
            else:
                self.quit_confirm = False
                self.quit_index = 0
            return None

        if self.selection_mode:
            if self.confirm_options[self.confirm_index] == "YES":
                return self.commit_char()
            self.selection_mode = False
            self.pending_char = None
            self.confirm_index = 0
            return None

        if self.in_phrase_panel:
            visible_count = min(self.visible_phrases, len(self.phrases) - self.phrase_scroll_offset)

            if self.phrase_index == -1:
                if self.phrase_scroll_offset == 0:
                    # On first page → go back to keyboard
                    self.in_phrase_panel = False
                    self.phrase_index = 0
                    self.phrase_scroll_offset = 0
                else:
                    # On later pages → scroll back
                    self.phrase_scroll_offset -= self.visible_phrases
                    if self.phrase_scroll_offset < 0:
                        self.phrase_scroll_offset = 0
                    self.phrase_index = -1

            elif self.phrase_index == visible_count:
                # NEXT PAGE
                self.phrase_scroll_offset += self.visible_phrases
                if self.phrase_scroll_offset >= len(self.phrases):
                    self.phrase_scroll_offset = 0
                self.phrase_index = -1

            else:
                selected_index = self.phrase_scroll_offset + self.phrase_index
                if selected_index < len(self.phrases):
                    self.pending_char = self.phrases[selected_index]
                    self.selection_mode = True
            
            return None

        # Regular keyboard
        kind, value = self.key_order[self.key_index]
        if kind == "SPECIAL":
            if value == "PHRASES":
                self.in_phrase_panel = True
                self.phrase_index = -1
                self.phrase_scroll_offset = 0
            elif value == "QUIT":
                self.quit_confirm = True
                self.quit_index = 0
            return None

        if kind == "KEY" and value in self.valid_keys:
            self.pending_char = value
            self.selection_mode = True
        return None

    def toggle_confirmation(self):
        if self.selection_mode:
            self.confirm_index = (self.confirm_index + 1) % len(self.confirm_options)

    def commit_char(self):
        if self.in_phrase_panel:
            phrase = self.pending_char
            self.selection_mode = False
            self.pending_char = None
            self.confirm_index = 0
            self.in_phrase_panel = False
            self.phrase_index = 0
            self.phrase_scroll_offset = 0
            return phrase

        char = self.pending_char
        self.selection_mode = False
        self.pending_char = None
        self.confirm_index = 0

        if char == ".":
            self.text_buffer += " "
        elif char == "/":
            self.text_buffer = self.text_buffer[:-1]
        elif char == "-":
            return "ENTER"
        else:
            self.text_buffer += char
        return None

    def is_phrase_selected(self):
        return self.key_order[self.key_index] == ("SPECIAL", "PHRASES")

    def get_current_char(self):
        kind, value = self.key_order[self.key_index]
        return value if kind == "KEY" else None
