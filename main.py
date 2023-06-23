import arcade
from arcade import gui

WIN_WIDTH = 800
WIN_HEIGHT = 600
WIN_TITLE = 'Bitmap editor'
NAMES = {
    'Brush Tool': 'Кисть',
}


class Layer:
    def __init__(self, figures, order):
        self.figures = figures
        self.order = order

    def change_order(self, new_order):
        self.order = new_order

    def get_order(self):
        return self.order

    def get_figures(self):
        return self.figures

    def update_figures(self, new_figures):
        self.figures = new_figures


class LayerController:
    def __init__(self):
        self.layer_queue = []

    def add_layer(self, figures_list=None, new_layer_order=None):
        empty_figures_list = arcade.ShapeElementList() or figures_list
        new_layer_order = new_layer_order or 1
        new_layer = Layer(empty_figures_list, new_layer_order)
        self.layer_queue.insert(new_layer_order - 1, new_layer)

    def get_layer(self, order):
        return self.layer_queue[order - 1]

    def change_order(self, layer, new_order):
        self.layer_queue.remove(layer)
        self.layer_queue.insert(new_order - 1, layer)

    def remove_layer(self, layer):
        self.layer_queue.remove(layer)

    def copy_layer(self, layer):
        copy_figures_list = layer.get_figures()
        copy_order = layer.get_order() + 1
        self.add_layer(copy_figures_list, copy_order)


class AbstractTool:
    def __init__(self, name):
        self.name = name

    def action(self):
        pass


class BrushTool(AbstractTool):
    def __init__(self):
        super().__init__(NAMES['Brush Tool'])

    def action(self):
        pass


class DrawSpace:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.scale = scale
        self.active_layer = None
        self.active_tool = None
        self.layer_controller = None
        self.diameter = None
        self.positions_list = None

    def add_figure(self, figure):
        self.active_layer.update_figures(figure)

    def clear_layer(self):
        figure = arcade.ShapeElementList()
        self.active_layer.update_figures(figure)


class MainWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.is_mouse_press = None
        self.draw_space = None

        self.to_draw = arcade.ShapeElementList()
        self.is_drawing = False
        self.positions = []
        self.selection_figure_pos = (0, 0)
        self.diameter = 5
        self.current_color = (0, 0, 0)
        self.current_color_number = 0
        self.gui = arcade.gui.UIManager()
        self.clear_button = arcade.gui.UIFlatButton(700,
                                                    550,
                                                    100,
                                                    50,
                                                    'Стереть',
                                                    )
        self.menu_color = (0, 0, 0, 50)
        self.colors_bar_color = (0, 0, 0, 35)
        self.colors = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'white': (255, 255, 255),
            'black': (0, 0, 0)
        }
        self.colors_bar = arcade.ShapeElementList()
        self.thickness_bar_pos = (550, 575)
        self.move_thickness = False
        self.circle_button = arcade.gui.UIFlatButton(650,
                                                    550,
                                                    50,
                                                    50,
                                                    'Круг',)
        self.make_circle = False
        self.circle_start_point = None
        self.circle_end_point = None

    def setup(self):
        arcade.set_background_color(arcade.color.WHITE_SMOKE)
        self.clear_button.on_click = self.clear_layer
        self.circle_button.on_click = self.add_circle
        self.gui.add(self.clear_button)
        self.gui.add(self.circle_button)
        self.gui.enable()
        current_pos_colors = 1
        for color, rgb in self.colors.items():
            new_color = arcade.create_rectangle_filled(50 * current_pos_colors - 25,
                                                       WIN_HEIGHT - 25,
                                                       40,
                                                       40,
                                                       rgb)
            new_color.on_click = lambda x: print('sdfsdf')
            self.colors_bar.append(new_color)
            current_pos_colors += 1

    def add_circle(self, data):
        if data:
            self.make_circle = True

    def clear_layer(self, data):
        if data:
            self.to_draw = arcade.ShapeElementList()

    def on_draw(self):
        self.clear()
        arcade.draw_rectangle_filled(WIN_WIDTH // 2,
                                     WIN_HEIGHT - 25,
                                     WIN_WIDTH,
                                     50,
                                     self.menu_color
                                     )
        arcade.draw_rectangle_filled(WIN_WIDTH // 6,
                                     WIN_HEIGHT - 25,
                                     WIN_WIDTH // 3,
                                     50,
                                     self.colors_bar_color
                                     )
        self.colors_bar.draw()
        if self.current_color_number > 0:
            border_color = (50, 50, 50, 70)
            arcade.draw_rectangle_outline(50 * self.current_color_number - 25,
                                          WIN_HEIGHT - 25,
                                          45,
                                          45,
                                          border_color,
                                          5.0,
                                          )
        arcade.draw_ellipse_filled(*self.selection_figure_pos,
                                   self.diameter,
                                   self.diameter,
                                   self.current_color)
        arcade.draw_ellipse_filled(*self.thickness_bar_pos, 20, 20, self.colors['black'])
        if self.make_circle and self.circle_start_point:
            arcade.draw_ellipse_filled(*self.circle_start_point,
                                       *self.circle_end_point,
                                       self.current_color)
        self.to_draw.draw()
        self.gui.draw()

    def on_update(self, delta_time):
        self.on_draw()

    def reset_draw(self):
        self.positions = []

    def draw_line(self):
        if len(self.positions) > 2:
            self.to_draw.append(arcade.create_line_strip(self.positions[-3:], self.current_color, self.diameter))

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        if y >= WIN_HEIGHT - 50:
            self.is_drawing = False
            self.reset_draw()
        if self.is_drawing:
            self.positions.append((x, y))
            print(self.positions)
            self.draw_line()
        if self.make_circle:
            self.circle_end_point = (x, y)
        if self.move_thickness:
            if 550 <= x <= 600:
                self.diameter = (x - 545) // 5 + 0.1
                self.thickness_bar_pos = (x, 575)
        self.selection_figure_pos = (x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if y < WIN_HEIGHT - 50:
            if self.make_circle:
                self.circle_start_point = (x, y)
                self.circle_end_point = (x, y)
            else:
                self.is_drawing = True
                self.reset_draw()
        else:
            if 600 >= x >= 550 <= y <= 600:
                self.move_thickness = True
            else:
                to_activate = x // 50
                if to_activate < len(self.colors.items()):
                    self.new_color(to_activate)

    def new_color(self, color_number):
        self.current_color = list(self.colors.values())[color_number]
        self.current_color_number = color_number + 1

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.is_drawing = False
        self.move_thickness = False
        self.stop_circle()

    def stop_circle(self):
        if self.make_circle:
            self.to_draw.append(arcade.create_ellipse_filled(*self.circle_start_point,
                                                             *self.circle_end_point,
                                                             self.current_color))
        self.make_circle = False
        self.circle_start_point = None
        self.circle_end_point = None


if __name__ == "__main__":
    game = MainWindow(WIN_WIDTH, WIN_HEIGHT, WIN_TITLE)
    game.setup()
    arcade.run()



