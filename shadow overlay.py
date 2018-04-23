from tkinter import *
# from PIL import Image, ImageDraw, ImageTk
import PIL.Image, PIL.ImageTk, PIL.ImageDraw
import math


class MainWindow():
    """ Object used to track and update state of the canvas
    """
    def __init__(self, main, map_path: object) -> None:
        # main frame
        self.main = main
        # dictionary for coordinates
        self.coords = {}
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
        self.wind_direction = 999   # impossible direction initialization
        self.wave_direction = 999

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
        # create a transparent overlay pillow image object
        self.overlay = PIL.Image.new(mode='RGBA', size=self.base_image.size,
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
        self.canvas.bind("<Button 2>", self.reset_overlay)
        self.canvas.bind("<Return>", self.return_key)
        # frame will not be visible unless it is packed
        self.frame.pack(fill=BOTH, expand=1)

    # right mouse click resets the overlay screen
    def reset_overlay(self, event):
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

    def draw_point(self, click_point):
        """ click_point is the coordinate recorded during mouse click event
        """
        # draw click circles
        diameter = 10 / 2  # pixels
        point_circle = [(click_point.x - diameter, click_point.y - diameter),
                        (click_point.x + diameter, click_point.y + diameter)]

        # draw shape on the transparent overlay
        draw = PIL.ImageDraw.Draw(self.overlay)
        draw.ellipse(point_circle, fill='black')

        # # use function to combine image and updated overlay
        # tkcomposite = self.combine_image_overlay(self.base_image,
        #                                          self.overlay)
        #
        # return tkcomposite
        return None

    def draw_polygon(self, coords):
        draw = PIL.ImageDraw.Draw(self.overlay)
        draw.polygon(coords, fill=(145,0,145,100))

        # tkcomposite = self.combine_image_overlay(self.base_image,
        #                                          self.overlay)
        # return tkcomposite
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
            self.draw_polygon(coord_list)

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

    def combine_image_overlay(self, base_image, overlay):
        # combine original image and overlay
        composite = PIL.Image.alpha_composite(base_image, overlay)
        # composite.show()
        # create tk compatible image
        tkcomposite = PIL.ImageTk.PhotoImage(composite)
        # tkcomposite = PhotoImage(tkcomposite)

        return tkcomposite

    def get_windwave_direction(self):
        self.wind_direction = input('What is the wind direction in degrees? ')
        self.wave_direction = input('What is the wave direction in degrees?')

    def calculate_projection(self,
                             point_jetty_shore,
                             point_jetty_end,
                             point_shore,
                             shadow_dir):
        """ function that calculates the projected line from the end of the jetty to the shore.
        Arguments are coordinates for the point where the jetty meets the shore, where the jetty
        ends, and a point somewhere along the shoreline.

        Returns coordinates of the shadow line.
        """

        # jetty x and y components
        jettylengthx = math.fabs(point_jetty_end[0] - point_jetty_shore[0])
        print(jettylengthx)
        jettylengthy = math.fabs(point_jetty_end[1] - point_jetty_shore[1])
        print(jettylengthy)

        # called r12 in notes
        jettylength = math.sqrt(jettylengthx ** 2 + jettylengthy ** 2)
        print(jettylength)

        # shadow direction in radians is 180deg opposite of wave heading
        shadow_rad = math.radians(shadow_dir - 180.0)
        print(shadow_rad)

        # theta 12 from notes (jetty angle CW from east)
        jetty_angle_east = math.asin(jettylengthy / jettylength)
        print(jetty_angle_east)

        # shore x and y components
        shoremeasx = math.fabs(point_shore[0] - point_jetty_shore[0])
        print(shoremeasx)
        shoremeasy = math.fabs(point_shore[1] - point_jetty_shore[1])
        print(shoremeasy)

        # shore angle CCW from east
        shore_angle_east = math.atan(shoremeasy / shoremeasx)
        print(shore_angle_east)

        # shore plus jetty angle (angle gamma from notes)
        shore_jetty_angle = shore_angle_east + jetty_angle_east
        print(shore_jetty_angle)

        # angle between shadow and jetty (angle alpha in notes)
        jetty_shadow_angle = (math.pi / 2 - jetty_angle_east) + shadow_rad
        print(jetty_shadow_angle)

        # angle between shore and shadow (angle beta in notes)
        shore_shadow_angle = math.pi - (jetty_shadow_angle + shore_jetty_angle)
        print(shore_shadow_angle)

        # shadow length (length c in notes)
        shadow_length = jettylength * (
                    math.sin(shore_jetty_angle) / math.sin(shore_shadow_angle))
        print(shadow_length)

        # shadow x and y components
        shadow_lengthx = shadow_length * math.sin(shadow_rad)
        shadow_lengthy = shadow_length * math.cos(shadow_rad)

        # shadow-shore point
        shadowx = point_jetty_end[0] - shadow_lengthx
        shadowy = point_jetty_end[1] - shadow_lengthy
        point_shadow_shore = (shadowx, shadowy)
        print(point_shadow_shore)

        return point_shadow_shore

        # need to make sure that the shadow point coordinates are never negative

# main tk frame (whatever that means)
root = Tk()

# initialize our canvas object
map_canvas = MainWindow(root, "surfside.png")

# prompt for wind and wave direction
# map_canvas.get_windwave_direction()

root.mainloop()
# root.destroy()  # kills the loop when you stop execution

# one change