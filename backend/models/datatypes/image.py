from .sample import Sample
from ...aergia import db


class Image(Sample):
    """
    A sample containing an image.

    Creating and saving a table will result in one entry in the `Sample` database table that
    contains the generic sample information (features, dataset) with the `type` set to `table`
    (see `Image.__mapper_args_['polymorphic_identity']`).

    Furthermore, another entry will be created in the database table `Image`. Its id will reference
    (be the same) as the id of the entry in `Sample`. Its purpose is to save all information that
    are specific to a sample of type `Image` (data).

    Examples:
        The constructor takes all keyword arguments of `Sample` in addition to `data`.

        >>> import json
        >>> from backend.models import Dataset
        >>> image_data = open('folder/your_image.png', 'rb').read()
        >>> image = Image(
        ...     features=json.dumps({'width': 480, 'blue_pixels': 1487}),
        ...     dataset=db.session.query(Dataset).first()
        ...     content = image_data
        ... )
        >>> db.session.add(image_data)
        >>> db.session.commit()

        After running the example, the database will look like this:

        Database table `Sample`
        +----+-------------------------------------+------------+-------+
        | id | features                            | dataset_id | type  |
        +====+=====================================+============+=======+
        | 1  | {'width': 480, 'blue_pixels': 1487} | 1          | table |
        +----+-------------------------------------+------------+-------+

        Databaes table `Image`
        +----+--------------------------------------------------------------------+
        | id | content                                                            |
        +====+====================================================================+
        | 1  | 45,06 kB 00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00 |
        +----+--------------------------------------------------------------------+

        After that, querying `Sample` will return objects of of this class.

        >>> db.session.query(Sample).all()
        [Image 1 in dataset "Lorem"]
    """
    __tablename__ = 'image'

    id = db.Column(db.Integer, db.ForeignKey('sample.id'), primary_key=True)
    data = db.Column(db.BLOB)

    __mapper_args__ = {
        'polymorphic_identity': 'image'
    }

    def __str__(self):
        return 'Image {} in dataset "{}"'.format(self.id, self.dataset)

    def __repr__(self):
        return str(self)
