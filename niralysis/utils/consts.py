
# tables headers

TIME_COLUMN = 'Time'
END_COLUMN = 'End'
START_COLUMN = 'Start'
DURATION_COLUMN = 'Duration'
EVENT_COLUMN = 'Event'


# event markers

EVENT_BEGIN = 'begin'
EVENT_END = 'end'
EVENTS = ['begin:Yael', 'end:Yael', 'begin:Alon', 'end:Alon', 'begin:Roy', 'end:Roy', 'begin:Sahar', 'end:Sahar', 
          'begin discussion:A','end discussion:A', 'begin discussion:B','end discussion:B', 'begin open discussion', 'end open discussion', 
          'begin:Yael', 'end:Yael', 'begin:Alon', 'end:Alon', 'begin:Roy', 'end:Roy', 'begin:Sahar', 'end:Sahar']
CANDIDATES = ['Roy', 'Sahar', 'Alon', 'Yael']
DISCUSSION = ['discussion A', 'discussion B', 'open discussion']
# fps

FRAMES_PER_SECOND = 30  # number of frames in a group for analysis of movement

# key points

HEAD_KP = [0,1,2,5,15,16,17,18]
ARM_KP = [1,2,3,4,5,6,7,8]