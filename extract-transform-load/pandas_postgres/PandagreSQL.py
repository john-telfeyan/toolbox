# -*- coding: utf-8 -*-
#python 3.6



#import psycopg2
import pandas as pd
from configparser import ConfigParser
from sqlalchemy import create_engine

class PandagreSQL:
    """Synopsis: Additinal functions for ETLing pandas DFs to and from PostgreSQL to help novice data scientists
    
    Usage: Best practice: read in connection info from a .ini config file, the paramaters can 
    be over written and specified ad hoc as kwargs
    
    Created:  Thu Jan  3 14:28:24 2019
    
    Author:   John Telfeyan
              john <dot> telfeyan <at> gmail <dot> com
    
    Distribution: MIT Opens Source Copyright; Full permisions here:
        https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
             
    """
    def __init__(self, **kwargs):
        """ 
        Example 1, Connect with ini file:
        db = PandagreSQL(config_filename="secrets/config.ini", meta_section="default")
        include your .ini in a .gitignore 
        
        Example 2, Connect to local DB with default settings :
        db = PandagreSQL()                    #(no password)
        db = PandagreSQL(password="Pa$$w0rd") #(custom password)
        
        Example 3, Build, but dont connect:
        db = PandagreSQL(connect=False)
        
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
        
        # First load files from config file (Best practice)
        if "config_filename" in kwargs and "meta_section" in kwargs:
            self.get_connection_from_ini(config_filename=kwargs.get("config_filename"),
                                         meta_section=kwargs.get("meta_section"))
        
        # Check if the user overided config credentials in the declaration
        for key in self.credentials:
            if key in kwargs:
                self.credentials[key] = kwargs.get(key)
        
        # Attempt to connect 
        connect_on_init = True if "connect" not in kwargs else kwargs.get("connect")
        self.build_connection_string(connect=connect_on_init)
        
        if self.connected :
            self.load_metadata()
    
    def can_sql(self):
        """Build a dictionary of canned SQL statements specific to Postgres with short
        descritpions:
           "User Tables"   : df with all user created tables (excluding default PG tables)
           "All Tables"    : df including user and PG administrative tables; editing these will break the DB
           "All Databases" : df with list of all DBs accessable to user
        """
        self.SQL = {}   #Dict of canned SQL 
        self.SQL["User Tables"] = '''
        SELECT table_schema,table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' 
            AND table_schema = 'public' 
        ORDER BY table_schema,table_name;
        '''
        
        self.SQL["All Tables"] = '''
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
        # Allow replacement of specific credentials, ad-hoc (e.g. user/pw)
        _creds = {}
        for key in self.credentials:
            _creds[key] = self.credentials[key] if kwargs.get(key) == None else kwargs.get(key)
        _delim = ":" if len(_creds["password"]) >= 1 else ""
        _params = (_creds["user"], _delim, _creds["password"], _creds["host"], _creds["port"], _creds["name"])
        self.connection_string = 'postgresql://%s%s%s@%s:%s/%s' % _params
        if connect: self.connect()
        
    def connect(self):
        """ Connect using the self.connection string
        """
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
        """Query/requery your db connections metadata via postgres specfic SQL
        """
        self.meta["user_tables"] = pd.read_sql(self.SQL["User Tables"], self.engine)
        self.meta["all_tables"] = pd.read_sql(self.SQL["All Tables"], self.engine)
        self.meta["all_databases"] = pd.read_sql(self.SQL["All Databases"], self.engine)
        

    
    def all_excel_worksheets_to_tables(self, excel_filename, schema_name="public", exists="fail"):
        """Convert all worksheets in an Excel workbook to tables; sheet names become table names
        """
        xls=pd.ExcelFile(excel_filename)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet)
            df.to_sql( sheet, self.engine, schema=schema_name, if_exists=exists)
            
    #def df_to_table(self, df, table_name, schema_name="public"):
    #   df.to_scq(table_name, self.engine, schema = schema_name)
        
        

            
           
if __name__ == '__main__':
    # Example usage
    # best practice: connection info in config.ini
    db = PandagreSQL(config_filename="secrets/config.ini", meta_section="default")
    db.load_metadata()
    meta = db.meta #for spyder ide
    db.all_excel_worksheets_to_tables("data/data_type_test.xlsx", exists="append")
    
    # add one table
    df = pd.read_excel("data/float_test.xlsx", "Sheet3")
    df.to_sql("float_test", db.engine, if_exists="replace")
    db.load_metadata() #check to see if it added
    
    # override the ini config file and log in as read_only user:
    rddb = PandagreSQL(config_filename="secrets/config.ini", 
                            meta_section="default", user="read_only")
    

    
    
        
        