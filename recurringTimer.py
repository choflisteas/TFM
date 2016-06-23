# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 12:33:54 2016

@author: gonzalo
"""

import threading


class recurringTimer(threading.Timer):
    """ Implementación de una clase que permite la invocación
    de un método de forma periódica"""
     
    def __init__ (self, *args, **kwargs):
        threading.Timer.__init__ (self, *args, **kwargs) 
        self.setDaemon (True)
        self._running = 0
        self._destroy = 0
        self.start()
 
    def run (self):
        while True:
            self.finished.wait (self.interval)
            if self._destroy:
                return;
            if self._running:
                self.function (*self.args, **self.kwargs)
 
    def start_timer (self):
        self._running = 1
 
    def stop_timer (self):
        self._running = 0
 
    def is_running (self):
        return self._running
 
    def destroy_timer (self):
        self._destroy = 1;
        
if __name__ == "__main__":
    def sayhi (name):
        print ('hi %s' % name)
    def sayHi():
        print("Hi!!")
 
    t = recurringTimer(1.5, sayHi)
    t.start_timer()