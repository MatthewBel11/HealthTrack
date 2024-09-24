from flask import session
from firebase_admin import db
from datetime import datetime, timedelta
import requests


class Person:
    def __init__(self, person_id, firstname, surname, birthday):
        self.person_id = person_id
        self.firstname = firstname
        self.surname = surname
        self.birthday = birthday
        self.prescriptions = []
        self.appointments = []

    def date_format(self, original_date):
        date = datetime.strptime(original_date, '%Y-%m-%d')
        return date.strftime('%d-%m-%Y')


class Prescription:
    def __init__(self, pres_id, name, start_date, end_date, expiration_date, repeat, dosage):
        self.pres_id = pres_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.expiration_date = expiration_date
        self.repeat = repeat
        self.dosage = dosage

    def date_format(self, original_date):
        date = datetime.strptime(original_date, '%Y-%m-%d')
        return date.strftime('%d-%m-%Y')


class Notification:
    def __init__(self, person, date, comment):
        self.person = person
        self.date = date
        self.comment = comment

    def date_format(self, original_date):
        date = datetime.strptime(original_date, '%Y-%m-%d')
        return date.strftime('%d-%m-%Y')


class Appointment:
    def __init__(self, app_id, title, location, date):
        self.app_id = app_id
        self.title = title
        self.location = location
        self.date = date

    def date_format(self, original_date):
        date = datetime.strptime(original_date, '%Y-%m-%d')
        return date.strftime('%d-%m-%Y')


class Document:
    def __init__(self, doc_id, filename, url):
        self.doc_id = doc_id
        self.filename = filename
        self.url = url


def return_person_info(person_id):
    person = db.reference("/Accounts/" + str(session['user']) + "/family/" + person_id).get()
    person_info = Person(
        person_id=person_id,
        firstname=person["firstname"],
        surname=person["surname"],
        birthday=person["birthday"],
    )
    # Fetches all prescriptions and appointments related to a specific family member
    # Document are not fetched as they are not required unless on personal page
    person_info.prescriptions = fetch_prescriptions(person_id)
    person_info.appointments = fetch_appointments(person_id)
    return person_info


def fetch_appointments(person_id, filter_type="upcoming"):
    appointments = []
    appointment_list = db.reference("/Appointments/" + str(session['user']) + "/" + str(person_id)).get()
    now = datetime.now()

    try:
        for app in appointment_list:
            appointment = Appointment(
                app_id=app,
                title=appointment_list[app]["title"],
                location=appointment_list[app]["location"],
                date=appointment_list[app]["date"]
            )
            app_date = datetime.strptime(appointment.date, '%Y-%m-%d')
            if filter_type == "past" and app_date < now:
                appointments.append(appointment)
            elif filter_type == "upcoming" and app_date >= now:
                appointments.append(appointment)
            elif filter_type == "all":
                appointments.append(appointment)
    except TypeError:
        pass

    return appointments


def fetch_prescriptions(person_id):
    # Generates list of prescription objects using info in the database
    prescriptions = []
    prescription_list = db.reference("/Prescriptions/" + str(session['user']) + "/" + str(person_id)).get()
    try:
        for pres in prescription_list:
            prescriptions.append(Prescription(
                pres_id=pres,
                name=prescription_list[pres]["name"],
                start_date=prescription_list[pres]["start_date"],
                end_date=prescription_list[pres]["end_date"],
                expiration_date=prescription_list[pres]["expiration_date"],
                repeat=prescription_list[pres]["repeat"],
                dosage=prescription_list[pres]["dosage"]
            ))
    except TypeError:
        pass
    return prescriptions


def fetch_documents(person_id):
    # Generates list of document objects using info in the database
    documents = []
    doc_list = db.reference("/Documents/" + str(session['user']) + "/" + person_id).get()
    try:
        for doc in doc_list:
            documents.append(Document(
                doc_id=doc,
                filename=doc_list[doc]['filename'],
                url=doc_list[doc]['url']
            ))
    except TypeError:
        pass
    return documents


def fetch_notifications(fetch_for):
    today = datetime.today()
    next_week = today + timedelta(days=7)
    notifications = []
    for person in fetch_for:
        # Generate prescription notifications
        for pres in person.prescriptions:
            end_date = datetime.strptime(pres.end_date, '%Y-%m-%d')
            exp_date = datetime.strptime(pres.expiration_date, '%Y-%m-%d')
            if today <= end_date <= next_week:
                notifications.append(Notification(
                    person=person.firstname,
                    date=(end_date - today + timedelta(days=1)).days,
                    # Calculates how many days until prescription ends
                    comment=f"Prescription '{pres.name}' is ending on {datetime.strftime(end_date, '%d-%m-%y')}."
                ))
            if today <= exp_date <= next_week:
                notifications.append(Notification(
                    person=person.firstname,
                    date=(exp_date - today + timedelta(days=1)).days,
                    # Calculates how many days until prescription expires
                    comment=f"Prescription '{pres.name}' is expiring on {datetime.strftime(exp_date, '%d-%m-%y')}."
                ))
        # Generate appointment notifications
        for app in person.appointments:
            date = datetime.strptime(app.date, '%Y-%m-%d')
            if today <= date <= next_week:
                notifications.append(Notification(
                    person=person.firstname,
                    date=(date - today + timedelta(days=1)).days,
                    # Calculates how many days until appointment
                    comment=f"Appointment '{app.title}' is on {datetime.strftime(date, '%d-%m-%y')}."
                ))
    notifications.sort(key=lambda x: x.date)  # Sorts notifs in ascending order of days until
    return notifications


def get_facilities(lat, lon, facility):
    # Sends HTTP request to HERE Discover API to fetch nearest facilities
    results = []
    URL = ("https://discover.search.hereapi.com/v1/discover?at=%s,%s&q=%s"
           "&limit=5&apikey=lJMBXZkbA_hg47W1UaVmZhYhkkt1e2rW9tL9-i5CUwA") % (
              lat, lon, facility)
    response = requests.get(URL).json()
    for item in response.get('items', []):
        results.append({
            'name': item.get('title'),
            'address': item.get('address', {}).get('label')
        })
    return results

def search_user_in_db(search_query):
    accounts_ref = db.reference("/Accounts/")
    accounts = accounts_ref.get()

    if not accounts:
        return None

    for user_id, user_data in accounts.items():
        if (user_id == search_query or
                user_data.get('email') == search_query or
                user_data.get('phone') == search_query):

            print(user_id, search_query)
            print(user_data.get('email'), search_query)
            print(user_data.get('phone'), search_query)

            return {"user_id": user_id, **user_data}

    return None