from flask import Flask , render_template , request , session , redirect , url_for
from flask_socketio import join_room , leave_room , send , SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    
    return code

@app.route("/" , methods= ["POST" , "GET"])
def home():

    session.clear()                                             # good practice  

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join" , False)                 # since a button , there is no value associated with it 
        create = request.form.get("create" , False)             # hence the default value , if not clicked is false , rather than none

        if not name:
            return render_template('home.html', error="Enter a Name , before proceeding" , code=code , name=name)

        if not join != False and not code:
            return render_template('home.html', error="Enter room Code , before proceeding", code=code , name=name)

        room = code 

        if create != False:                                         # user clicked on create to create a new room 
            room = generate_unique_code(4)

            rooms[room] = { "members" : 0 , "messages" : [] }

        elif code not in rooms:
            return render_template('home.html', error="Room does not exist" , code=code , name=name)

        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))



    return render_template('home.html')


@app.route("/room")
def room():

    room = session.get("room")

    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html")


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return 
    
    if room not in rooms:
        return 
    
    join_room(room)
    send({"name":name , "message":"has entered the room {room} "} , to=room )
    rooms[room]["members"] += 1

    print(f"{name} joined the room ")


@socketio.on("disconnect")
def disconnect():

    room = session.get("room")
    name = session.get("name")

    leave_room(room)

    if room in rooms:
        rooms[room]['members'] -= 1

        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name":name , "message":"has left the room {room}"} , to=room )
    print(f"{name} joined the room ")


if __name__ == "__main__":
    socketio.run(app , debug = True)


