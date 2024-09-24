from flask import Blueprint, render_template, flash, request, redirect, url_for, session, request
import geocoder
from geopy.geocoders import Nominatim
from firebase_admin import db
import pyrebase
from account.data import return_person_info, fetch_notifications, fetch_documents, get_facilities, fetch_appointments, \
    search_user_in_db
from account.forms import AddressForm, AccountSearchForm
from datetime import datetime, timedelta

account_blueprint = Blueprint('account', __name__, template_folder='templates')

firebase_config = {}
firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()


@account_blueprint.route("/personal", methods=['GET', 'POST'])
def personal():
    if "user" in session:
        # POST request - personal page opened from family page so find and load up user passed in through form
        if request.method == 'POST':
            person_id = request.form.get('person_id')
            person_info = return_person_info(person_id)
            notifications = fetch_notifications([person_info])
            documents = fetch_documents(person_id)
            session['person'] = person_id
            filter_type = request.args.get('filter', 'upcoming')
            return render_template("personal.html", person=person_info, notifications=notifications,
                                   documents=documents, filter_type=filter_type)
        # GET request - personal page opened through navbar
        elif request.method == "GET":
            # if user visited page before, go back to last viewed family member saved in session
            if "person" in session:
                person_info = return_person_info(session['person'])
                notifications = fetch_notifications([person_info])
                documents = fetch_documents(session['person'])
                filter_type = request.args.get('filter', 'upcoming')
                person_info.appointments = fetch_appointments(session['person'], filter_type)
                return render_template("personal.html", person=person_info, notifications=notifications,
                                       documents=documents, filter_type=filter_type)
            # if user hasn't visited page before, loads up first family member in account
            else:
                family_list = db.reference("/Accounts/" + str(session['user']) + "/family").get()
                if family_list:
                    person_id = next(iter(family_list))
                    person_info = return_person_info(person_id)
                    notifications = fetch_notifications([person_info])
                    documents = fetch_documents(person_id)
                    session['person'] = person_id
                    filter_type = request.args.get('filter', 'upcoming')
                    person_info.appointments = fetch_appointments(session['person'], filter_type)
                    return render_template("personal.html", person=person_info, notifications=notifications,
                                           documents=documents, filter_type=filter_type)
                else:
                    flash("No family members found.")
                    return redirect(url_for('account.family'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route("/edit_details", methods=['POST'])
def edit_details():
    if "user" in session:
        if all(field in request.form for field in  # if all fields aren't empty
               ['firstname', 'surname', 'birthday']):
            firstname = request.form.get('firstname')
            surname = request.form.get('surname')
            birthday = request.form.get('birthday')
            old = return_person_info(session['person'])
            docs = fetch_documents(old.person_id)

            # Deletes information saved under old name in the database
            db.reference("/Appointments/" + session['user'] + "/" + old.person_id).delete()
            db.reference("/Prescriptions/" + session['user'] + "/" + old.person_id).delete()
            db.reference("/Documents/" + session['user'] + "/" + old.person_id).delete()
            db.reference("/Accounts/" + session['user'] + "/family/" + old.person_id).delete()

            # Uploads information under the new name in the database
            new_ref = db.reference("/Appointments/" + session['user'] + "/" + firstname + "_" + surname)
            for app in old.appointments:
                new_ref.push({
                    'title': app.title,
                    'location': app.location,
                    'date': app.date
                })
            new_ref = db.reference("/Prescriptions/" + session['user'] + "/" + firstname + "_" + surname)
            for pres in old.prescriptions:
                new_ref.push({
                    'name': pres.name,
                    'start_date': pres.start_date,
                    'end_date': pres.end_date,
                    'expiration_date': pres.expiration_date,
                    'repeat': pres.repeat,
                    'dosage': pres.dosage
                })
            new_ref = db.reference("/Documents/" + session['user'] + "/" + firstname + "_" + surname)
            for doc in docs:
                new_ref.push({
                    'filename': doc.filename,
                    'url': doc.url
                })
            new_ref = db.reference("/Accounts/" + session['user'] + "/family/" + firstname + "_" + surname)
            new_ref.set({
                'firstname': firstname,
                'surname': surname,
                'birthday': birthday
            })
            session['person'] = firstname + "_" + surname
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route("/upload_document", methods=['POST'])
def upload_document():
    if "user" and "person" in session:
        # Uploads document to storage and adds URL to the database
        file = request.files['document']
        storage.child("docs/" + file.filename).put(file)
        link = storage.child("docs/" + file.filename).get_url(None)
        db.reference("/Documents/" + str(session['user']) + "/" + session['person']).push({
            'filename': file.filename,
            'url': link
        })
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route("/delete_document", methods=['POST'])
def delete_document():
    if "user" and "person" in session:
        # Deletes document URL in the database
        # Does not delete actual file in storage - future backup implementation
        doc_id = request.form.get('doc_id')
        db.reference("/Documents/" + session['user'] + "/" + session['person'] + "/" + doc_id).delete()
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


# Gets current user through form, then adds prescription to said user, then re-renders personal page
@account_blueprint.route('/add_prescription', methods=["POST"])
def add_prescription():
    if "user" and "person" in session:
        if all(field in request.form for field in  # if all fields aren't empty
               ['name', 'start_date', 'end_date', 'expiration_date', 'repeat', 'dosage']):
            name = request.form.get('name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            expiration_date = request.form.get('expiration_date')
            repeat = request.form.get('repeat')
            dosage = request.form.get('dosage')
            # Adds prescription info to the database with a unique ID
            ref = db.reference("/Prescriptions/" + session['user'] + "/" + session['person'])
            ref.push({
                'name': name,
                'start_date': start_date,
                'end_date': end_date,
                'expiration_date': expiration_date,
                'repeat': repeat,
                'dosage': dosage
            })
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/delete_prescription', methods=['POST'])
def delete_prescription():
    if "user" and "person" in session:
        # Deletes prescription node in the database
        pres_id = request.form.get('pres_id')
        db.reference("/Prescriptions/" + session['user'] + "/" + session['person'] + "/" + pres_id).delete()
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/add_appointment', methods=['POST'])
def add_appointment():
    if "user" and "person" in session:
        if all(field in request.form for field in  # if all fields aren't empty
               ['title', 'location', 'date']):
            title = request.form.get('title')
            location = request.form.get('location')
            date = request.form.get('date')
            # Adds appointment info to the database with a unique ID
            ref = db.reference("/Appointments/" + session['user'] + "/" + session['person'])
            ref.push({
                'title': title,
                'location': location,
                'date': date
            })
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/delete_appointment', methods=['POST'])
def delete_appointment():
    if "user" and "person" in session:
        app_id = request.form.get('app_id')
        db.reference("/Appointments/" + session['user'] + "/" + session['person'] + "/" + app_id).delete()
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/family', methods=['GET', 'POST'])
def family():
    if "user" in session:
        form = AddressForm()
        results = []

        # Generates list of family members under account name
        family_list = []
        family_ref = db.reference("/Accounts/" + str(session['user']) + "/family").get()
        try:
            for person in family_ref:
                family_list.append(return_person_info(person))
        except TypeError:
            pass
        notifications = fetch_notifications(family_list)

        # Function either uses IP or given Postcode to locate nearest facilities
        if form.validate_on_submit():
            if form.service.data == 'Enable Location':
                g = geocoder.ip('me')
                results = get_facilities(g.latlng[0], g.latlng[1], form.facility.data)
            else:
                if form.postcode.data:
                    locator = Nominatim(user_agent="Medical_Facility_Locator")
                    location = locator.geocode(form.postcode.data)
                    results = get_facilities(location.latitude, location.longitude, form.facility.data)
                else:
                    flash("Please input postcode")
        return render_template('family.html', form=form, results=results, family_list=family_list,
                               notifications=notifications)
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/add_user', methods=['POST'])
def add_user():
    if "user" in session:
        if all(field in request.form for field in  # if all fields aren't empty
               ['firstname', 'surname', 'birthday']):
            firstname = request.form.get('firstname')
            surname = request.form.get('surname')
            birthday = request.form.get('birthday')
            ref = db.reference("/Accounts/" + session['user'] + "/family/" + firstname + "_" + surname)
            ref.set({
                'firstname': firstname,
                'surname': surname,
                'birthday': birthday
            })
            flash("User added successfully")
        return redirect(url_for('account.family'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/delete_user', methods=['POST'])
def delete_user():
    if "user" in session:
        person = str(request.form.get('person_id'))
        db.reference("/Accounts/" + session['user'] + "/family/" + person).delete()
        return redirect(url_for('account.family'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    if "user" in session:
        user_id = session['user']
        # Fetch the user's information from the database
        user_ref = db.reference("/Accounts/" + str(user_id))
        user_data = user_ref.get()

        if not user_data:
            return render_template("errors/genericErrorNoInfo.html")

        # Calculate age
        from datetime import datetime
        birthday = datetime.strptime(user_data.get('birthday', '01/01/1900'), '%d/%m/%Y')
        age = datetime.now().year - birthday.year - ((datetime.now().month, datetime.now().day) < (birthday.month, birthday.day))

        user_info = {
            "firstname": user_data.get('firstname', 'N/A'),
            "surname": user_data.get('surname', 'N/A'),
            "email": user_data.get('email', 'N/A'),
            "phone": user_data.get('phone', 'N/A'),
            "birthday": user_data.get('birthday', 'N/A'),
            "age": age,
            "user_id": user_id
        }

        return render_template('settings.html', userInfo=user_info)
    else:
        return render_template('errors/page401.html')




@account_blueprint.route('/reduce_dosage', methods=['POST'])
def reduce_dosage():
    if "user" and "person" in session:
        pres_id = request.form.get('pres_id')
        user = session['user']
        person_id = session['person']

        # Fetch the current prescription data
        pres_ref = db.reference(f"/Prescriptions/{user}/{person_id}/{pres_id}")
        prescription = pres_ref.get()
        current_dosage = int(prescription['dosage'])

        # Reduce the dosage by 1
        new_dosage = max(0, current_dosage - 1)  # Ensure dosage doesn't go negative
        pres_ref.update({'dosage': new_dosage})

        flash(f'Dosage reduced by 1. New dosage: {new_dosage}')
        return redirect(url_for('account.personal'))
    else:
        return redirect(url_for('auth.login'))


@account_blueprint.route('/admin', methods=['GET', 'POST'])
def adminPage():
    form = AccountSearchForm()
    if "user" in session:
        user_id = session['user']
        # Fetch the user's information from the database
        user_ref = db.reference("/Accounts/" + str(user_id))
        user_data = user_ref.get()

        if not user_data:
            return render_template("errors/genericErrorNoInfo.html")

        # Check if the user has the admin role
        if user_data.get('role') != 'admin':
            return render_template('errors/page401.html')

        birthday = datetime.strptime(user_data.get('birthday', '01/01/1900'), '%d/%m/%Y')
        age = datetime.now().year - birthday.year - (
            (datetime.now().month, datetime.now().day) < (birthday.month, birthday.day))

        user_info = {
            "firstname": user_data.get('firstname', 'N/A'),
            "surname": user_data.get('surname', 'N/A'),
            "email": user_data.get('email', 'N/A'),
            "phone": user_data.get('phone', 'N/A'),
            "birthday": user_data.get('birthday', 'N/A'),
            "age": age,
            "user_id": user_id
        }

        search_results = None
        if form.validate_on_submit():
            search_query = form.search.data
            search_results = search_user_in_db(search_query)

        # Read the most recent 10 lines from log.txt
        try:
            with open('log.txt', 'r') as file:
                lines = file.readlines()
                recent_lines = lines[-10:]
        except FileNotFoundError:
            recent_lines = ["log.txt not found."]

        return render_template("admin.html", userInfo=user_info, log_lines=recent_lines, form=form, search_results=search_results)
    else:
        return render_template("errors/page401.html")


