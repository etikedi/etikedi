from flask_restful.reqparse import RequestParser


def convert_dataclass_to_parser(dataclass) -> RequestParser:
    """ Returns a parser that accepts the fields defined at the given dataset in the request body. """
    parser = RequestParser()
    for field in dataclass.__dataclass_fields__.values():
        parser.add_argument(
            field.name.lower(),
            type=field.type,
            location='form',
            required=True
        )
    return parser
