from trytond.pool import Pool
from . import cars

__all__ = ['register']


def register():
    Pool.register(
        cars.Marca,
        module='cars', type_='model')
    Pool.register(
        module='cars', type_='wizard')
    Pool.register(
        module='cars', type_='report')
