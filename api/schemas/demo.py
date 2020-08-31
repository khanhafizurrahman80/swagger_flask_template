from extension import ma, db
from models.demo import Demo


class DemoSchema(ma.SQLAlchemyAutoSchema):
    
    class Meta:
        model = Demo
        sqla_session = db.session
        load_instance = True
