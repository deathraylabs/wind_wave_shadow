#! /Users/peej/anaconda/envs/automate_boring/bin/python

import sys      # required for command line arguments
from tkinter import *
# from tkinter import ttk
import PIL.Image
import PIL.ImageTk
import PIL.ImageDraw
import PIL.ImageColor
import math
from datetime import datetime

# todo: get some legit docstrings in this bitch

# get arguments from command line
try:
    wind_direction_input = sys.argv[1]
    swell_direction_input = sys.argv[2]
except IndexError:
    # fail gracefully if not run from command line
    print("No command line arguments given.")
    wind_direction_input = None
    swell_direction_input = None


def draw_polygon(overlay, coords, color='black', trans=80):
    # convert color name to RGBA tuple
    poly_color = (PIL.ImageColor.getrgb(color) + (trans,))

    draw = PIL.ImageDraw.Draw(overlay)
    draw.polygon(coords, fill=poly_color)

    return overlay


# function to prompt for next label coordinate
def label_grabber(labels):

    if len(labels) == 0:
        print("All calibration points have been recorded.")
        return "done"
    elif len(labels) == 1:
        label = labels.pop(0)
        print("The last calibration point was recorded.")
        return label
    else:
        label = labels.pop(0)
        print("click on the point corresponding to " + labels[0])
        return label


def combine_image_overlay(base_image, overlay):
    # combine original image and overlay
    composite = PIL.Image.alpha_composite(base_image, overlay)
    # composite.show()
    # create tk compatible image
    tkcomposite = PIL.ImageTk.PhotoImage(composite)
    # tkcomposite = PhotoImage(tkcomposite)

    return tkcomposite


# todo: logic needs to handle parallel projections (infinite triangle)
def projection_calculations(point_jetty_shore,
                            point_jetty_end,
                            point_shore,
                            shadow_dir):
    """ function that calculates the projected line from the end of the
    jetty to the shore. Arguments are coordinates for the point where the
    jetty meets the shore, where the jetty ends, and a point somewhere
    along the shoreline.

    Returns coordinates of the shadow line.
    """
    n_or_s_jetty = ''

    # is the data for the north or south jetty?
    if point_shore[0] - point_jetty_shore[0] > 0:
        n_or_s_jetty = 'N'
    elif point_shore[0] - point_jetty_shore[0] < 0:
        n_or_s_jetty = 'S'
    else:
        raise ValueError

    # jetty x and y components
    jettylengthx = point_jetty_end[0] - point_jetty_shore[0]
    jettylengthy = point_jetty_end[1] - point_jetty_shore[1]

    # called r12 in notes
    jettylength = math.sqrt(jettylengthx ** 2 + jettylengthy ** 2)

    # shadow direction in radians is 180deg opposite of wave heading
    shadow_rad = math.radians(shadow_dir - 180.0)

    # theta 12 from notes (jetty angle CW from east)
    jetty_angle_east = math.asin(jettylengthy / jettylength)
    jetty_angle_degrees = 90.0 + math.degrees(jetty_angle_east)

    # will the jetty cast a shadow?
    if shadow_dir - jetty_angle_degrees <= 0 and n_or_s_jetty == 'N':
        return 'no shadow'
    elif shadow_dir - jetty_angle_degrees >= 0 and n_or_s_jetty == 'S':
        return 'no shadow'

    # shore x and y components
    shoremeasx = point_shore[0] - point_jetty_shore[0]
    shoremeasy = point_shore[1] - point_jetty_shore[1]

    # shore angle CCW from east
    shore_angle_east = math.atan(math.fabs(shoremeasy / shoremeasx))

    # shore plus jetty angle (angle gamma from notes)
    shore_jetty_angle = shore_angle_east + jetty_angle_east
    gamma_degrees = math.degrees(shore_jetty_angle)

    # angle between shadow and jetty (angle alpha in notes)
    # should always be positive or wrong jetty selected
    jetty_shadow_angle = (math.pi / 2 - jetty_angle_east) + shadow_rad
    alpha_degrees = math.degrees(jetty_shadow_angle)

    # angle between shore and shadow (angle beta in notes)
    shore_shadow_angle = math.pi - (jetty_shadow_angle + shore_jetty_angle)
    beta_degrees = math.degrees(shore_shadow_angle)

    # shadow length (length c in notes)
    shadow_length = jettylength * (
                math.sin(shore_jetty_angle) / math.sin(shore_shadow_angle))

    # shadow x and y components
    shadow_lengthx = shadow_length * math.sin(shadow_rad)
    shadow_lengthy = shadow_length * math.cos(shadow_rad)

    # shadow-shore point
    shadowx = int(point_jetty_end[0] + shadow_lengthx)
    shadowy = int(point_jetty_end[1] - shadow_lengthy)
    point_shadow_shore = (shadowx, shadowy)

    print('This is the {}-Jetty'.format(n_or_s_jetty))
    print('The shadow angle is {}°'.format(str(shadow_dir)[:4]))
    print('The jetty angle is  {}°'.format(str(jetty_angle_degrees)[:4]))
    print('alpha is            {}°'.format(str(alpha_degrees)[:4]))
    print('beta is             {}°'.format(str(beta_degrees)[:4]))
    print('gamma is            {}°'.format(str(gamma_degrees)[:4]))

    # return coordinates needed to plot polygon
    return point_jetty_shore, point_jetty_end, point_shadow_shore


class MainWindow:
    """ Object used to track and update state of the canvas
    """
    def __init__(self, main, map_path, mask_path):

        # main frame
        self.main = main
        # dictionary with calibration points
        self.coords = {'n_jetty_start': (530, 549),
                       'n_jetty_end': (869, 919),
                       'n_shoreline_end': (905, 115),
                       's_jetty_start': (515, 734),
                       's_jetty_end': (781, 1027),
                       's_shoreline_end': (208, 901)}
        # list of coordinates you need for calibration
        self.coord_labels = ['n_jetty_start',
                             'n_jetty_end',
                             's_jetty_start',
                             's_jetty_end',
                             'n_shoreline_end',
                             's_shoreline_end']
        self.wind_direction = 999.9   # impossible direction initialization
        self.wave_direction = 999.9

        # setting up a tkinter frame with scrollbars
        # bd=  this is the border width
        self.frame = Frame(main, bd=2, relief=SUNKEN)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        xscroll = Scrollbar(self.frame, orient=HORIZONTAL)
        xscroll.grid(row=1, column=0, sticky=E + W)
        yscroll = Scrollbar(self.frame)
        yscroll.grid(row=0, column=1, sticky=N + S)

        # initialize canvas for image
        self.canvas = Canvas(self.frame,
                             bd=0,
                             width=1200,
                             height=1050,
                             xscrollcommand=xscroll.set,
                             yscrollcommand=yscroll.set
                             )
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        xscroll.config(command=self.canvas.xview)
        yscroll.config(command=self.canvas.yview)
        # # frame will not be visible unless it is packed
        # self.frame.pack(fill=BOTH, expand=1)

        # create a pillow image file object
        self.base_image = PIL.Image.open(map_path)
        self.shadow_mask = PIL.Image.open(mask_path)
        # create a transparent overlay pillow image object
        self.overlay = PIL.Image.new(mode='RGBA', size=self.base_image.size,
                                     color=(0, 0, 0, 0))
        # last generated composit image
        self.last_image = PIL.Image.new(mode='RGBA', size=self.base_image.size,
                                        color=(0, 0, 0, 0))
        # create a tk image object
        self.tk_base_image = PIL.ImageTk.PhotoImage(self.base_image)

        # make the base satellite image visible
        self.image_on_canvas = \
            self.canvas.create_image(0, 0,
                                     image=self.tk_base_image,
                                     anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

        # keyboard and mouse button bindings
        self.canvas.bind("<Button 1>", self.savecoords)
        self.canvas.bind("<Button 2>", self.reset_everything)
        self.canvas.bind("<Return>", self.return_key)
        self.canvas.bind("<p>", self.p_key)
        self.canvas.bind("<q>", self.q_key)

        # frame will not be visible unless it is packed
        self.frame.pack(fill=BOTH, expand=1)

    # right mouse click resets the overlay screen
    def reset_everything(self, event):
        # create a transparent overlay pillow image object
        self.overlay = PIL.Image.new(mode='RGBA', size=self.base_image.size,
                                     color=(0, 0, 0, 0))
        updated_image = combine_image_overlay(self.base_image,
                                              self.overlay)
        # reset recorded mouse coordinate points
        self.coords = {}
        # reset coordinate point names
        self.coord_labels = ['n_jetty_start',
                             'n_jetty_end',
                             # 's_jetty_start',
                             # 's_jetty_end',
                             # 'n_shoreline_start',
                             'n_shoreline_end',
                             # 's_shoreline_start',
                             # 's_shoreline_end'
                             ]
        self.update_canvas(updated_image)

        return event

    # generate an overlay image to place an object on
    def create_overlay(self):
        # black transparent overlay based on the sat image
        return PIL.Image.new(mode='RGBA', size=self.base_image.size,
                             color=(0, 0, 0, 0))

    def draw_point(self, click_point, color='black', trans=255):
        """ click_point is the coordinate recorded during mouse click event
        """
        # convert color name to RGBA tuple
        poly_color = (PIL.ImageColor.getrgb(color) + (trans,))

        # draw click circles
        diameter = 10 / 2  # pixels
        try:
            point_circle = [(click_point.x - diameter,
                             click_point.y - diameter),
                            (click_point.x + diameter,
                             click_point.y + diameter)]
        except AttributeError:
            point_circle = [(click_point[0] - diameter,
                             click_point[0] - diameter),
                            (click_point[0] + diameter,
                             click_point[0] + diameter)]

        # draw shape on the transparent overlay
        draw = PIL.ImageDraw.Draw(self.overlay)
        draw.ellipse(point_circle, fill=poly_color)

        return None

    def update_canvas(self, updated_canvas_image):
        """update the canvas after the image has changed
        """
        self.canvas.itemconfig(self.image_on_canvas,
                               image=updated_canvas_image)
        self.main.mainloop()

    # function called on mouse click
    def savecoords(self, event):
        # get the coordinates
        # click_point = (event.x, event.y)
        click_point = event
        # print(click_point)

        # sets the focus to the canvas so the keyboard will capture
        self.canvas.focus_set()

        self.draw_point(click_point)
        label = label_grabber(self.coord_labels)

        if len(self.coord_labels) > 0:
            # update dict
            self.coords[label] = (click_point.x, click_point.y)
        elif len(self.coord_labels) == 0 and label != "done":
            self.coords[label] = (click_point.x, click_point.y)
            # this is where I draw the polygon
            coord_list = [self.coords["n_jetty_start"],
                          self.coords["n_jetty_end"],
                          self.coords["n_shoreline_end"]]
            draw_polygon(self.overlay, coord_list)

        print(self.coords)

        # combine images to format tk can use
        tkcomposite = combine_image_overlay(self.base_image,
                                            self.overlay)

        # update the canvas with composit image by calling method below
        self.update_canvas(tkcomposite)

        return None

    # function called on key click
    def return_key(self, event):

        self.display_projection_on_map()

        # don't have much use for this but whatever
        return event.keysym

    # save current image
    def p_key(self, event):
        """ Method for saving a .png version of the currently displayed
        pillow file image.

        :param event:
        :return:
        """
        # self.last_image.show()
        # time string format
        fmt = '%y%m%d%H%M%S'
        now_str = datetime.now().strftime(fmt)
        dir_str = "/Users/peej/Downloads/"

        file_str = dir_str + "shadow" + now_str + ".png"
        self.last_image.save(file_str, format='png')

        return event

    def q_key(self, event):
        self.main.destroy()
        return event

    def get_windwave_direction(self, wind_direction=None, wave_direction=None):

        if wind_direction is not None:
            self.wind_direction = float(wind_direction)
        else:
            self.wind_direction = float(input('What is the wind direction in '
                                              'degrees? \n'))
        if wave_direction is not None:
            self.wave_direction = float(wave_direction)
        else:
            self.wave_direction = float(input('What is the wave direction in '
                                              'degrees? \n'))
        print("**************************************\n"
              "*  Hit RETURN to show wind direction *\n"
              "**************************************\n"
              "*    click on the map to calibrate   *\n"
              "**************************************\n"
              "*      right mouse button resets     *\n"
              "**************************************\n")

        self.canvas.focus_set()

        print("wind direction: " + str(wind_direction) + "°")
        print("wave direction: " + str(wave_direction) + "°")

        # self.wind_direction = 190  # for testing
        # self.wave_direction = 170  # for testing

        return None

    # todo: should display arrows for wind and swell directions
    # todo: projection colors are straight up ugly
    # todo: create logic to find projection for south jetty as well
    def display_projection_on_map(self):
        # create blank overlay images for wind and waves
        wind_overlay = self.create_overlay()
        wave_overlay = self.create_overlay()

        # calculate the shadow for the north jetty
        wind_shadow_n = projection_calculations(self.coords['n_jetty_start'],
                                                self.coords['n_jetty_end'],
                                                self.coords['n_shoreline_end'],
                                                self.wind_direction)
        # draw shadows if they exist
        if wind_shadow_n != 'no shadow':
            draw_polygon(wind_overlay, wind_shadow_n, 'Green', 127)

        wave_shadow_n = projection_calculations(self.coords['n_jetty_start'],
                                                self.coords['n_jetty_end'],
                                                self.coords['n_shoreline_end'],
                                                self.wave_direction)
        if wave_shadow_n != 'no shadow':
            draw_polygon(wave_overlay, wave_shadow_n, 'red', 50)

        # calculate the shadow for the south jetty
        wind_shadow_s = projection_calculations(self.coords['s_jetty_start'],
                                                self.coords['s_jetty_end'],
                                                self.coords['s_shoreline_end'],
                                                self.wind_direction)
        # draw shadows if they exist
        if wind_shadow_s != 'no shadow':
            draw_polygon(wind_overlay, wind_shadow_s, 'Green', 127)

        wave_shadow_s = projection_calculations(self.coords['s_jetty_start'],
                                                self.coords['s_jetty_end'],
                                                self.coords['s_shoreline_end'],
                                                self.wave_direction)
        if wave_shadow_s != 'no shadow':
            draw_polygon(wave_overlay, wave_shadow_s, 'red', 50)

        shadow_composite = PIL.Image.alpha_composite(wind_overlay, wave_overlay)
        # shadow_composite = PIL.Image.blend(wind_overlay, wave_overlay, 0.5)
        composite = PIL.Image.alpha_composite(self.base_image, shadow_composite)
        composite = PIL.Image.composite(self.base_image,
                                        composite,
                                        self.shadow_mask)
        # in case we want to save this image later
        self.last_image = composite

        tkcomposite = combine_image_overlay(composite, self.overlay)
        self.update_canvas(tkcomposite)

        return None


# main tk frame (whatever that means)
root = Tk()
root.title("Wind and Wave Shadow Projections")

# initialize our canvas object
map_canvas = MainWindow(root, "surfside.png", "surfside_mask.png")

# prompt for wind and wave direction
# map_canvas.get_windwave_direction(wind_direction_input, swell_direction_input)
map_canvas.get_windwave_direction(90, 110)

# display the wind projection if possible
map_canvas.display_projection_on_map()

root.mainloop()

# root.destroy()  # kills the loop when you stop execution
