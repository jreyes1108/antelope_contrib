#!/usr/bin/env python

#{{{
# Run In Separate Process (RISP)
#
# A procedure that RUNS A FUNCTION ASYNCHRONOUSLY 
# IN A FORKED PROCESS (Availability: Macintosh, Unix). 
# The return from the specified function is written 
# into an anonymous memory map (mmap: requires +Python 2.5). 
# This can be useful for releasing resources used by 
# the function such as memory, updating a gui or cli widget, 
# or other weirdness.
# Most copied from code by Gary Eakins Feb 27 '08.
# Similar to a previous code by Muhammad Alkarouri on Apr 11 '07. 
#
# 
# @author:   Juan Reyes <reyes@ucsd.edu>
# @created:  2011-01-21
# @updated:  
#}}}

import sys, os, cPickle, time, mmap

try:
    import cPickle as pickle
except:
    import pickle

class ForkedProcessException(Exception):
    pass

def risp_s(size, func, *args, **kwds):
#{{{
    # size is in bytes
    # 102,400 bytes == 100 kilobytes
    # 5 megabytes == 1048576 bytes
    # 2 gigabyte == 1073741824 bytes
    try:
        mmsize = kwds['mmsize']
        del kwds['mmsize']
        mmsize = max(mmsize, size)
    except KeyError:
        mmsize = size

    mm = mmap.mmap(-1, mmsize) 
    pid = os.fork()

    if pid != 0:
        """
        print 'From parent:'
        print 'pid: [%s]' % pid
        print 'os.getpid: [%s]' % os.getpid()
        """

        try:
            """ Blocking method """
            #wpid, wstatus = os.waitpid(pid,0)

            """ Non-blocking method """
            while 1:
                wpid, wstatus = os.waitpid(pid, os.WNOHANG)
                if wpid == pid: break

        except KeyboardInterrupt:
            raise ForkedProcessException('User cancelled!')

        if os.WIFEXITED(wstatus):
            status = os.WEXITSTATUS(wstatus)

        elif os.WIFSIGNALED(wstatus):
            raise ForkedProcessException('Child killed by signal: %d' % os.WTERMSIG(wstatus))

        else:
            raise RuntimeError('Unknown child exit status!')

        mm.seek(0)

        if status  == 0:
            return  pickle.load(mm)
        else:
            raise pickle.load(mm)

    else:
        """
        print 'From child:'
        print 'pid: [%s]' % pid
        print 'os.getpid: [%s]' % os.getpid()
        """

        try:
            mm.seek(0)
            result = func(*args, **kwds)
            status = 0 # success
            pickle.dump(result, mm, pickle.HIGHEST_PROTOCOL)
        except pickle.PicklingError, exc:
            status = 2 # failure
            pickle.dump(exc, mm, pickle.HIGHEST_PROTOCOL)
        except (KeyboardInterrupt), exc:
            status = 4 # failure
            pickle.dump(ForkedProcessException('User cancelled!'), mm, pickle.HIGHEST_PROTOCOL)
        except ValueError:
            status = 3 # failure
            pstr = pickle.dumps(result, pickle.HIGHEST_PROTOCOL)
            mm.seek(0)
            pickle.dump(ForkedProcessException('mmsize: %d, need: %d' % (mmsize, len(pstr))), mm, pickle.HIGHEST_PROTOCOL)
        except (Exception), exc:
            status = 1 # failure
            pickle.dump(exc, mm, pickle.HIGHEST_PROTOCOL)

        os._exit(status)
#}}}

def risp(func, *args, **kwds):
#{{{
    # size default to 1024 bytes
    size = 1024
    try:
        mmsize = kwds['mmsize']
        del kwds['mmsize']
        mmsize = max(mmsize, size)
    except KeyError:
        mmsize = size

    mm = mmap.mmap(-1, mmsize) 
    pid = os.fork()

    if pid != 0:
        """
        print 'From parent:'
        print 'pid: [%s]' % pid
        print 'os.getpid: [%s]' % os.getpid()
        """

        try:
            """ Blocking method """
            #wpid, wstatus = os.waitpid(pid,0)

            """ Non-blocking method """
            while 1:
                wpid, wstatus = os.waitpid(pid, os.WNOHANG)
                if wpid == pid: break

        except KeyboardInterrupt:
            raise ForkedProcessException('User cancelled!')

        if os.WIFEXITED(wstatus):
            status = os.WEXITSTATUS(wstatus)

        elif os.WIFSIGNALED(wstatus):
            raise ForkedProcessException('Child killed by signal: %d' % os.WTERMSIG(wstatus))

        else:
            raise RuntimeError('Unknown child exit status!')

        mm.seek(0)

        if status  == 0:
            return  pickle.load(mm)
        else:
            raise pickle.load(mm)

    else:
        """
        print 'From child:'
        print 'pid: [%s]' % pid
        print 'os.getpid: [%s]' % os.getpid()
        """

        try:
            mm.seek(0)
            result = func(*args, **kwds)
            status = 0 # success
            pickle.dump(result, mm, pickle.HIGHEST_PROTOCOL)
        except pickle.PicklingError, exc:
            status = 2 # failure
            pickle.dump(exc, mm, pickle.HIGHEST_PROTOCOL)
        except (KeyboardInterrupt), exc:
            status = 4 # failure
            pickle.dump(ForkedProcessException('User cancelled!'), mm, pickle.HIGHEST_PROTOCOL)
        except ValueError:
            status = 3 # failure
            pstr = pickle.dumps(result, pickle.HIGHEST_PROTOCOL)
            mm.seek(0)
            pickle.dump(ForkedProcessException('mmsize: %d, need: %d' % (mmsize, len(pstr))), mm, pickle.HIGHEST_PROTOCOL)
        except (Exception), exc:
            status = 1 # failure
            pickle.dump(exc, mm, pickle.HIGHEST_PROTOCOL)

        os._exit(status)
#}}}

# Functions to run in a separate process
def treble(x, fail=False):
    if fail: 1/0
    return 3 * x
def suicide():
    os.kill(os.getpid(), 15)
def toobig():
    return '1234567890' * 1110
def nocanpickle():
    return globals()
def waitaround(seconds=1, fail=False):
    while seconds:
        if fail: 1/0
        time.sleep(1)
        seconds -= 1
    return ['here', 'is', 'the', 'array']
def nested():
    return {'array':['here', 'is', 'the', 'array'], 'nested':[1,2,3,4] }
def sysexit():
    sys.exit(9)

# General test function call
def run(func, *args, **kwargs):

    try:
        print '\nRunning %s(%s, %s) ' % (func.func_name, args, kwargs),
        result = risp(func, *args, **kwargs)
        print '%s returned: %s' % (func.func_name, result)

    except Exception, e:
        print '%s raised %s: %s' % (func.func_name, e.__class__.__name__, str(e))

def main():
    direct = True
    run(waitaround)
    run(waitaround, seconds=3)
    run(waitaround, fail=True)
    run(toobig)
    run(nested)
    run(nocanpickle)
    run(suicide)
    run(sysexit)
    run(treble, 4)

if __name__ == '__main__':
    main()

