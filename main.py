from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
import re


app = Flask(__name__)
forms_db = TinyDB('forms_db.json')
def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    phone = phone.replace(" ", "")
    pattern = r'^\+7\d{10}$'
    return bool(re.match(pattern, phone))


def validate_date(date):
    date_formats = [
        r'^\d{2}\.\d{2}.\d{4}$',
        r'^\d{4}-\d{2}-\d{2}$'
    ]
    return any(bool(re.match(pattern, date)) for pattern in date_formats)


def validate_text(text):
    pattern = r'^[a-zA-Z0-9\s]+$'
    return bool(re.match(pattern, text))


def find_matching_form(fields, forms):
    for form in forms:
        if set(fields.keys()).issuperset(set(form['fields'])):
            return form['name']
    return None

def infer_field_types(fields):
    field_types = {}
    for field, value in fields.items():
        if "@" in value and validate_email(value):
            field_types[field] = "email"
        elif value.startswith("+7") and validate_phone(value):
            field_types[field] = "phone"
        elif validate_date(value):
            field_types[field] = "date"
        elif validate_text(value):
            field_types[field] = "text"
        else:
            field_types[field] = "error: invalid value"
    return field_types



def process_request(request_data):
    fields = {key: value for key, value in request_data.items()}

    forms = forms_db.all()

    matching_form = find_matching_form(fields, forms)

    if matching_form:
        return {"form_name": matching_form}
    else:
        field_types = infer_field_types(fields)
        return {"inferred_field_types": field_types}



@app.route('/', methods=['GET', 'POST'])
def handle_request():
    request_data = request.form.to_dict()
    result = process_request(request_data)

    if not result:
        return jsonify({"inferred_field_types": result})
    else:
        return jsonify({"form_name": result})

if __name__ == "__main__":
    app.run(port=8000, debug=True)