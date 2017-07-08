

'''
   _____ __________.___  ___________                   __  .__
  /  _  \\______   \   | \_   _____/_ __  ____   _____/  |_|__| ____   ____   ______
 /  /_\  \|     ___/   |  |    __)|  |  \/    \_/ ___\   __\  |/  _ \ /    \ /  ___/
/    |    \    |   |   |  |     \ |  |  /   |  \  \___|  | |  (  <_> )   |  \\___ \
\____|__  /____|   |___|  \___  / |____/|___|  /\___  >__| |__|\____/|___|  /____  >
        \/                    \/             \/     \/                    \/     \/
xmlrpc wrapper functions for reading and writing to ERP
HITS /home/iron-aiden/udesco/odoo10/odoo/service/wsgi_server.py
'''

# following is NOT postgres database settings - it is odoo settings
# pg database connections are supposed to match with odoo10/debian/odoo.conf


# import oerplib
#
#
# def auth_erp():
#     oerp = oerplib.OERP(server='localhost', database=DB, protocol='xmlrpc', port=8069)
#     try:
#         uid = oerp.login(user=USERNAME, passwd=PASSWORD)
#     except:
#         init_uid = oerp.login(user='admin', passwd='admin')
#         user_obj = oerp.get('res.users')
#         user_obj.write([1], {'login': USERNAME, 'password': PASSWORD})
#         uid = oerp.login(user=USERNAME, passwd=PASSWORD)
#     return uid, oerp




import xmlrpclib

#following is NOT postgres database settings - it is odoo settings
#pg database connections are supposed to match with odoo10/debian/odoo.conf
USERNAME = 'aiden'
PASSWORD = 'odoo'
DB = 'odoo_demo'
SOCK_MODELS = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
SOCK_COMMON = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/common')



#AUTH
def auth_erp(username = USERNAME, password = PASSWORD, db = DB, sock_common = SOCK_COMMON, sock_models=SOCK_MODELS):
    #sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/common')
    try:
        uid = sock_common.authenticate(db, username, password, {})
        if not uid:
            init_uid = sock_common.authenticate(db, 'admin', 'admin', {})
            sock_models.execute_kw(db, init_uid, 'admin', 'res.users', 'write',
                                   [init_uid, {'login': username, 'password': password}])
            uid = sock_common.authenticate(db, username, password, {})
    except Exception as e:
        print e
        # init_uid =  sock_common.authenticate(db, 'admin', 'admin', {})
        # sock_models.execute_kw(db, init_uid, password, 'res.users', 'write', [init_uid, {'login':username,'password':password}])
        # uid = sock_common.authenticate(db, username, password, {})
    return uid

UID = auth_erp()


#INSPECT FIELDS
def inspect_erp(model,username = USERNAME, password = PASSWORD, db = DB,
             uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON):
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    sock_models.execute_kw(
    db, uid, password, model, 'fields_get',
    [], {'attributes': ['string', 'help', 'type']})

#READ
def read_erp(model,function,username = USERNAME, password = PASSWORD, db = DB,
             uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON):
    '''

    :param model: the ERP model you are looking for (str)
    :param function: some function to check on model, ex, 'check_access_rights
    :param username:
    :param password:
    :param db:
    :param uid:
    :param sock_models:
    :return:
    '''
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    #sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    try:
        ret = sock_models.execute_kw(db, uid, password,
            model, function #'check_access_rights',
            ['read'], {'raise_exception': False})
    except Exception as e:
        print e
        if "Fault 2: 'None'" in str(e):
            ret = str(e)
        else:
            raise
    return ret


#SEARCH
def search_erp(model,search_list_of_tuples,username = USERNAME, password = PASSWORD, db = DB,
               uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON):
    '''

    :param model: the ERP model you are looking for (str)
    :param search_list_of_tuples: [('field1','op',value1),('field1','op',value1),('field1','op',value1)]
    :param username:
    :param password:
    :param db:
    :param uid:
    :param sock_models:
    :return: list of IDS of models
    '''
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    #sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    try:
        ids = sock_models.execute_kw(db, uid, password,
            model, 'search',
            [search_list_of_tuples], #[('name','=','Stock')]
            #{'offset': 10, 'limit': 5}
            )
    except Exception as e:
        print e
        if "Fault 2: 'None'" in str(e):
            ids=[]
        else:
            raise
    return ids


#SEARCH-READ
def search_read_erp(model,search_list_of_tuples,fields,username = USERNAME, password = PASSWORD,
                    db = DB, uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON, limit=9999):
    '''

    :param model: the ERP model you are looking for (str)
    :param search_list_of_tuples: [('field1','op',value1),('field1','op',value1),('field1','op',value1)]
    :param fields:  list of fields to return
    :param username:
    :param password:
    :param db:
    :param uid:
    :param sock_models:
    :param limit:
    :return: a list of dictionaries of field values
    '''
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    #sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    try:
        vals = sock_models.execute_kw(db, uid, password,
                          model, 'search_read',
                          [search_list_of_tuples],
                          {'fields': fields, 'limit': limit})
    except Exception as e:
        print e
        if "Fault 2: 'None'" in str(e):
            vals=[]
        else:
            raise
    return vals

#CREATE
def create_erp(model,create_dict,username = USERNAME, password = PASSWORD,
                    db = DB, uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON):
    '''

    :param model: the ERP model you are looking for (str)
    :param search_list_of_tuples: [('field1','op',value1),('field1','op',value1),('field1','op',value1)]
    :param fields:  list of fields to return
    :param username:
    :param password:
    :param db:
    :param uid:
    :param sock_models:
    :param limit:
    :return: id of created record
    '''
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    #sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    created_id = sock_models.execute_kw(db, uid, password, model, 'create', [create_dict])

    return created_id


#UPDATE RECORD
def write_erp(model,ids,update_dict,username = USERNAME, password = PASSWORD,
                    db = DB, uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON):
    '''

    :param model: the ERP model you are looking for (str)
    :param search_list_of_tuples: [('field1','op',value1),('field1','op',value1),('field1','op',value1)]
    :param fields:  list of fields to return
    :param username:
    :param password:
    :param db:
    :param uid:
    :param sock_models:
    :param limit:
    :return: id of created record
    '''
    ids = [ids] if isinstance(ids, (int, long)) else ids
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    #sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    sock_models.execute_kw(db, uid, password, model, 'write', [ids, update_dict])

#DELETE RECORD
def delete_erp(model,ids,update_dict,username = USERNAME, password = PASSWORD,
                    db = DB, uid = UID, sock_models = SOCK_MODELS,sock_common=SOCK_COMMON):
    '''

    :param model: the ERP model you are looking for (str)
    :param search_list_of_tuples: [('field1','op',value1),('field1','op',value1),('field1','op',value1)]
    :param fields:  list of fields to return
    :param username:
    :param password:
    :param db:
    :param uid:
    :param sock_models:
    :param limit:
    :return: id of created record
    '''
    ids = [ids] if isinstance(ids, (int, long)) else ids
    if not uid:
        print 'reauth'
        uid = auth_erp(username = username, password = password, db = db, sock_common = sock_common)
    #sock_models = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/2/object')
    sock_models.execute_kw(db, uid, password, model, 'unlink', [ids])






