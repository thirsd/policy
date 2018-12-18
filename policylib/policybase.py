
import signal,functools #下面会用到的两个库 

class PolicyError(Exception): pass #定义一个策略基类
class RuntimeError(PolicyError): pass #定义一个Exception，后面超时抛出 
class TypeError(PolicyError): pass

def set_timeout(num, callback):
    '''
        def after_timeout():  # 超时后的处理函数
            print("Time out!")
        
        @set_timeout(2, after_timeout)  # 限时 2 秒超时
        def connect():  # 要执行的函数
            time.sleep(3)
    '''
    def wrapped_function(func):
        @wraps(func)
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError
 
        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(num)  # 设置 num 秒的闹钟
                print('start alarm signal.')
                r = func(*args, **kwargs)
                print('close alarm signal.')
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError as e:
                callback()
 
        return to_do
 
    return wrapped_function


from threading import Thread
import time

ThreadStop = Thread._Thread__stop
 
def set_timeout(timeout):
    def decorator(func):

        @wraps(func)
        def decorator2(*args,**kwargs):
            class TimeLimited(Thread):
                def __init__(self,_error= None,):
                    Thread.__init__(self)
                    self._error =  _error
 
                def run(self):
                    try:
                        self.result = func(*args,**kwargs)
                    except Exception,e:
                        self._error = str(e)
 
                def _stop(self):
                    if self.isAlive():
                        ThreadStop(self)
 
            t = TimeLimited()
            t.start()
            t.join(timeout)
 
            if isinstance(t._error,RuntimeError):
                t._stop()
                raise RuntimeError('timeout for %s' % (repr(func)))
 
            if t.isAlive():
                t._stop()
                raise RuntimeError('timeout for %s' % (repr(func)))
 
            if t._error is None:
                return t.result
 
        return decorator2
    return decorator



from functools import wraps

class logit(object):
    def __init__(self, logfile='out.log'):
        self.logfile = logfile
 
    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            # 打开logfile并写入
            with open(self.logfile, 'a') as opened_file:
                # 现在将日志打到指定的文件
                opened_file.write(log_string + '\n')
            # 现在，发送一个通知
            self.notify()
            return func(*args, **kwargs)
        return wrapped_function
 
    def notify(self):
        # logit只打日志，不做别的
        pass

from functools import wraps
def type_limit(*typeLimit,**returnType):
    '''
        example:
            @type_limit(int,int)
            def test(x,y):
                return x+y
    '''
    def test_value_type(func):
        @wraps(func)
        def wrapper(*param,**kw):
            length = len(typeLimit)
            if length != len(param):
                raise TypeError("The list of typeLimit and param must have the same length")
            for index in range(length):
                t = typeLimit[index]
                p = param[index]
                if not isinstance(p,t):
                    raise TypeError("The param %s should be %s,but it's %s now!"%(str(p),type(t()),type(p)))  
            res = func(*param,**kw)
            if "returnType" in returnType:
                limit = returnType["returnType"]
                if  not isinstance(res,limit):
                    raise TypeError("This function must return a value that is %s,but now it's %s"%(limit,type(res) ) )
            return res
        return wrapper
    return test_value_type

import sys,os,linecache
def trace(func):
    def globaltrace(frame, why, arg):
        if why == "call": 
            return localtrace
        return None
    def localtrace(frame, why, arg):
        if why == "line":
            # record the file name and line number of every trace 
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            bname = os.path.basename(filename)
            print "{}({}): {}".format(bname, lineno,
                linecache.getline(filename, lineno).strip('\r\n')),
        return localtrace

    @wraps(func)
    def wrapped_function(*args, **kwds):
        sys.settrace(globaltrace)
        result = func(*args, **kwds)
        sys.settrace(None)
        return result
    return wrapped_function