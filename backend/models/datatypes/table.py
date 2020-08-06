from .sample import Sample
from ...config import db


class Table(Sample):
    """
    A sample containing a raw html table.

    Creating and saving a table will result in one entry in the `Sample` database table that
    contains the generic sample information (features, dataset) with the `type` set to `table`
    (see `Table.__mapper_args_['polymorphic_identity']`).

    Furthermore, another entry will be created in the database table `Table`. Its id will reference
    (be the same) as the id of the entry in `Sample`. Its purpose is to save all information that
    are specific to a sample of type `Table` (content).

    Examples:
        The constructor takes all keyword arguments of `Sample` in addition to `content`.

        >>> import json
        >>> from backend.models import Dataset
        >>> table = Table(
        ...     features=json.dumps({'rows': 5, 'complete': True}),
        ...     dataset=db.session.query(Dataset).first()
        ...     content = '<table>[...]</table>'
        ... )
        >>> db.session.add(table)
        >>> db.session.commit()

        After running the example, the database will look like this:

        Database table `Sample`
        +----+------------------------------------+------------+-------+
        | id | features                           | dataset_id | type  |
        +====+====================================+============+=======+
        | 1  | {"length": 124, "beautiful": true} | 1          | table |
        +----+------------------------------------+------------+-------+

        Database table `Table`
        +----+----------------------+
        | id | content              |
        +====+======================+
        | 1  | <table>[...]</table> |
        +----+----------------------+

        After that, querying `Sample` will return objects of of this class.

        >>> db.session.query(Sample).all()
        [Table 1 in dataset "Lorem"]
    """

    __tablename__ = "table"

    id = db.Column(db.Integer, db.ForeignKey("sample.id"), primary_key=True)
    content = db.Column(db.Text())

    __mapper_args__ = {"polymorphic_identity": "table"}

    def __str__(self):
        return 'Table {} in dataset "{}"'.format(self.id, self.dataset)

    def __repr__(self):
        return str(self)
