from flask import *
from psycopg2 import *
from datetime import date
app = Flask(__name__)
app.secret_key = "123"


def connect_db():
    return connect(
        database="cypruseventhub",
        user="postgres",
        password="cypruseventhub",
        host="localhost",
        port="5432"
    )


def is_user_organizer(uname):
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Check if the user exists in the organizer table
        cur.execute('SELECT ousername FROM organizer WHERE ousername = %s', (uname,))
        org = cur.fetchone()
        print(org)
        if org is not None:
            cur.close()
            conn.close()
            return True
        else:
            cur.close()
            conn.close()
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def is_user_customer(uname):
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Check if the user exists in the customer table
        cur.execute('SELECT cusername FROM customer WHERE cusername = %s', (uname,))
        customer = cur.fetchone()
        print(customer)
        if customer is not None:
            cur.close()
            conn.close()
            return True
        else:
            cur.close()
            conn.close()
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


@app.route('/offerRide',methods=['POST', 'GET'])
def offerRide():
    #check for car registeration
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT pnumber FROM car WHERE rusername = %s",(session['username'],))
    pnumber = cur.fetchone()
    if pnumber is None:
        return render_template('rideOfferForm.html', msg="Please register your car first!")
    if request.method == 'POST' and "username" in session:
        username = session['username']
        seats = request.form['seats-available']
        fromLocation = request.form['from-location']
        offerDate = request.form['date-time']
        eventid = request.form['event']
        price = request.form['price']
        cur.execute("SELECT rid FROM ridebooking ORDER BY rid DESC LIMIT 1")
        rid = cur.fetchone()[0]
        cur.execute("INSERT INTO ridebooking VALUES (%s, %s, %s, %s, %s, %s, %s)",(rid+1, seats, fromLocation, offerDate, eventid, username, price))
        conn.commit()
        conn.close()
        return render_template('offerRide_success.html')
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT eid, ename, elocation, dateandtime FROM events")
    events = cur.fetchall()
    conn.close()
    return render_template('rideOfferForm.html', events=events)


@app.route('/bookEvent', methods=['GET','POST'])
def book_event():
    if request.method == 'POST':
        eventid = request.form.get('event_id')
        datebooked = date.today().strftime('%Y-%m-%d')
        isPaid = 'N'
        username = session.get('username')
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT ebID FROM Eventbooking ORDER BY ebid DESC LIMIT 1")
        lastID = 0
        res = c.fetchone()
        print()
        if res is not None:
            lastID = res[0]
            print(lastID)
        c.execute("SELECT COUNT(*) FROM Eventbooking WHERE eventid = %s", (eventid,))
        result = c.fetchone()
        if result[0] > 0:
            return redirect(url_for('exploreEvents', msg="You already booked this event!"))
        c.execute("INSERT INTO Eventbooking VALUES (%s, %s, %s, %s, %s)",
                  (lastID+1, datebooked, isPaid, eventid, username))
        c.execute("UPDATE Events SET maxticket = maxticket - 1 WHERE eid = %s", (eventid,))
        conn.commit()
        conn.close()
        return redirect(url_for('myBookings'))

@app.route('/myBookings')
def myBookings():
    username = session.get('username')
    conn = connect_db()
    c = conn.cursor()
    c.execute("""SELECT 
    e.eid,
    e.ename,
    e.dateandtime,
    e.elocation,
    e.description,
    e.tprice,
    b.datebooked
    FROM 
    events e
    JOIN 
    eventbooking b ON e.eid = b.eventid
    WHERE 
    b.username = %s""", (username,))
    bookings = c.fetchall()
    conn.close()
    return render_template('bookings.html', records=bookings)


@app.route('/customerProfile')
def customerProfile():
    return redirect(url_for('myBookings'))

@app.route('/profile')
def get_profile():
    if session['role'] == 'organizer':
        conn = connect_db()
        c = conn.cursor()
        c.execute("""SELECT COUNT(e.eID) AS TotalEventsCreated
                    FROM Users u JOIN Events e ON u.uName = e.creatorName WHERE 
                    u.sRole = 'organizer' and e.creatorName=%s GROUP BY u.uName;""", (session['username'],))
        total_events = 0
        res = c.fetchone()
        if res is not None:
            total_events = res[0]
        c.execute("""SELECT SUM(e.tIncome) AS TotalIncome
                    FROM Users u JOIN Events e ON u.uName = e.creatorName
                    WHERE u.sRole = 'organizer' and e.creatorName=%s GROUP BY u.uName;""", (session['username'],))
        total_income = 0
        res = c.fetchone()
        if res is not None:
            total_income = res[0]

        #other info:
        c.execute("SELECT eid, ename, description, dateandtime, elocation, tprice, maxticket FROM events where creatorName=%s GROUP BY eid;", (session['username'],))
        rows = c.fetchall()
        processed_rows = []
        for row in rows:
            dateandtime = row[3]
            date = dateandtime.date()
            time = dateandtime.time()
            processed_rows.append((row[0], row[1], row[2], date, time, row[4], row[5], row[6]))
        #done
        conn.commit()
        conn.close()
        return render_template('organizerProfile.html', total_events=total_events, total_income=total_income, events=processed_rows)
    elif session['role'] == 'customer':
        return redirect(url_for('customerProfile'))


@app.route('/updateEvent', methods=['POST'])
def update_event():
    event_id = request.form.get('event_id')

    event_name = request.form.get('event_name')
    description = request.form.get('description')
    price = request.form.get('price')
    maxTicket = request.form.get('maxTicket')

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Events
        SET eName = %s, description = %s, tPrice = %s, maxticket = %s
        WHERE eID = %s
    """, (event_name, description, price, maxTicket, event_id))

    conn.commit()
    conn.close()
    return render_template('eventUpdated.html', event_id=event_id)


@app.route('/deleteEvent', methods=['POST'])
def delete_event():
    event_id = request.form.get('event_id')
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Events WHERE eid = %s", (event_id,))
    conn.commit()
    conn.close()
    return render_template('eventUpdated.html', event_id=event_id)


@app.route('/exploreEvents')
def exploreEvents():
    if 'role' in session:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT ename,dateandtime,elocation,description,tprice,eid FROM Events ORDER BY dateandtime DESC")
        rows = c.fetchall()
        processed_rows = []
        for row in rows:
            dateandtime = row[1]
            date = dateandtime.date()
            time = dateandtime.time()
            processed_rows.append((row[0], date, time, row[2], row[3], row[4], row[5]))
        conn.close()
        msg = ''
        if session['role'] == 'customer':
            msg = request.args.get('msg')
            return render_template('events.html', records=processed_rows, role=session['role'],msg=msg)
        elif session['role'] == 'organizer':
            msg = "You are an organizer, you should create a user account to be able to book an event!"
            return render_template('events.html', records=processed_rows, msg=msg)
    msg = "You are not authorized to view this page! Please login first."
    return render_template('events.html', msg=msg)



@app.route('/')
def home():
    if "username" in session:
        return render_template('home.html', username=session['username'], role=session['role'])
    return render_template('home.html')


@app.route('/login', methods=['get', 'POST'])
def login():
    if request.method == 'POST' and 'username' not in session:
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = connect_db()
        cur = conn.cursor()
        # Check user's credentials and role in the users table
        cur.execute("SELECT fname, lname FROM users WHERE uname = %s AND upassword = %s AND srole = %s",
                    (username, password, role))
        user = cur.fetchone()
        conn.close()

        if not user:
            conn.close()
            return render_template('login.html', msg="Invalid username, password, or role")

        role_check = False
        # Check the user's presence in the respective table based on their role
        if role == 'organizer':
            role_check = is_user_organizer(username)
        elif role == 'customer':
            role_check = is_user_customer(username)

        if not role_check:
            return render_template('login.html', msg="Role-specific data not found")

        # Store username and role in session if login is successful
        session['username'] = username
        session['role'] = role
        return render_template('home.html', username=username, role=role)

    elif 'username' not in session:
        return render_template('login.html')
    else:
        return render_template('home.html', username=session['username'], role=session['role'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))


@app.route('/register', methods=['get', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        # print(session['username'])
        conn = connect_db()
        c = conn.cursor()
        c.execute("INSERT INTO Users (uName, email, fName, lName, sRole, pNumber, uPassword, gender, ticketCount)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (username, email, firstName, lastName, role, phone, password, gender, 0))
        if role == 'customer':
            c.execute("INSERT INTO customers (cusername) VALUES (%s)", (username,),)
            conn.commit()
        conn.commit()
        conn.close()
        session['username'] = username

        if role == 'organizer':
            return redirect(url_for('organizer'))
        return redirect(url_for('register_success'))

    conn = connect_db()

    c = conn.cursor()
    c.execute("SELECT uName,email FROM Users")
    namesAndEmail = c.fetchall()
    print(namesAndEmail)
    names = [name[0] for name in namesAndEmail]
    emails = [e[1] for e in namesAndEmail]
    print(names)
    print(emails)
    conn.close()
    return render_template('register.html', unames=names, emails=emails)


@app.route('/register_success')
def register_success():
    return render_template('register_success.html')


@app.route('/organizer',methods=['GET', 'POST'])
def organizer():
    if request.method == "POST":
        tax = request.form.get('tax-number')
        conn = connect_db()
        c = conn.cursor()
        c.execute("INSERT INTO organizer(ousername,tnumber) VALUES (%s,%s)", (session['username'], tax))
        conn.commit()
        conn.close()
        return redirect(url_for('register_success'))
    return render_template('organizertax.html')


@app.route('/createEvent',methods=['GET', 'POST'])
def createEvent():
    if request.method == "POST":
        name = request.form.get('event-name')
        ticket = request.form.get('max-tickets')
        date = request.form.get('event-date-time')
        type = request.form.get('event-type')
        location = request.form.get('event-location')
        description = request.form.get('event-description')
        price = request.form.get('ticket-price')
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT eID FROM Events ORDER BY eid DESC LIMIT 1")
        eid = c.fetchone()[0]
        c.execute("INSERT INTO events(eid,ename,maxticket,dateandtime,etype,elocation,description,tprice,tincome,creatorname) "
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (eid+1, name, ticket, date, type, location, description,price, 0, session["username"]))
        conn.commit()
        conn.close()
        return redirect(url_for('exploreEvents'))
    return render_template('createEvents.html')


if __name__ == '__main__':
    app.run(debug=True)
