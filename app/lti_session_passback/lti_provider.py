from lti.tool_provider import ToolProvider

from .lti_outcome import LTIOutcomeRequest


class LTIProvider(ToolProvider):
    """
    Класс для переопределения метода new_request для обхода проверки https в модуле requests
    """

    def new_request(self, defaults):
        opts = dict(defaults)
        opts.update({
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret,
            'lis_outcome_service_url': self.lis_outcome_service_url,
            'lis_result_sourcedid': self.lis_result_sourcedid
        })
        self.outcome_requests.append(LTIOutcomeRequest(opts=opts))
        self._last_outcome_request = self.outcome_requests[-1]
        return self._last_outcome_request
