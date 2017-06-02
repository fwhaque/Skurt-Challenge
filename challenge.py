import argparse
import logging
import logging.handlers
import time

import requests

import emailconfig


def call_api(car_id):
    '''Performs a 'GET' call to the skurt interiew API, passing a vehicle's ID.
    Args:
        car_id: the identifier for an individual vehicle
    Returns:
        location: a list of two coordinates, x,y, of the car's location eg [0.0, 1.0]
        bounds: a list of x,y, points, each one representing a vertex in the geofence's bounding polygon eg [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    '''
    try:
        url = "http://skurt-interview-api.herokuapp.com/carStatus/{}".format(
            car_id)

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        location = data["features"][0]["geometry"]["coordinates"]
        bounds = data["features"][1]["geometry"]["coordinates"][0]

        return location, bounds
    except requests.exceptions.RequestException as e:
        logger.error("Error polling car " + str(car_id) +
                     "." " API error: " + str(e))


def poll_api(car_ids, interval=240):
    '''Sets up a loop in which calls to an API are made at certain intervals. The Api returns a bounding polyon and a locaton coordinate to check for inclusion. If not, a warning email is sent with the car ID. Loop will continue until process is terminated.
    Args:
        car_ids: a list of vehicle IDs
        interval: the polling period in seconds. Defaults to 240s (4m)
    Returns:
        None
    '''
    out_of_bound_cars = []
    while True:
        logger.info("polling all vehicles...")
        for car_id in car_ids:
            logger.info("polling car " + str(car_id))
            location, bounds = call_api(car_id)
            if not is_in_bounds(location[0], location[1], bounds):
                out_of_bound_cars.append(car_id)
        logger.info("all vehicles polled this period")
        if out_of_bound_cars:
            logger.warning(
                "the following vehicles are outside their designated geofences: " + str(out_of_bound_cars))
            out_of_bound_cars.clear()
        time.sleep(interval)


def is_in_bounds(x, y, bounds):
    '''Checks to see whether an (x,y) point is within a polygon defined by a set of vertices
    Algorithm details here: https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm
    Python implementaiton taken from here: http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html
    Args:
        x: latitude of point to be checked
        y: longitude of point to be checked
        bounds: list of pairs of points, each pair defining a vertex of a polygon, eg [[0.0, 0.0], [0.0 ,1.0], [1.0, 0.0], [1.1, 1.1]]
    Returns:
        bool: True if point (x, y) is in bounds, False otherwise
    '''
    # check if point is a vertex
    for point in bounds:
        if x == point[0] and y == point[1]:
            return True
    # check if point is on a boundary
    for i in range(len(bounds)):
        p1 = None
        p2 = None
        if i == 0:
            p1 = bounds[0]
            p2 = bounds[1]
        else:
            p1 = bounds[i - 1]
            p2 = bounds[i]
        if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
            return True
        if p1[0] == p2[0] and p1[0] == x and y > min(p1[1], p2[1]) and y < max(p1[1], p2[1]):
            return True
    # regular in-bound checks
    n = len(bounds)
    inside = False
    p1x, p1y = bounds[0]
    for i in range(n + 1):
        p2x, p2y = bounds[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    if inside:
        return True
    else:
        return False


def parse_args():
    '''Parsing cmd line args
    Args:
        None
    Returns:
        args: a dictonary of arguments as keys, with the corresponding value as entered at program invocation eg {mode: test}
    '''
    parser = argparse.ArgumentParser(
        description="A sample daemon that emails Skurt engineering whenever vehicles leave their defined geofences")
    parser.add_argument(
        "-m", "--mode", choices=["test", "normal"], default="normal", help="set test mode")
    args = vars(parser.parse_args())
    return args


def configure_logger():
    '''Sets up a logger with two handlers- one for logging to a file, and another for loggint to email via SMTP.
    Args:
        None
    Returns:
        logger: a standard logger instance
    '''
    # Logger setup
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # 2 handlers; file and email
    file_handler = logging.FileHandler("challenge.log")
    file_handler.setLevel(logging.INFO)
    email_handler = logging.handlers.SMTPHandler(mailhost=(emailconfig.mailhost, emailconfig.port),
                                                 fromaddr=emailconfig.fromaddrs,
                                                 toaddrs=emailconfig.toaddrs,
                                                 subject=emailconfig.subject,
                                                 credentials=(
                                                     emailconfig.username, emailconfig.password),
                                                 secure=emailconfig.secure)
    email_handler.setLevel(logging.WARNING)
    # format of records
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    email_handler.setFormatter(formatter)
    # add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(email_handler)
    return logger


def main(arguments):
    if arguments["mode"] == "test":
        logger.info("running in test mode...")
        car_ids = [11]
        poll_api(car_ids, 15)
    else:
        logger.info("running in normal mode...")
        car_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # polls at default interval; override with second arg if required, time
        # in seconds
        poll_api(car_ids)


if __name__ == "__main__":
    logger = configure_logger()
    arguments = parse_args()
    main(arguments)
