from tkinter import *
# from PIL import Image, ImageDraw, ImageTk
import PIL.Image, PIL.ImageTk, PIL.ImageDraw, PIL.ImageColor
import math


class MainWindow():
    """ Object used to track and update state of the canvas
    """
    def __init__(self, main, map_path: object, mask_path) -> None:
        # main frame
        self.main = main
        # dictionary with calibration points
        self.coords = {'n_jetty_start': (530, 549),
                       'n_jetty_end': (869, 919),
                       'n_shoreline_end': (905, 115)}
        # list of coordinates you need for calibration
        self.coord_labels = ['n_jetty_start',
                             'n_jetty_end',
                             # 's_jetty_start',
                             # 's_jetty_end',
                             # 'n_shoreline_start',
                             'n_shoreline_end',
                             # 's_shoreline_start',
                             # 's_shoreline_end'
                             ]
        self.wind_direction = 999.9   # impossible direction initialization
        self.wave_direction = 999.9

        # setting up a tkinter frame with scrollbars
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

        # mouseclick event
        self.canvas.bind("<Button 1>", self.savecoords)
        # reset canvas with right mouse click
        self.canvas.bind("<Button 2>", self.reset_everything)
        self.canvas.bind("<Return>", self.return_key)
        self.canvas.bind("<p>", self.p_key)
        # frame will not be visible unless it is packed
        self.frame.pack(fill=BOTH, expand=1)

    # right mouse click resets the overlay screen
    def reset_everything(self, event):
        # create a transparent overlay pillow image object
        self.overlay = PIL.Image.new(mode='RGBA', size=self.base_image.size,
                                     color=(0, 0, 0, 0))
        updated_image = self.combine_image_overlay(self.base_image,
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
        return None

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
        except:
            point_circle = [(click_point[0] - diameter,
                             click_point[0] - diameter),
                            (click_point[0] + diameter,
                             click_point[0] + diameter)]

        # draw shape on the transparent overlay
        draw = PIL.ImageDraw.Draw(self.overlay)
        draw.ellipse(point_circle, fill=poly_color)

        return None

    # todo: switch to drawing a polygon on an overlay passed to method
    def draw_polygon(self, overlay, coords, color='black', trans=80):
        # convert color name to RGBA tuple
        poly_color = (PIL.ImageColor.getrgb(color) + (trans,))

        draw = PIL.ImageDraw.Draw(overlay)
        draw.polygon(coords, fill=poly_color)

        return overlay

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
        label = self.label_grabber(self.coord_labels)

        if len(self.coord_labels) > 0:
            # update dict
            self.coords[label] = (click_point.x, click_point.y)
        elif len(self.coord_labels) == 0 and label != "done":
            self.coords[label] = (click_point.x, click_point.y)
            # this is where I draw the polygon
            coord_list = [self.coords["n_jetty_start"],
                          self.coords["n_jetty_end"],
                          self.coords["n_shoreline_end"]]
            self.draw_polygon(self.overlay, coord_list)

        print(self.coords)

        # combine images to format tk can use
        tkcomposite = self.combine_image_overlay(self.base_image,
                                                 self.overlay)

        # update the canvas with composit image by calling method below
        self.update_canvas(tkcomposite)

        return None

    # function called on key click
    def return_key(self, event):
        print(event.keysym)
        # calculate the shadow
        wind_shadow = self.calculate_projection(self.coords['n_jetty_start'],
                                                self.coords['n_jetty_end'],
                                                self.coords['n_shoreline_end'],
                                                self.wind_direction)
        wave_shadow = self.calculate_projection(self.coords['n_jetty_start'],
                                                self.coords['n_jetty_end'],
                                                self.coords['n_shoreline_end'],
                                                self.wave_direction)

        # create blank overlay images for wind and waves
        wind_overlay = self.create_overlay()
        wave_overlay = self.create_overlay()
        # conditional_overlay = self.create_overlay()

        # generate shadows
        # shadow_transparency = .5  # 0 is transparent 1 is opaque
        # alpha = int(shadow_transparency * 255)
        self.draw_polygon(wind_overlay, wind_shadow, 'Green', 127)
        self.draw_polygon(wave_overlay, wave_shadow, 'red', 50)
        # self.draw_polygon(conditional_overlay, wind_shadow, 'yellow', alpha)

        shadow_composite = PIL.Image.alpha_composite(wind_overlay, wave_overlay)
        # shadow_composite = PIL.Image.blend(wind_overlay, wave_overlay, 0.5)
        composite = PIL.Image.alpha_composite(self.base_image, shadow_composite)
        composite = PIL.Image.composite(self.base_image,
                                        composite,
                                        self.shadow_mask)
        # in case we want to save this image later
        self.last_image = composite

        tkcomposite = self.combine_image_overlay(composite, self.overlay)
        self.update_canvas(tkcomposite)

    # function to prompt for next label coordinate
    def label_grabber(self, labels):

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

    # open generated image in preview on mac
    def p_key(self, event):
        self.last_image.show()

    def combine_image_overlay(self, base_image, overlay):
        # combine original image and overlay
        composite = PIL.Image.alpha_composite(base_image, overlay)
        # composite.show()
        # create tk compatible image
        tkcomposite = PIL.ImageTk.PhotoImage(composite)
        # tkcomposite = PhotoImage(tkcomposite)

        return tkcomposite

    def get_windwave_direction(self, wind_direction=None, wave_direction=None):

        if wind_direction is None:
            self.wind_direction = float(input('What is the wind direction in '
                                              'degrees? \n'))
        if wave_direction is None:
            self.wave_direction = float(input('What is the wave direction in '
                                              'degrees? \n'))
        print("**************************************\n"
              "*  Hit RETURN to show wind direction *\n"
              "**************************************\n"
              "*    click on the map to calibrate   *\n"
              "**************************************\n"
              "*      right mouse button resets     *\n"
              "**************************************\n")

        self.wind_direction = wind_direction
        self.wave_direction = wave_direction
        self.canvas.focus_set()

        print("wind direction: " + str(wind_direction) + "°")
        print("wave direction: " + str(wave_direction) + "°")

        # self.wind_direction = 190  # for testing
        # self.wave_direction = 170  # for testing

        return None

    def calculate_projection(self,
                             point_jetty_shore,
                             point_jetty_end,
                             point_shore,
                             shadow_dir):
        """ function that calculates the projected line from the end of the
        jetty to the shore. Arguments are coordinates for the point where the
        jetty meets the shore, where the jetty ends, and a point somewhere
        along the shoreline.

        Returns coordinates of the shadow line.
        """

        # jetty x and y components
        jettylengthx = point_jetty_end[0] - point_jetty_shore[0]
        jettylengthy = point_jetty_end[1] - point_jetty_shore[1]
        # jettylengthx = math.fabs(point_jetty_end[0] - point_jetty_shore[0])
        # jettylengthy = math.fabs(point_jetty_end[1] - point_jetty_shore[1])

        # called r12 in notes
        jettylength = math.sqrt(jettylengthx ** 2 + jettylengthy ** 2)

        # shadow direction in radians is 180deg opposite of wave heading
        shadow_rad = math.radians(shadow_dir - 180.0)

        # theta 12 from notes (jetty angle CW from east)
        jetty_angle_east = math.asin(jettylengthy / jettylength)

        # shore x and y components
        shoremeasx = point_shore[0] - point_jetty_shore[0]
        shoremeasy = point_shore[1] - point_jetty_shore[1]
        # shoremeasx = math.fabs(point_shore[0] - point_jetty_shore[0])
        # shoremeasy = math.fabs(point_shore[1] - point_jetty_shore[1])

        # shore angle CCW from east
        shore_angle_east = math.atan(math.fabs(shoremeasy / shoremeasx))

        # shore plus jetty angle (angle gamma from notes)
        shore_jetty_angle = shore_angle_east + jetty_angle_east

        # angle between shadow and jetty (angle alpha in notes)
        # should always be positive or wrong jetty selected
        jetty_shadow_angle = (math.pi / 2 - jetty_angle_east) + shadow_rad

        # angle between shore and shadow (angle beta in notes)
        shore_shadow_angle = math.pi - (jetty_shadow_angle + shore_jetty_angle)

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

        #something wrong with this debugging code anyway
        # self.draw_point(point_shadow_shore, 'blue',)
        # self.draw_point(point_jetty_shore, 'black')
        # self.draw_point(point_jetty_end, 'red')

        # return coordinates needed to plot polygon
        return (point_jetty_shore, point_jetty_end, point_shadow_shore)

        # need to make sure that the shadow point coordinates are never negative

# main tk frame (whatever that means)
root = Tk()

# initialize our canvas object
map_canvas = MainWindow(root, "surfside.png", "surfside_mask.png")

# prompt for wind and wave direction
# map_canvas.get_windwave_direction(190, 160)
map_canvas.get_windwave_direction(160, 190)

# debugging code
# map_canvas.calculate_projection((602,627),(869,919),(866,261),190)

root.mainloop()

# root.destroy()  # kills the loop when you stop execution

# one change