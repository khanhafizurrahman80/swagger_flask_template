from http import HTTPStatus


class Response:

    def __init__(self, status: int):
        self.status = HTTPStatus(status)
        self.code = status
        self.success = {}
        self.error = {}

    def wrap(self, response_body):
        if self.status.value < 400:
            self.success = response_body
            self.error = None
        else:
            self.success = None
            self.error = response_body
        return {'status': self.status.phrase, 'code': self.status, 'success': self.success, 'error': self.error}
