import xmlrpclib


username = 'aiden' #'Email' in create database splash page - really res.user username
password = 'odoo'
db = 'odoo'

#LOGIN
'''
The xmlrpc/2/common endpoint provides meta-calls which dont require authentication, such as the authentication itself or fetching version information
'''
sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/common')
uid = sock_common.authenticate(db, username, password, {})



#CONNECTION TO WORK WITH MODELS
'''
The second endpoint is xmlrpc/2/object, is used to call methods of odoo models via the execute_kw RPC function.

Each call to execute_kw takes the following parameters:

    db - the database to use, a string
    uid - the user id (retrieved through authenticate), an integer
    password - the user's password, a string
    'res.partner' - the model name, a string
    'check_access_rights' - the method name, a string
    an array/list of parameters passed by position
    a mapping/dict of parameters to pass by keyword (optional)
'''
sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')


#READ

ret = sock_models.execute_kw(db, uid, password,
	'res.partner', 'check_access_rights',
	['read'], {'raise_exception': False})
print ret


#SEARCH
search = [('name','=','Stock')]#[['is_company', '=', True], ['customer', '=', True]]
ids = sock_models.execute_kw(db, uid, password,
	'account.account', 'search',
	[search],
	#{'offset': 10, 'limit': 5}
							 )
print ids


#SEARCH-READ
vals = sock_models.execute_kw(db, uid, password,
				  'res.partner', 'search_read',
				  [[['company_id', '=', 1],]],
				  {'fields': ['name', 'country_id', 'comment'], 'limit': 5})

print vals

