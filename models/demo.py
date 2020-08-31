from extension import db


class Demo(db.Model):
    demo_id = db.Column(db.Integer, primary_key=True)
    
    def __init__(self, **kwargs):
        super(Demo, self).__init__(**kwargs)
        
    def __repr__(self):
        return "<Demo %s>" % self.demo_id

