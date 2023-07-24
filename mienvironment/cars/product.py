from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.pyson import Eval

class Product(metaclass=PoolMeta):
    __name__ = 'product.template'
    piezas = fields.Many2Many('cars.modelo_product','pieza','modelo','Modelos compatibles',
        states={
            'invisible': Eval('type', '') != 'goods' ## Para que el field sea invisible cuando type no sea goods
        },
        depends=['type'],
    )

    ## Poner la unidad automáticamente
    @classmethod
    def default_default_uom(cls):
        pool = Pool()
        ProductUOM = pool.get('product.uom')
        productUOM= ProductUOM.search([
            ('name','=','Unit')
        ])
        return productUOM[0].id

