from sqlalchemy import Column, Integer, ForeignKey, Text

from .sample import Sample


class Text(Sample):
    """
    A sample containing raw text.

    Creating and saving a text will result in one entry in the `Sample` database table that
    contains the generic sample information (features, dataset) with the `type` set to `text`
    (see `Text.__mapper_args_['polymorphic_identity']`).

    Furthermore, another entry will be created in the database table `Text`. Its id will reference
    (be the same) as the id of the entry in `Sample`. Its purpose is to save all information that
    are specific to a sample of type `Text` (content).

    Examples:
        The constructor takes all keyword arguments of `Sample` in addition to `content`.

        >>> import json
        >>> from backend.models import Dataset
        >>> table = Text(
        ...     features=json.dumps({'length': 100, 'error_free': False}),
        ...     dataset=db.session.query(Dataset).first()
        ...     content = 'Lorem ipsum dolor amet sunt...'
        ... )
        >>> db.session.add(table)
        >>> db.session.commit()

        After running the example, the database will look like this:

        Database table `Sample`
        +----+--------------------------------------+------------+------+
        | id | features                             | dataset_id | type |
        +====+======================================+============+======+
        | 1  | {'length': 100, 'error_free': False} | 1          | text |
        +----+--------------------------------------+------------+------+

        Databaes table `Text`
        +----+--------------------------------+
        | id | content                        |
        +====+================================+
        | 1  | Lorem ipsum dolor amet sunt... |
        +----+--------------------------------+

        After that, querying `Sample` will return objects of of this class.

        >>> db.session.query(Sample).all()
        [Text 1 in dataset "Lorem"]
    """

    __tablename__ = "text"

    id = Column(Integer, ForeignKey("sample.id"), primary_key=True)
    content = Column(Text())

    __mapper_args__ = {"polymorphic_identity": "text"}

    def __str__(self):
        return 'Text {} in dataset "{}"'.format(self.id, self.dataset)

    def __repr__(self):
        return str(self)
