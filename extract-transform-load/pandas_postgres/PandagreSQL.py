# -*- coding: utf-8 -*-
#python 3.6



#import psycopg2
import pandas as pd
from configparser import ConfigParser
from sqlalchemy import create_engine

class PandagreSQL:
    """Synopsis: A frankenstien combination of functions for ETLing pandas DFs to and from PostgreSQL
    
    Usage: Best practice: read in connection info from a .ini config file, the paramaters can 
    be over written and specified ad hoc as kwargs
    
    Created:  Thu Jan  3 14:28:24 2019
    
    Author:   John Telfeyan
              john <dot> telfeyan <at> gmail <dot> com
    
    Distribution: MIT Opens Source Copyright; Full permisions here:
        https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
             
    """
    def __init__(self, **kwargs):
        """ example use: db = PandagreSQL(config_filename="secrets/config.ini", meta_section="default")
        include your .ini in a .gitignore 
        
        """
        self.credentials = { "user" : "postgres",
                             "password": "",
                             "host" : "localhost",
                             "port" : "5432",
                             "name" : "postgres"
                             }
        self.can_sql()
        self.connected = False
        self.meta = {}
        
        if "config_filename" in kwargs and "meta_section" in kwargs:
            self.get_connection_from_ini(config_filename=kwargs.get("config_filename"),
                                         meta_section=kwargs.get("meta_section"))
        
        for key in self.credentials:
            if key in kwargs:
                self.credentials[key] = kwargs.get(key)
                
        connect_on_init = True if "connect" not in kwargs else kwargs.get("connect")
        self.build_connection_string(connect=connect_on_init)
        
        if self.connected :
            self.load_metadata()
    
    def can_sql(self):
        self.SQL = {}   #Dict of canned SQL 
        self.SQL["All Non-admin Tables"] = '''
        SELECT table_schema,table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' 
            AND table_schema = 'public' 
        ORDER BY table_schema,table_name;
        '''
        
        self.SQL["All Tables and Admin Tables"] = '''
        SELECT table_schema,table_name
        FROM information_schema.tables
        ORDER BY table_schema,table_name;
        '''
        
        self.SQL["All Databases"] = ''' 
        SELECT datname FROM pg_database
        WHERE datistemplate = false;
        '''

    def build_connection_string(self, connect=True, **kwargs):
        ''' By default, uses the credtentials dictionary to build a connection string. Any
        credential can be overwritten by passing it as an argument.
        
        '''
        _user = self.credentials["user"] if kwargs.get('user') == None else kwargs.get('user')
        _password = self.credentials["password"] if kwargs.get('password') == None else kwargs.get('password')
        _host = self.credentials["host"] if kwargs.get('host') == None else kwargs.get('host')
        _port = self.credentials["port"] if kwargs.get('port') == None else kwargs.get('port')
        _name = self.credentials["name"] if kwargs.get('name') == None else kwargs.get('name')
        delim = ":" if len(_password) >= 1 else ""
        self.connection_string = 'postgresql://%s%s%s@%s:%s/%s' % (_user, delim, _password, _host,
                                                                  _port, _name)
        if connect: self.connect()
        
    def connect(self):
        self.engine = create_engine(self.connection_string)
        self.conn = self.engine.connect()
        self.connected = True
        
        
    def get_connection_from_ini(self, config_filename, meta_section="default",
                                verbose=False):
        ''' Read  in connection credentials from a .ini file using config parser. This .ini
        should be excepmt from your code repo and not shared, for example by using .gitignore.
        A template is included. 
        .ini file format example:
            
        [meta_schema_name]
        user=admin
        password=postgres123
        host=127.0.0.1
        database=postgres
        '''
        self.config_filename = config_filename
        parser = ConfigParser()
        parser.read(config_filename)
        conn_info = {}
        
        if parser.has_section(meta_section):
            params = parser.items(meta_section)
            for param in params:
                conn_info[param[0]] = param[1]
        
            for key in self.credentials:
                if key in conn_info:
                    self.credentials[key] = conn_info[key]
                    if verbose : print("Updated %s.  " % key)
                         
            self.build_connection_string(connect=False)
        else:
            with open(config_filename) as f:   # ensure the file exists
                pass
            raise Exception('Section {0} not found in the {1} file'.format(meta_section, config_filename))
            
    def load_metadata(self):
        """ query/requery your db connections metadata via postgres specfic SQL
        """
        self.meta["user_tables"] = pd.read_sql(self.SQL["All Non-admin Tables"], self.engine)
        self.meta["all_tables"] = pd.read_sql(self.SQL["All Tables and Admin Tables"], self.engine)
        self.meta["all_databases"] = pd.read_sql(self.SQL["All Databases"], self.engine)
        

    
    def all_excel_worksheets_to_tables(self, excel_filename, schema_name="public", exists="fail"):
        """
        """
        xls=pd.ExcelFile(excel_filename)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet)
            df.to_sql( sheet, self.engine, schema=schema_name, if_exists=exists)
            
    #def df_to_table(self, df, table_name, schema_name="public"):
    #   df.to_scq(table_name, self.engine, schema = schema_name)
        
        

            
            
if __name__ == '__main__':
    # Example usage
    # best practice
    db = PandagreSQL(config_filename="secrets/config.ini", meta_section="default")
    db.load_metadata()
    meta = db.meta #for spyder ide
    db.all_excel_worksheets_to_tables("data/data_type_test.xlsx", exists="append")
    
    #one table
    df = pd.read_excel("data/float_test.xlsx", "Sheet3")
    df.to_sql("float_test", db.engine, if_exists="replace")
    db.load_metadata()
    
    #override the ini config file and log in as read_only user:
    rddb = db = PandagreSQL(config_filename="secrets/config.ini", 
                            meta_section="default", user="read_only")
    

    
    
        
        