# Add a logging handler so we can see the raw communication data
import time

import pusherclient

'''
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)
'''
global pusher


def callback(event):
    print(event)


# We can't subscribe until we've connected, so we use a callback handler
# to subscribe when able
def connect_handler(data):
    channel = pusher.subscribe('askreddit')
    channel.bind('new-listing', callback)


pusher = pusherclient.Pusher('b534d4fac76717b9872e')
pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

while True:
    # Do other things in the meantime here...
    time.sleep(1)
