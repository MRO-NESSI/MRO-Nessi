# Chapter 11: Responsive Interfaces, Using Threads and Timers
# Recipe 3: Threading Tools
#
import wx
import threading
from types import FunctionType, MethodType

__all__ = ['callafter', 'synchfunct', 'ClassSynchronizer']

def callafter(funct):
    """Decorator to automatically use CallAfter if
    a method is called from a different thread.
    """
    def callafterwrap(*args, **kwargs):
        if wx.Thread_IsMain():
            return funct(*args, **kwargs)
        else:
            wx.CallAfter(funct, *args, **kwargs)
    callafterwrap.__name__ = funct.__name__
    callafterwrap.__doc__ = funct.__doc__
    return callafterwrap

class Synchronizer(object):
    """Synchronize CallAfter calls"""
    def __init__(self, funct, args, kwargs):
        super(Synchronizer, self).__init__()

        # Attributes
        self.funct = funct
        self.args = args
        self.kwargs = kwargs
        self._synch = threading.Semaphore(0)

    def _AsynchWrapper(self):
        """This part runs in main gui thread"""
        try:
            self.result = self.funct(*self.args,
                                     **self.kwargs)
        except Exception, msg:
            # Store exception to report back to
            # the calling thread.
            self.exception = msg
        # Release Semaphore to allow processing back 
        # on other thread to resume.
        self._synch.release()

    def Run(self):
        """Call from background thread"""
        # Make sure this is not called from main thread
        # as it will result in deadlock waiting on the
        # Semaphore.
        assert not wx.Thread_IsMain(), "Deadlock!"
        # Make the asynchronous call to the main thread
        # to run the function.
        wx.CallAfter(self._AsynchWrapper)
        # Block on Semaphore release until the function
        # has been processed in the main thread by the
        # UI's event loop.
        self._synch.acquire()
        # Return result to caller or raise error
        try:
            return self.result
        except AttributeError:
            raise self.exception

def synchfunct(funct):
    """Decorator to synchronize a method call from a worker
    thread to the GUI thread.
    """
    def synchwrap(*args, **kwargs):
        if wx.Thread_IsMain():
            # called in context of main thread so
            # no need for special synchronization
            return self.funct(*args, **kwargs)
        else:
            synchobj = Synchronizer(funct, args, kwargs)
            return synchobj.Run()
            
    synchwrap.__name__ = funct.__name__
    synchwrap.__doc__ = funct.__doc__
    return synchwrap

class ClassSynchronizer(type):
    """Metaclass to make all methods in a class threadsafe"""
    def __call__(mcs, *args, **kwargs):
        obj = type.__call__(mcs, *args, **kwargs)

        # Wrap all methods/functions in the class with
        # the synchfunct decorator.
        for attrname in dir(obj):
            attr = getattr(obj, attrname)
            if type(attr) in (MethodType, FunctionType):
                nfunct = synchfunct(attr)
                setattr(obj, attrname, nfunct)

        return obj
