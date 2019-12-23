import socketio
from flask import Flask, Blueprint, request, make_response, jsonify
from google.cloud import datastore
from db import get, update, delete, getbyname, from_datastore, secret, getSessionByCode, getEventsByUserId
from JSONObject.user import User
from jose import jwt
from functools import wraps
from auth import auth_required
from JSONObject.session import Session
import json

session = Blueprint('session', __name__)

sio = socketio.Server(logger=False, async_mode='threading', cors_allowed_origins='*')

@sio.on('message')
def message(sid, msg):
    user = sio.get_session(sid)
    sio.emit('message', msg, room=user.get('room'))

@sio.on('join')
def join(sid, room, username):
    sio.enter_room(sid, room, username)
    sio.save_session(sid, {'username': username, 'room': room})
    sio.emit('connect', username, room=room, skip_sid=sid)

@sio.event
def connect(sid, environ):
    print('Connected', sid)

@sio.event
def disconnect(sid):
    user = sio.get_session(sid)
    sio.leave_room(sid, user.get('room'))
    sio.emit('leave', sio.get_session(sid)['username'], room=sio.get_session(sid)['room'], skip_sid=sid)

@session.route('/<int:id>')
@auth_required
def getSession(id):
    room = get(id, 'session')
    if room is None:
        return make_response(jsonify(id='Room does not exist'), 404)
    if not request.id in room.get('participants'):
        return make_response(jsonify(id='You need to enter the code to access this room'), 400)

    return make_response(jsonify(id=id, code=room.get('code'), hostId=room.get('hostId'), title=room.get('title'), location=room.get('location'), 
            starttime=room.get('starttime'), endtime=room.get('endtime'), votingtime=room.get('votingtime'), 
            weekends=room.get('weekends'), participants=room.get('participants')), 200)

@session.route('/<int:id>/events')
@auth_required
def getSessionEvents(id):
    room = get(id, 'session')
    if room is None:
        return make_response(jsonify(id='Room does not exist'), 404)
    if not request.id in room.get('participants'):
        return make_response(jsonify(id='You need to enter the code to access this room'), 400)
    
    event_list = []
    for participant in room.get('participants'):
        events = getEventsByUserId(participant)
        if len(events) != 0: 
            for event in events:   
                event['id'] = event.id 
                event_list.append(event)

    return make_response(jsonify(events=event_list), 200)

@session.route('/<int:id>', methods=['DELETE'])
@auth_required
def deleteSession(id):
    room = get(id, 'session')
    if request.id == room.get('hostId'):
        delete('session', id)
        id=str(id)
        sio.emit('close', 'Room was closed', room=id)
        return make_response(jsonify(id=id), 200)     
    return make_response(jsonify(code='You need host permission to delete this room'), 400)
    

@session.route('/join', methods=['POST'])
@auth_required
def joinSession():
    data = request.get_json()
    
    code = data.get('code')
   
    errors = {}
    if(code is None): errors['code'] = 'Code is empty'

    if len(errors.keys()) == 0:
        room = getSessionByCode(code)
        if len(room) == 0:
            return make_response(jsonify(username='Room does not exist'), 400)
        else:
            room = from_datastore(room[0])
            if not request.id in room['participants']:
                room['participants'].append(request.id)
                update(room, 'session', room.get('id'))
            return make_response(jsonify(id=room.get('id'), hostId=room.get('hostId'), title=room.get('title'), location=room.get('location'), 
            starttime=room.get('starttime'), endtime=room.get('endtime'), votingtime=room.get('votingtime'), 
            weekends=room.get('weekends'), participants=room.get('participants')), 200)
    else: 
        return make_response(jsonify(errors=errors), 400)

@session.route('/host', methods=['POST'])
@auth_required
def hostSess():
    data = request.get_json()
    if data is None: 
        return make_response('No data was sent', 400)
    hostId = request.id
    title = data.get('title')
    location = data.get('location')
    starttime = data.get('starttime')
    endtime = data.get('endtime')
    votingtime = data.get('votingtime')
    weekends = data.get('weekends')

    # TODO Validation 
    errors = {}
    if(title is None): errors['title'] = 'Title is empty'
    if(location is None): errors['location'] = 'Location is empty'
    if(starttime is None): errors['starttime'] = 'Start time is empty'
    if(endtime is None): errors['endtime'] = 'End time is empty'
    if(votingtime is None): errors['votingtime'] = 'Voting time is empty'
    if(weekends is None): errors['weekends'] = 'Weekends is empty'

    if len(errors.keys()) == 0:
        # TODO Sessions cannot generate the same code
        room = Session(hostId, title, location, starttime, endtime, votingtime, weekends)
        update(room.__dict__, 'session')
        room = getSessionByCode(room.code) ## TODO Find a better way to extract session id than fetching it from db
        room = from_datastore(room[0])
        return make_response(jsonify(id=room.get('id'), code=room.get('code'), hostId=hostId, title=title, location=location, starttime=starttime,
                endtime=endtime, votingtime=votingtime, weekends=weekends, participants=room.get('paprticipants')), 200)
    else:
        return make_response(jsonify(errors=errors), 400)

############### Voting.py ###############

@sio.on('startVote')
def startVote(sid):
    # TODO: Validate whether initiator = host
    # TODO：Client on beginVote => move to voting page
    sio.emit('beginVote', room=sio.get_session(sid)['room'], skip_sid=sid)
    
    # Run algorithm and store the generated available timeslots to session
    availableSlots = None

    # Add available slots to session
    room = sio.get_session(sid)['room']
    room = getSessionByCode(room)
    room = from_datastore(room[0])
    dictionary = dict()
    dictionary['availableSlots'] = availableSlots
    session[room] = dictionary

    # start the timer here???? 
    global timer
    timer = Countdown(room.get('votingTime'), room)
    timer.start()

# TODO: Client invokes REST API
@lobby.route('/<int:id>/getAvailableTimeslots')
def getTimeslots(id):
    while('availableSlots' not in session[id]):
       print ("Generating slots...")
    return session[id]['availableSlots']

@sio.on('vote')
def vote(sid, timeslot):
    # add vote of each participant to session
    room = sio.get_session(sid)['room']
    dictionary = session[room]
    if 'vote' in dictionary:
        votelist = dictionary['vote']
        if timeslot in votelist:
            votelist[timeslot] = votelist[timeslot] + 1
        else:
            votelist[timeslot] = 1
    else:
        votelist = dict()
        votelist[timeslot] = 1
    dictionary['vote'] = votelist
    session[room] = dictionary
    # get number of participant in the room
    room_obj = getSessionByCode(room)
    room_obj = from_datastore(room[0])
    total = len(room_obj['participants'])
     # check if every participant has already voted
    num_of_votes = sum(list(votelist.values()))
    if (total == num_of_votes):
        timer.cancel()
        result = majorityVote(votelist)
        sio.emit('result', result, room=room)
    # onResult needed in client side

# Countdown Timer
class Countdown(threading.Thread):
    def __init__(self, sec, room):
        threading.Thread.__init__(self)
        self.sec = sec
        self.room = room
        self.stopFlag = False

    def run(self):
        while not self.stopFlag:
            for secs in range(self.sec, 0, -1):
                # emit countdown time to client
                sio.emit('countdown', secs, room=self.room)
                sleep(1)
            sio.emit('countdown', 0, room=self.room)
            # perform majority voting when timeout
            votelist = session[self.room]['vote']
            result = majorityVote(votelist)
            sio.emit('result', result, room=self.room)
    
    def cancel(self):
        self.stopFlag = True
        

    
def majorityVote(votelist):
    return max(votelist, key=votelist.get)



