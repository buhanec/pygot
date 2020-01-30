"""Server for hosting the game."""

from __future__ import annotations

from http import HTTPStatus
from typing import Optional

from flask import Flask, Response, jsonify

from pygot.models import House
from pygot.models.serialisation import JSON, JSONType

app = Flask(__name__)

__all__ = tuple()


class APIException(Exception):
    """Generic API exception."""

    def __init__(self,
                 reason: str,
                 code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
                 extra_info: Optional[JSONType] = None) -> None:
        super().__init__(f'{code} - {reason}')
        self.reason = reason
        self.code = code
        self.extra_info = extra_info

    def to_json(self) -> JSON:
        """Generate JSON structure"""
        return {
            'code': self.code.value,
            'message': self.code.phrase,
            'reason': self.reason,
            'extra': self.extra_info,
        }


@app.route('/')
def index():
    """Project index."""
    return jsonify({
        '/house/<house_name>': 'Get house information'
    })


@app.route('/house/<house_name>')
def get_house(house_name: str):
    """
    Get house information.

    :param house_name: House name
    :return: House information
    """
    try:
        house = House[house_name.upper()]
    except KeyError as e:
        raise APIException(reason='House not found',
                           code=HTTPStatus.NOT_FOUND,
                           extra_info={'houseName': house_name}) from e
    return jsonify(house.info.to_json())


@app.errorhandler(APIException)
def handle_invalid_usage(error: APIException):
    """Invalid usage request handler."""
    response: Response = jsonify(error.to_json())
    response.status_code = error.code
    return response


if __name__ == '__main__':
    app.run(debug=True)
