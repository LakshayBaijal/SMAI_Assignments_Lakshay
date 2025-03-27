#!/usr/bin/env python3

import curses
import re
import sys
import os
from typing import List

from ngram import NgramCharacterModel


class TerminalUI:
    def __init__(self, prediction_model, text_content=None):
        """
        :param prediction_model: An instance of NgramCharacterModel.
        :param text_content: Optional string to display in the Text Content panel.
        """
        self.screen = None
        self.suggestions = []
        self.current_suggestion_idx = 0
        self.scores = []
        self.text_content = text_content if text_content else ""
        self.user_input = ""
        self.cursor_pos = 0
        self.cursor_row = 1

        self.suggestions_panel = None
        self.text_panel = None
        self.input_panel = None
        self.scores_panel = None

        self.prediction_model = prediction_model

        # Metric counters
        self.total_letter_keys_typed = 0
        self.total_tab_key_presses = 0

    def calculate_scores(self, text: str) -> List[float]:
        """
        Calculate and return:
          1) Total number of letter keys typed
          2) Total number of Tab key presses
          3) Average letters per word
          4) Average Tab presses per word
        """
        words = text.strip().split()
        num_words = len(words)
        if num_words > 0:
            avg_letters = self.total_letter_keys_typed / num_words
            avg_tabs = self.total_tab_key_presses / num_words
        else:
            avg_letters = 0.0
            avg_tabs = 0.0

        return [
            self.total_letter_keys_typed,
            self.total_tab_key_presses,
            avg_letters,
            avg_tabs
        ]

    def find_last_word_start(self, text: str, cursor_pos: int) -> int:
        """Find the start position of the last word being typed."""
        if cursor_pos == 0:
            return 0
        text_before_cursor = text[:cursor_pos]
        match = re.search(r"[^\s]*$", text_before_cursor)
        if match:
            return cursor_pos - len(match.group(0))
        return cursor_pos

    def get_current_word(self) -> str:
        """Return the current word being typed."""
        word_start = self.find_last_word_start(self.user_input, self.cursor_pos)
        return self.user_input[word_start:self.cursor_pos]

    def replace_current_word(self, new_word: str) -> None:
        """Replace the current word with a suggestion."""
        word_start = self.find_last_word_start(self.user_input, self.cursor_pos)
        self.user_input = (
            self.user_input[:word_start]
            + new_word
            + self.user_input[self.cursor_pos:]
        )
        self.cursor_pos = word_start + len(new_word)

    def draw_suggestions_panel(self) -> None:
        """Draw the suggestions panel (top panel)."""
        h, w = self.suggestions_panel.getmaxyx()
        self.suggestions_panel.erase()
        self.suggestions_panel.box()
        self.suggestions_panel.addstr(0, 2, " Suggestions ")
        if not self.suggestions:
            self.suggestions_panel.addstr(1, 2, "No suggestions")
        else:
            display_text = ""
            for i, suggestion in enumerate(self.suggestions):
                if i == self.current_suggestion_idx:
                    display_text += f"[{suggestion}] "
                else:
                    display_text += f"{suggestion} "
            if len(display_text) > w - 4:
                display_text = display_text[:w - 7] + "..."
            self.suggestions_panel.addstr(1, 2, display_text)
        self.suggestions_panel.noutrefresh()

    def draw_text_panel(self) -> None:
        """Draw the text content panel (middle panel)."""
        h, w = self.text_panel.getmaxyx()
        self.text_panel.erase()
        self.text_panel.box()
        self.text_panel.addstr(0, 2, " Text Content ")
        words = self.text_content.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) > w - 4:
                lines.append(current_line)
                current_line = word
            else:
                current_line = current_line + " " + word if current_line else word
        if current_line:
            lines.append(current_line)
        for i, line in enumerate(lines):
            if i < h - 2:
                self.text_panel.addstr(i + 1, 2, line)
        self.text_panel.noutrefresh()

    def draw_input_panel(self) -> None:
        """Draw the input panel (bottom panel)."""
        h, w = self.input_panel.getmaxyx()
        self.input_panel.erase()
        self.input_panel.box()
        self.input_panel.addstr(0, 2, " Input ")
        prompt = "> "
        prompt_len = len(prompt)
        available_width = w - 4
        first_line_width = available_width - prompt_len
        lines = []
        current_pos = 0
        text = self.user_input
        first_line_text = text[:first_line_width] if text else ""
        lines.append(first_line_text)
        current_pos = len(first_line_text)
        while current_pos < len(text) and len(lines) < h - 2:
            next_chunk = text[current_pos: current_pos + available_width]
            lines.append(next_chunk)
            current_pos += len(next_chunk)
        for i, line in enumerate(lines):
            if i >= h - 2:
                break
            if i == 0:
                self.input_panel.addstr(i + 1, 2, prompt + line)
            else:
                self.input_panel.addstr(i + 1, 2, line)
        cursor_pos = self.cursor_pos
        if cursor_pos <= first_line_width:
            cursor_y = 1
            cursor_x = 2 + prompt_len + cursor_pos
        else:
            cursor_pos -= first_line_width
            cursor_y = 1 + (cursor_pos // available_width) + 1
            cursor_x = 2 + (cursor_pos % available_width)
        cursor_y = max(1, min(cursor_y, h - 2))
        cursor_x = max(1, min(cursor_x, w - 2))
        self.cursor_row = cursor_y
        self.cursor_col = cursor_x
        try:
            self.input_panel.move(cursor_y, cursor_x)
        except curses.error:
            pass
        self.input_panel.noutrefresh()

    def draw_scores_panel(self) -> None:
        """Draw the scores panel (very bottom panel)."""
        h, w = self.scores_panel.getmaxyx()
        self.scores_panel.erase()
        self.scores_panel.box()
        self.scores_panel.addstr(0, 2, " Scores ")
        score_labels = [
            "Total Letters Typed:",
            "Total Tab Presses:",
            "Avg Letters/Word:",
            "Avg Tabs/Word:"
        ]
        display_texts = []
        for label, val in zip(score_labels, self.scores):
            if isinstance(val, float):
                display_texts.append(f"{label} {val:.2f}")
            else:
                display_texts.append(f"{label} {val}")
        display_str = " | ".join(display_texts)
        if len(display_str) > w - 4:
            display_str = display_str[:w - 7] + "..."
        self.scores_panel.addstr(1, max(2, (w - len(display_str)) // 2), display_str)
        self.scores_panel.noutrefresh()

    def handle_input(self, key) -> bool:
        """Handle key input and update metrics."""
        if key == curses.KEY_RESIZE:
            return True
        if key == 27:  # ESC
            return False
        if key == 9:  # TAB
            if self.suggestions:
                self.current_suggestion_idx = (self.current_suggestion_idx + 1) % len(self.suggestions)
            self.total_tab_key_presses += 1
            return True
        if key == 10:  # ENTER
            if self.suggestions and self.current_suggestion_idx < len(self.suggestions):
                self.replace_current_word(self.suggestions[self.current_suggestion_idx])
                self.suggestions = []
                self.current_suggestion_idx = 0
            return True
        if key in (curses.KEY_BACKSPACE, 127, 8):
            if self.cursor_pos > 0:
                self.user_input = (
                    self.user_input[:self.cursor_pos - 1]
                    + self.user_input[self.cursor_pos:]
                )
                self.cursor_pos -= 1
                current_word = self.get_current_word()
                self.suggestions = self.prediction_model.predict_top_words(current_word)
                self.current_suggestion_idx = 0
                self.scores = self.calculate_scores(self.user_input)
            return True
        if key == curses.KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                current_word = self.get_current_word()
                self.suggestions = self.prediction_model.predict_top_words(current_word)
                self.current_suggestion_idx = 0
            return True
        if key == curses.KEY_RIGHT:
            if self.cursor_pos < len(self.user_input):
                self.cursor_pos += 1
                current_word = self.get_current_word()
                self.suggestions = self.prediction_model.predict_top_words(current_word)
                self.current_suggestion_idx = 0
            return True
        if 32 <= key <= 126:
            char = chr(key)
            self.total_letter_keys_typed += 1
            self.user_input = (
                self.user_input[:self.cursor_pos]
                + char
                + self.user_input[self.cursor_pos:]
            )
            self.cursor_pos += 1
            current_word = self.get_current_word()
            self.suggestions = self.prediction_model.predict_top_words(current_word)
            self.current_suggestion_idx = 0
            self.scores = self.calculate_scores(self.user_input)
        return True

    def run(self) -> None:
        """Main loop to run the terminal UI."""
        try:
            self.screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.start_color()
            self.screen.keypad(True)
            curses.curs_set(1)
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
            max_y, max_x = self.screen.getmaxyx()
            suggestions_height = 3
            text_height = (max_y - 6) // 2
            input_height = (max_y - 6) // 2
            scores_height = 3
            self.suggestions_panel = curses.newwin(suggestions_height, max_x, 0, 0)
            self.text_panel = curses.newwin(text_height, max_x, suggestions_height, 0)
            self.input_panel = curses.newwin(input_height, max_x, suggestions_height + text_height, 0)
            self.scores_panel = curses.newwin(scores_height, max_x, suggestions_height + text_height + input_height, 0)
            self.draw_suggestions_panel()
            self.draw_text_panel()
            self.draw_input_panel()
            self.draw_scores_panel()

            # Try to move the cursor to a safe starting position.
            try:
                self.input_panel.move(1, 4)
            except curses.error:
                try:
                    self.input_panel.move(1, 2)
                except curses.error:
                    pass

            curses.doupdate()

            running = True
            while running:
                try:
                    self.input_panel.move(self.cursor_row, self.cursor_col)
                except curses.error:
                    try:
                        self.input_panel.move(1, 2)
                    except curses.error:
                        pass
                self.input_panel.noutrefresh()
                curses.doupdate()
                key = self.screen.getch()
                running = self.handle_input(key)
                if key == curses.KEY_RESIZE:
                    max_y, max_x = self.screen.getmaxyx()
                    suggestions_height = 3
                    text_height = (max_y - 6) // 2 + 2
                    input_height = (max_y - 6) // 2 + 1
                    scores_height = 3
                    self.suggestions_panel = curses.newwin(suggestions_height, max_x, 0, 0)
                    self.text_panel = curses.newwin(text_height, max_x, suggestions_height, 0)
                    self.input_panel = curses.newwin(input_height, max_x, suggestions_height + text_height, 0)
                    self.scores_panel = curses.newwin(scores_height, max_x, suggestions_height + text_height + input_height, 0)
                self.draw_suggestions_panel()
                self.draw_text_panel()
                self.draw_input_panel()
                self.draw_scores_panel()
                try:
                    self.input_panel.move(self.cursor_row, self.cursor_col)
                    self.input_panel.noutrefresh()
                except curses.error:
                    pass
                curses.doupdate()
        finally:
            if self.screen:
                curses.nocbreak()
                self.screen.keypad(False)
                curses.echo()
                curses.endwin()


if __name__ == "__main__":
    """
    Usage: python user_interface.py <path_to_corpus> [<path_to_text_content>]
    <path_to_corpus> can be a file or folder of .txt files.
    <path_to_text_content> is optional text to display in the Text Content panel.
    """
    if len(sys.argv) < 2:
        print("Usage: python user_interface.py <path_to_corpus> [<path_to_text_content>]")
        sys.exit(1)

    corpus_arg = sys.argv[1]
    # Read corpus for model training
    if os.path.isfile(corpus_arg):
        with open(corpus_arg, "r", encoding="utf-8") as file:
            corpus = file.read()
    else:
        corpus_file_path_list = sorted(os.listdir(corpus_arg))
        corpus_file_path_list = [os.path.join(corpus_arg, fname) for fname in corpus_file_path_list if fname.endswith(".txt")]
        corpus = ""
        for path in corpus_file_path_list:
            with open(path, "r", encoding="utf-8") as file:
                corpus += file.read()

    # Optionally read text content for the Text Content panel
    text_data = ""
    if len(sys.argv) >= 3:
        text_content_arg = sys.argv[2]
        if os.path.isfile(text_content_arg):
            with open(text_content_arg, "r", encoding="utf-8") as f:
                text_data = f.read()
        else:
            print(f"WARNING: '{text_content_arg}' is not a file. The text content will be empty.")
            text_data = ""

    n = 2  # Adjust n as desired
    model = NgramCharacterModel(corpus, n)
    ui = TerminalUI(model, text_content=text_data)
    ui.run()
