import pika 
import tornado.gen 
from tornado.gen import Future

class TornadoPika(pika.TornadoConnection):
    def __init__(self, params):
        self.future = Future()
        self.conn = False 
        super(TornadoPika, self).__init__(params, self._on_open, self._on_open_err)
    def _on_open(self, *args):
        self.future.set_result(True)
    def _on_open_err(self, *args):
        self.future.set_result(False)
    
    def connected(self):
        return self.future 
    
    def _on_open_channel(self, data = None):
        self.future.set_result(data)
    def get_channel(self, channel_number=None):
        self.future = Future()
        self.channel(self._on_open_channel, channel_number)
        return self.future

@tornado.gen.coroutine 
def work():
    params = pika.ConnectionParameters()
    conn = TornadoPika(params)
    ret = yield conn.connected()
    print(ret)
    
    ch = yield conn.get_channel()
    
    yield tornado.gen.Task(ch.queue_declare, queue='t1', auto_delete = True)
    yield tornado.gen.Task(ch.exchange_declare, exchange = 'test1', auto_delete = True)

    while True:
        ch.basic_publish('test1', 'test123', 'test123')
        yield tornado.gen.sleep(1)
    
    


if __name__ == '__main__':
    loop = tornado.ioloop.IOLoop.instance()
    
    work()
    loop.start()