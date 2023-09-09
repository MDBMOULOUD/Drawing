from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.uix.colorpicker import ColorPicker

from kivy.uix.button import Button
from kivy.config import Config

# Set Kivy configuration for automatic orientation handling
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')  # Set your initial window width
Config.set('graphics', 'height', '640')  # Set your initial window height

KV = '''
BoxLayout:
    orientation: 'vertical'

    BoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: 10

        MDIconButton:
            icon: "palette"
            on_release: app.show_color_picker_dialog()

        MDIconButton:
            icon: "eraser-variant"
            on_release: app.toggle_eraser_mode()

        MDIconButton:
            icon: "delete-sweep"
            on_release: app.delete_all_lines()

        MDIconButton:
            icon: "refresh"  # Icon for the reset button
            on_release: app.reset_app()  # Call the reset_app() method

    DrawingArea:
        id: drawing_area
'''


class DrawingArea(Widget):
    lines = []  # List to keep track of all drawn lines
    current_line = None
    current_color = (0, 0, 0, 1)  # Default color (black)
    eraser_mode = False  # Flag to indicate whether eraser mode is active

    def on_touch_down(self, touch):
        if self.eraser_mode:
            self.erase_at_point(touch.x, touch.y)
        else:
            with self.canvas:
                Color(*self.current_color)
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)
                self.lines.append(touch.ud['line'])  # Add the line to the list
                self.current_line = touch.ud['line']

    def on_touch_move(self, touch):
        if self.eraser_mode:
            self.erase_at_point(touch.x, touch.y)
        elif self.current_line:
            touch.ud['line'].points += [touch.x, touch.y]

    def erase_at_point(self, x, y):
        # Iterate through all lines and remove points that are close to the touch point
        for line in self.lines:
            new_points = []
            points = line.points
            for i in range(0, len(points), 2):
                px, py = points[i], points[i + 1]
                if abs(px - x) > 10 or abs(py - y) > 10:
                    new_points.extend([px, py])
            line.points = new_points


class DrawingApp(MDApp):
    color_picker_dialog = None  # Declare as a class attribute

    def build(self):
        # Set the orientation mode to 'auto'
        from kivy.core.window import Window
        Window.orientation = 'auto'

        return Builder.load_string(KV)

    def erase_lines(self):
        drawing_area = self.root.ids.drawing_area
        if drawing_area.eraser_mode:
            drawing_area.eraser_mode = False
        else:
            drawing_area.eraser_mode = True

    def delete_all_lines(self):
        drawing_area = self.root.ids.drawing_area
        for line in drawing_area.lines:
            drawing_area.canvas.remove(line)
        drawing_area.lines = []  # Clear the list of lines

    def show_color_picker_dialog(self):
        if not self.color_picker_dialog:
            color_picker = ColorPicker(
                color=DrawingArea.current_color,
                size_hint=(None, None),
                size=("100dp", "100dp"),
            )
            color_picker.scale = 5  # Adjust the scale to resize the ColorPicker wheel
            self.color_picker_dialog = MDDialog(
                title="Choose Color",
                type="custom",
                content_cls=color_picker,
                buttons=[
                    MDRaisedButton(
                        text="Select",
                        on_release=self.set_color_from_picker,
                    ),
                    MDRaisedButton(
                        text="Cancel",
                        on_release=self.dismiss_color_picker_dialog,
                    ),
                ],
                size_hint=(0.5, None),
                size=("300dp", "300dp"),  # Adjust the dialog size here
            )
        self.color_picker_dialog.open()

    def set_color_from_picker(self, instance):
        drawing_area = self.root.ids.drawing_area
        color_picker = self.color_picker_dialog.content_cls
        selected_color = color_picker.color
        drawing_area.current_color = selected_color
        self.dismiss_color_picker_dialog()

    def dismiss_color_picker_dialog(self):
        if self.color_picker_dialog:
            self.color_picker_dialog.dismiss()

    def toggle_eraser_mode(self):
        drawing_area = self.root.ids.drawing_area
        if drawing_area.eraser_mode:
            drawing_area.eraser_mode = False
        else:
            drawing_area.eraser_mode = True

    def reset_app(self):
        drawing_area = self.root.ids.drawing_area
        drawing_area.canvas.clear()  # Clear the drawing canvas
        drawing_area.lines = []  # Clear the list of lines
        drawing_area.current_color = (0, 0, 0, 1)  # Reset color to black
        drawing_area.eraser_mode = False  # Turn off eraser mode
        self.dismiss_color_picker_dialog()  # Dismiss color picker dialog if open


if __name__ == '__main__':
    DrawingApp().run()