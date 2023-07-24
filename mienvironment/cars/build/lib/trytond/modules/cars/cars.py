from trytond.model import ModelView, ModelSQL,fields

class Marca(ModelSQL,ModelView):
    'Marca'
    __name__='cars.marca'
    nombre = fields.Char('Nombre',required=True)
    