#!/usr/bin/python3
# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
import multiprocessing
import re
import random
import tornado.ioloop
import tornado.web
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

class PixelState:
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.value = 0

    def get_value(self):
        return self.value

    def reset(self):
        self.lock.acquire()
        try:
            self.value = 0;
        finally:
            self.lock.release()

    def update(self):
        self.lock.acquire()
        try:
            self.value = self.value + 1
        finally:
            self.lock.release()


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, pixel_state):
        self.pixel_state = pixel_state

    def get(self):
        self.write("Hello, world. Current count is " + str(self.pixel_state.value.get_value()))
        self.pixel_state.value.reset()

def pixel_loop(pixel_state):
    while True:
            time.sleep(3)
            pixel_state.update()
            logging.debug(pixel_state.get_value())

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        try:

            ps = multiprocessing.Value('pixel_state', PixelState())

            p = Process(target=pixel_loop, args=(ps))
            p.start()

            app = tornado.web.Application([(r"/", MainHandler, {"pixel_state" : ps})])
            app.listen(80)
            tornado.ioloop.IOLoop.current().start()
            p.join()
        except KeyboardInterrupt:
            p.join()