import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings

def get_google_calendar_service():
    credentials = os.path.join(settings.BASE_DIR, 'google_credentials.json')

    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

    # Retrieve the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    # Store the credentials to file
    if not os.path.exists(credentials):
        auth_code = request.GET.get('code')
        flow.fetch_token(authorization_response=request.build_absolute_uri(), code=auth_code)

        # Save the credentials
        credentials = flow.credentials.to_json()
        with open(credentials, 'w') as credentials_file:
            credentials_file.write(credentials)

    # Load the stored credentials
    flow.credentials = credentials

    # Build the Google Calendar service
    service = build('calendar', 'v3', credentials=flow.credentials)

    return service
