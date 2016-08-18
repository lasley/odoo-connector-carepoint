# -*- coding: utf-8 -*-
# Copyright 2015-2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  )
from ..unit.backend_adapter import CarepointCRUDAdapter
from ..unit.mapper import CarepointImportMapper
from ..backend import carepoint
from ..unit.import_synchronizer import (DelayedBatchImporter,
                                        CarepointImporter,
                                        )

_logger = logging.getLogger(__name__)


class CarepointFdbImg(models.Model):
    _name = 'carepoint.fdb.img'
    _inherit = 'carepoint.binding'
    _inherits = {'fdb.img': 'odoo_id'}
    _description = 'Carepoint FdbImg'
    _cp_lib = 'fdb_img'  # Name of model in Carepoint lib (snake_case)

    odoo_id = fields.Many2one(
        string='FdbImg',
        comodel_name='fdb.img',
        required=True,
        ondelete='restrict'
    )


class FdbImg(models.Model):
    _inherit = 'fdb.img'

    carepoint_bind_ids = fields.One2many(
        comodel_name='carepoint.fdb.img',
        inverse_name='odoo_id',
        string='Carepoint Bindings',
    )


@carepoint
class FdbImgAdapter(CarepointCRUDAdapter):
    _model_name = 'carepoint.fdb.img'


@carepoint
class FdbImgBatchImporter(DelayedBatchImporter):
    """ Import the Carepoint FdbImgs.
    For every product category in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['carepoint.fdb.img']


@carepoint
class FdbImgImportMapper(CarepointImportMapper):
    _model_name = 'carepoint.fdb.img'
    direct = [
        ('IMGFILENM', 'file_name'),
        ('data', 'data'),
    ]

    @mapping
    def data(self, record):
        return {'data': record['data'].decode('base64')}

    @mapping
    def carepoint_id(self, record):
        return {'carepoint_id': record['IMGID']}


@carepoint
class FdbImgImporter(CarepointImporter):
    _model_name = ['carepoint.fdb.img']

    _base_mapper = FdbImgImportMapper

    def _get_carepoint_data(self):
        """ Return the raw Carepoint data for ``self.carepoint_id`` """
        _logger.debug('Getting CP data for %s', self.carepoint_id)
        record = self.backend_adapter.read(self.carepoint_id, [
            'IMGFILENM', 'IMAGE_PATH', 'IMGID'
        ])
        record['data'] = self.backend_adapter.read_image(record['IMAGE_PATH'])
        return record
