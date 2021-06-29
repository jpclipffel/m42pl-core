| zmq_sub topic='webcam'
| decode {zmq.frames[0]} with 'msgpack'
| cv2_show cv2.frame
