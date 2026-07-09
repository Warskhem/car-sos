from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

class TwilioService:
    def __init__(self, account_sid, auth_token, from_number):
        self.client = Client(account_sid, auth_token) if account_sid and auth_token else None
        self.from_number = from_number

    def is_configured(self):
        return self.client is not None and bool(self.from_number)

    def make_sos_call(self, to_number, vehicle_info, location_url, site_url):
        if not self.is_configured():
            return {'status': 'failed', 'error': 'Twilio not configured'}

        twiml = self._build_sos_twiml(vehicle_info, location_url, site_url)

        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                twiml=str(twiml),
                timeout=30
            )
            return {'status': 'initiated', 'sid': call.sid}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def send_location_sms(self, to_number, vehicle_info, location_url):
        if not self.is_configured():
            return {'status': 'failed', 'error': 'Twilio not configured'}

        map_short = f"maps.google.com/?q={location_url.split('=')[-1]}" if '=' in location_url else location_url
        body = (
            f"🚨 SOS ALERT: {vehicle_info['make']} {vehicle_info['model']} "
            f"({vehicle_info['plate']}) needs emergency assistance!\n"
            f"📍 Location: {map_short}\n"
            f"📌 {location_url}"
        )

        try:
            msg = self.client.messages.create(
                to=to_number,
                from_=self.from_number,
                body=body
            )
            return {'status': 'sent', 'sid': msg.sid}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def _build_sos_twiml(self, vehicle_info, location_url, site_url):
        response = VoiceResponse()
        gather = Gather(num_digits=1, action=f'{site_url}/twilio/handle-input', method='POST', timeout=5)
        gather.say(
            f"EMERGENCY SOS ALERT. "
            f"Vehicle: {vehicle_info['make']} {vehicle_info['model']}, "
            f"year {vehicle_info['year']}, "
            f"plate number {vehicle_info['plate']}. "
            f"Color: {vehicle_info.get('color', 'unknown')}. "
            f"Location: {location_url}. "
            f"An accident or breakdown has been reported. "
            f"Please respond immediately. "
            f"After the beep, press any key to repeat this message.",
            voice='alice', language='en-US'
        )
        response.append(gather)
        response.play(f'{site_url}/static/beep.wav')
        response.pause(length=1)
        response.play(f'{site_url}/static/beep.wav')
        response.pause(length=1)
        response.play(f'{site_url}/static/beep.wav')
        response.redirect('')
        return response


