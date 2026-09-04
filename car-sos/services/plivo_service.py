from urllib.parse import quote
from plivo import RestClient

class PlivoService:
    def __init__(self, auth_id, auth_token, from_number):
        if auth_id and auth_token:
            self.client = RestClient(auth_id=auth_id, auth_token=auth_token)
        else:
            self.client = None
        self.from_number = from_number

    def is_configured(self):
        return self.client is not None and bool(self.from_number)

    def build_answer_url(self, vehicle_info, location_url, site_url):
        return (
            f'{site_url}/plivo/answer-sos'
            f'?make={quote(vehicle_info["make"])}'
            f'&model={quote(vehicle_info["model"])}'
            f'&year={quote(str(vehicle_info["year"]))}'
            f'&plate={quote(vehicle_info["plate"])}'
            f'&color={quote(vehicle_info.get("color","unknown"))}'
            f'&location={quote(location_url)}'
        )

    def make_sos_call(self, to_number, vehicle_info, location_url, site_url):
        if not self.is_configured():
            return {'status': 'simulated', 'to': to_number}

        answer_url = self.build_answer_url(vehicle_info, location_url, site_url)

        try:
            call = self.client.calls.create(
                from_=self.from_number,
                to=to_number,
                answer_url=answer_url,
                answer_method='GET'
            )
            return {'status': 'initiated', 'sid': call.get('request_uuid', '')}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def make_sos_call_with_timeout(self, to_number, vehicle_info, location_url,
                                   site_url, timeout_seconds=30,
                                   hangup_url=None):
        """Place an SOS call that rings for up to timeout_seconds.

        Returns {'status': 'initiated', ...} if the call was placed. The
        answer status ('answered' / 'no_answer') is delivered asynchronously to
        `hangup_url` (and optionally read back via the polling endpoint).
        In demo mode (not configured) it returns a simulated result.
        """
        answer_url = self.build_answer_url(vehicle_info, location_url, site_url)

        if not self.is_configured():
            return {
                'status': 'simulated',
                'to': to_number,
                'timeout_seconds': timeout_seconds
            }

        try:
            call = self.client.calls.create(
                from_=self.from_number,
                to=to_number,
                answer_url=answer_url,
                answer_method='GET',
                ring_timeout=int(timeout_seconds),
                hangup_on_ring=True,
                hangup_url=hangup_url,
                hangup_method='GET'
            )
            return {'status': 'initiated', 'sid': call.get('request_uuid', '')}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def send_location_sms(self, to_number, vehicle_info, location_url):
        if not self.is_configured():
            return {'status': 'failed', 'error': 'Plivo not configured'}

        map_short = f"maps.google.com/?q={location_url.split('=')[-1]}" if '=' in location_url else location_url
        body = (
            f"SOS ALERT: {vehicle_info['make']} {vehicle_info['model']} "
            f"({vehicle_info['plate']}) needs emergency assistance!\n"
            f"Location: {map_short}\n"
            f"{location_url}"
        )

        try:
            msg = self.client.messages.create(
                src=self.from_number,
                dst=to_number,
                text=body
            )
            return {'status': 'sent', 'sid': msg.get('message_uuid', '')}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
