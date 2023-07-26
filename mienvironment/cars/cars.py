from trytond.model import ModelView, ModelSQL,fields, Unique
from trytond.pyson import Eval, Bool
import datetime
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, StateTransition, Button

class Marca(ModelSQL,ModelView):
    'Marca'
    __name__='cars.marca'
    _rec_name='nombre'
    nombre = fields.Char('Nombre',required=True)
    modelos = fields.One2Many('cars.modelo','marca','Modelos')



class Modelo(ModelSQL, ModelView):
    'Modelo'
    __name__='cars.modelo'
    _rec_name='nombre'
    nombre=fields.Char('Nombre', required=True)
    marca=fields.Many2One('cars.marca','Marca',required=True, ondelete='CASCADE')
    fecha_lanzamiento=fields.Date('Fecha de lanzamiento')
    precio=fields.Numeric('Precio',
        domain=['OR',
            ('precio','>',0), ## Para que el precio sea poitivo
            ('precio','=',None) ## Para que el precio no sea obligatorio
        ]) 
    combustible=fields.Selection([
        ('V',''),
        ('G','Gasolina'),
        ('D','Diesel'),
        ('H','Hibrido'),
        ('E','Eléctrico')],'Combustible')
    caballos=fields.Integer('Numeros de Caballos')
    piezas=fields.Many2Many('cars.modelo_product','modelo','pieza','Piezas compatibles',
        domain=[
            ('type','=','goods') ## Para que dependa de que existe una marca
        ]
    )


    ## Poner la fecha de lanzamiento automáticamente a la hora de hoy
    @classmethod
    def default_fecha_lanzamiento(cls):
        return datetime.date.today()

    ## Poner en marca la primera marca que aparece (no útil)
    @classmethod
    def default_marca(cls):
        pool = Pool()
        Marca = pool.get('cars.marca')
        marca= Marca.search([],
            order=[('nombre','ASC'),('id','ASC')],limit=1)
        return marca[0].id



class ModeloProduct(ModelSQL):
    'Modelo Product'
    __name__='cars.modelo_product'
    _table = 'modelo_product_rel'
    modelo=fields.Many2One('cars.modelo','Modelo', required=True,ondelete='CASCADE')
    pieza=fields.Many2One('product.template','Pieza', required=True,ondelete='CASCADE')



class Coche(ModelSQL, ModelView):
    'Coche'
    __name__='cars.coche'
    matricula=fields.Char('Matricula', required=True,
        states={
                'readonly': Eval('id', -1) > 0 ## Or Greater(), Para que el field sea readonly cuando se ha guardado el registro
            }   
        )
    marca=fields.Many2One('cars.marca','Marca', ondelete='CASCADE')
    modelo=fields.Many2One('cars.modelo','Modelo', ondelete='CASCADE',
        domain=[
            ('marca','=',Eval('marca', -1)) ## Para que dependa de que existe una marca
        ],depends=['marca'],
        states={
            'required': Bool(Eval('marca', -1)), ## Para que sea required cuando haya una marca
            'invisible':~Bool(Eval('marca', -1)) ## Or Not(), para hacer invisible hasta que haya una marca
        }
    ) ## Para que depenga de la marca y no le aparezcan opciones
    propietario=fields.Many2One('party.party', 'Propietario',required=True)
    precio=fields.Numeric('Precio',
        domain=['OR',
            ('precio','>',0),## Para que el precio sea poitivo
            ('precio','=',None) ## Para que el precio no sea obligatorio
        ])
    fecha_matriculacion=fields.Date('Fecha de Matriculación')
    fecha_baja=fields.Date('Fecha de Baja')
    fecha_lanzamiento=fields.Function(fields.Date('Fecha de lanzamiento'), 'getFechaLanzamiento', searcher='searcherFechaLanzamiento')
    caballos=fields.Function(fields.Integer('Caballos'),'getCaballos', searcher='searcherCaballos')


    ## Conseguir los caballos de otro módulo
    def getCaballos(self,name):
        if self.modelo:
            return self.modelo.caballos
        else:
            return None

    ## Poner los caballos en el filtro
    @classmethod
    def searcherCaballos(cls,name,clause):
        return [('modelo.'+str(clause[0]),clause[1],clause[2])]
    
    ## Conseguir la fecha de lanzamiento de otro módulo
    def getFechaLanzamiento(self,name):
        if self.modelo:
            return self.modelo.fecha_lanzamiento
        else:
            return None

    ## Poner la fecha de lanzamiento en el filtro
    @classmethod
    def searcherFechaLanzamiento(cls,name,clause):
        return [('modelo.'+str(clause[0]),clause[1],clause[2])]

    ## Crear un constraint para que un valor sea único
    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('matricula_unica', Unique(t, t.matricula), 'cars.msg_coche_matricula_unique')
        ]
    
    ## Cuando se cambia la marca si solo hay un modelo se pone ese, si no en blanco
    @fields.depends('marca','modelo','precio')
    def on_change_marca(self):  
        if self.marca:
            if len(self.marca.modelos)==1:
                    self.modelo=self.marca.modelos[0]
            if self.modelo:            
                if self.marca != self.modelo.marca:
                        self.modelo=None
        else:
            self.modelo=None            

    ## Cunado se cambia el modelo se cambia el precio del coche
    @fields.depends('modelo','marca')
    def on_change_with_precio(self):  
        if self.marca and self.modelo and self.modelo.precio:
            return self.modelo.precio        



class BajaCoche(Wizard):
    "Dar de baja el coche"
    __name__="cars.coche.baja"

    start=StateView('cars.coche.baja.start','cars.coche_baja_start_view_form',[
        Button('Cancel','end','tryton-cancel'),
        Button('Baja','baja','tryton-ok',default=True)])
    baja=StateTransition()
    result=StateView('cars.coche.baja.result','cars.coche_baja_result_view_form',[
        Button('Close','end','tryton-close')])



class BajaCocheStart(Wizard):
    "Baja de Coche"
    __name__="cars.coche.baja.start"
    fecha_baja=fields.Date('Fecha de baja', required=True)

    @classmethod
    def default_fecha_baja(cls):
        return datetime.date.today()



class BajaCocheResult(Wizard):
    "Resultado de Baja de Coche"
    __name__="cars.coche.baja.result"
    cantidad=fields.Integer('Cantidad de cambios hechos', required=True, readonly=True)