
__version__ = '0.0.1'

from frappe import model
model.data_field_options = (
	'Email',
	'Name',
	'Phone',
	'URL',
	'Barcode',
    'Hijri Date'
)