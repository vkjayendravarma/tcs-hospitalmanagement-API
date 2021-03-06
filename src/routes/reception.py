from src import app, db, Config
from flask import request
from src.models import patientModel
from flask_mongoengine import mongoengine
from flask_api import status
from markupsafe import escape


from src.routes import shared
from src.routes.security import authorization


@app.route('/reception/patients/new', methods=['POST'])
@authorization
def newPatient(role):
    L2Auth = role in ["HMAD", "HMFD"]
    if not L2Auth:
        return {
            "success": False,
            "message": "Unauthorized"
        },status.HTTP_401_UNAUTHORIZED
    req = request.get_json()
    try:
        ssnid = req['ssnid']
        name = req['name']
        age = int(req['age'])
        address = req['address']
        dateOfJoining = req['dateOfJoining']
        roomType = req['roomType']
        city = req['city']
        state = req['state']
    except KeyError as e:
        return {
            "success":False,
            "message": "missing"
        },status.HTTP_400_BAD_REQUEST

    config = patientModel.config.objects().first()
    patientId = config.patientId +1
    config.update(patientId=patientId)
    try:
        patient = patientModel.Patient(ssnid=ssnid, patientId=patientId, name=name, age=age, address=address, dateOfJoining=dateOfJoining, roomType=roomType, city=city, state=state).save()
        patientid = str(patient['patientId'])
    except mongoengine.errors.NotUniqueError as e:
        return {'success': False, 'message': "SSN ID exists"},status.HTTP_406_NOT_ACCEPTABLE
    except mongoengine.errors.ValidationError as e:
        return {'success': False, 'message': "Missing field"},status.HTTP_400_BAD_REQUEST

    return {
        'success': True,
        'res': {
            'message': 'patient created',
            'patientId': patientid
        }
    },status.HTTP_200_OK

# return all patients


@app.route('/reception/patients', methods=['GET'])
@authorization
def allPatients(role):    
    L2Auth = role in ["HMAD", "HMFD"]
    if L2Auth:
        data = patientModel.Patient.objects()
        return {
                'success': True,
                'res': data
        }, status.HTTP_200_OK
    return {
        'success': False,
        'message': "Unauthorised route"
    },status.HTTP_401_UNAUTHORIZED

# GET return patient data
# POST update patient data
# PUT change status to Discharged
# DELETE delete patient


@app.route('/reception/patients/individual/<patientId>', methods=['GET', 'PUT', 'POST', 'DELETE'])
@authorization
def Patient(role,patientId):
    L2Auth = role in ["HMAD", "HMFD"]
    if not L2Auth:
        return {
            "success": False,
            "message": "Unauthorized"
        },status.HTTP_401_UNAUTHORIZED
    
    if request.method == 'GET':
        data = patientModel.Patient.objects(patientId=patientId).first()
        if(data):
            pharmacyInvoices = shared.getPharmacyInvoices(data.pharmacy)
            data['pharmacy'] = pharmacyInvoices
            labInvoices = shared.getLabInvoices(data.diagnostics)
            data['diagnostics'] = labInvoices
            return {
                'success': True,
                'res': data
            },status.HTTP_200_OK
        return {
            'success': False,
            'message': 'Patient not found'
        },status.HTTP_404_NOT_FOUND

    if request.method == 'POST':
        data = patientModel.Patient.objects(patientId=patientId)
        if(data):
            req = request.get_json()                   
            try:
                ssnid = req['ssnid']
                name = req['name']
                age = int(req['age'])
                address = req['address']
                dateOfJoining = req['dateOfJoining']
                roomType = req['roomType']
                city = req['city']
                state = req['state']               

            except KeyError:
                return {"success": False, "message": "se"}
            data.update(ssnid=ssnid, patientId=patientId, name=name, age=age, address=address, dateOfJoining=dateOfJoining, roomType=roomType, city=city, state=state)
            return {
                'success': True,
                'message': 'updated'
            },status.HTTP_200_OK
        else:
            return {
                'success': False,
                'message': 'Patient not found'
            },status.HTTP_404_NOT_FOUND

        

    if(request.method == 'PUT'):
        data = patientModel.Patient.objects(patientId=patientId)
        if(data):
            data.update(status='Discharged')

            return {
                'success': True,
                'message': 'patient discharged'
            },status.HTTP_200_OK
        else:
            return {
                'success': False,
                'message': 'Patient not found'
            },status.HTTP_404_NOT_FOUND

    if(request.method == 'DELETE'):
        data = patientModel.Patient.objects(patientId=patientId)

        if(data):
            data.delete()

            return {
                'success': True,
                'message': 'deleted'
            },status.HTTP_200_OK
        else:
            return {
                'success': False,
                'message': 'Patient not found'
            },status.HTTP_404_NOT_FOUND
