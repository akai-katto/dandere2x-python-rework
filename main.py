import time

from dandere2xlib.core import Dandere2x
from dandere2xlib.d2xsession import get_dandere2x_session

dandere2x_session = get_dandere2x_session()

start = time.time()
d2x = Dandere2x(dandere2x_session)
d2x.process()
print(f"end: {time.time() - start}")