# coding: utf-8

{
    'name': 'Export data in csv file',
    'version' : '1.0',
    'author' : 'CIEXPRO',
    'category' : 'Uncategorized',
    'description' : """

    Export modules data in CSV file automatically
 
    """,

    'depends': [
        'base'
    ],
    'data': [

        'security/export_data_security.xml',
        'security/ir.model.access.csv',

        'views/export_data_csv_view.xml',
        'views/export_data_csv_config_view.xml',
    ],
    'installable': True,
}

