from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval

class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    coches = fields.One2Many('cars.coche','propietario','Coches')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.name.required=True ## Hace que el nombre sea requerido
        cls.name.states.update({ ## Solo lo cambia lo que está definido
            'readonly':Eval('id', -1) > 0 ## Para que no se pueda editar después de guardar
        })