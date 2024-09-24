from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, DateField, IntegerField
from wtforms.validators import ValidationError, DataRequired
import re
from auth.forms import validate_phone, character_check


'''Validate_postcode uses a reg-expression to make sure it is a valid UK Postcode'''


def validate_postcode(form, field):
    p = re.compile(r'^[A-Z]{1,2}[0-9][0-9A-Z]? [0-9][A-Z]{2}$')
    if not p.match(field.data) and (field.data != ""):
        raise ValidationError("Enter a valid UK postcode.")
        # Raises this error message when regex is not matched.


'''All fields excluding date and select fields in the following forms are validated by DataRequired to ensure
 they are filled in.'''


'''Address form contains the fields needed for the Family() view function within account/views.
Dropdown box 'service' lets the user choose whether to manually enter postcode or use a location service.
postcode uses the above function to validate.
Dropdown box 'facility' lets the user choose between hospitals, Gps and pharmacies to search for.'''


class AddressForm(FlaskForm):
    service = SelectField('Choose an option', choices=['Enter Address', 'Enable Location'], default=['Enter Address'])
    # dropdown box for the user to select manual entry or to enable location.
    postcode = StringField('Postcode', validators=[validate_postcode])
    # postcode is validated by the validate_postcode function.
    facility = SelectField('Choose an option', choices=['Hospitals', 'GPs', 'Pharmacies'], default=['Hospitals'])
    # dropdown box to select what facility to search for
    submit = SubmitField()


'''Prescription form contains the fields needed for the add_prescription() view function within account/views.
This form uses string, date and integer fields to record the name, start date, end date, expiration date and quantity.
Dropdown box 'repeat' allows the choice of yes or no to indicate repeat prescription.'''


class PrescriptionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    startDate = DateField('Start Date', validators=[DataRequired()])
    endDate = DateField('End Date', validators=[DataRequired()])
    expDate = DateField('End Date', validators=[DataRequired()])
    repeat = SelectField('Yes', choices=['Yes', 'No'], default=['Yes'])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add Prescription')


'''Appointment form contains the fields needed for the add_appointment() view function within account/views.
All that is needed in this form is the appointment title and the date of said appointment. '''


class AppointmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Add Appointment')


'''Edit form contains the fields needed for the edit_details() view function within account/views.
This form takes in new user details to update the old ones. 
phone is validated by the validate_phone() function from auth/forms.
First and last name validated by character_check from auth/forms.'''


class EditForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), character_check])
    lastName = StringField('Surname', validators=[DataRequired(), character_check])
    # Uses character_check from auth/forms to forbid characters
    age = IntegerField('Age', validators=[DataRequired()])
    phone = StringField(validators=[DataRequired(), validate_phone])  # validate_phone is called from auth/forms
    submit = SubmitField('Update Details')


class AccountSearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
