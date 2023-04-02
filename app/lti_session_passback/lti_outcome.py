import requests
from lti.outcome_request import OutcomeRequest, InvalidLTIConfigError
from lti.outcome_response import OutcomeResponse
from requests_oauthlib import OAuth1
from requests_oauthlib.oauth1_auth import SIGNATURE_TYPE_AUTH_HEADER


class LTIOutcomeRequest(OutcomeRequest):
    """
    Override `post_outcome_request` method of OutcomeRequest to avoid
        requests.exceptions.SSLError:
            (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate (_ssl.c:1108)')))
    """

    def post_outcome_request(self, **kwargs):
        '''
        POST an OAuth signed request to the Tool Consumer.
        '''
        if not self.has_required_attributes():
            raise InvalidLTIConfigError(
                'OutcomeRequest does not have all required attributes')

        header_oauth = OAuth1(self.consumer_key, self.consumer_secret,
                              signature_type=SIGNATURE_TYPE_AUTH_HEADER,
                              force_include_body=True, **kwargs)

        headers = {'Content-type': 'application/xml'}
        resp = requests.post(self.lis_outcome_service_url, auth=header_oauth,
                             data=self.generate_request_xml(),
                             headers=headers, verify=False)
        outcome_resp = OutcomeResponse.from_post_response(resp, resp.content)
        self.outcome_response = outcome_resp
        return self.outcome_response
