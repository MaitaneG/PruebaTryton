from trytond.pool import Pool
from . import cars
from . import party
from . import product

__all__ = ['register']


def register():
    Pool.register(
        cars.Marca,
        cars.Modelo,
        cars.Coche,
        cars.ModeloProduct,
        cars.BajaCocheStart,
        cars.BajaCocheResult,
        party.Party,
        product.Product,
        module='cars', type_='model')
    Pool.register(
        cars.BajaCoche,
        module='cars', type_='wizard')
    Pool.register(
        module='cars', type_='report')
