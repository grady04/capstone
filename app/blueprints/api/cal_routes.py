from  __future__  import print_function
from flask import render_template
from flask_login import login_required, current_user
from app.models import Task, User, Comments
import datetime
import pickle
import os.path
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from . import bp as api

 # for testing
@api.route('/test', methods = ['GET'])
@login_required
def test():
    my_students = ['Scarlett', 'Aydee', 'Patrick', 'Armani', 'Jalen']
    return render_template('students.html.j2', students = my_students)

@api.route("/calendar")
@login_required
def calendar():
    creds =  None #credentials.json
    SCOPES  = ['https://www.googleapis.com/auth/calendar.readonly']
    if os.path.exists('token.pickle'):
        with  open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() +  'Z' 
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='grady.dickerson04@gmail.com', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime', ).execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    event_list = [event["summary"] for event in events]
    
    return  render_template("calendar.html.j2", events=event_list)