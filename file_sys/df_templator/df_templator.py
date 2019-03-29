# -*- coding: utf-8 -*-
#python=3.6
"""
Synopsis: fill a template with variables from a pandas dataframe (schema and data)

Created: Created on Sun Feb 24 04:24:26 2019

Sources:

Author:   John Telfeyan
          john <dot> telfeyan <at> gmail <dot> com

Distribution: MIT Opens Source Copyright; Full permisions here:
    https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
         
"""
from jinja2 import Template
from jinja2 import Environment, meta
import pandas as pd

def template_df(df, template_file):
    """Given a pandas dataframe and a jinja2 template with variables that match 
    the df exactly; return a filled template for each row in the dataframe.
    """
    with open (template_file, 'r') as f:
        t = Template(f.read())
    rows = df.to_dict(orient='records')
    
    filled_templates = []
    for d in rows: 
        filled_templates.append(t.render(**d))
        
    return filled_templates


def get_template_vars(template_str):
    """ Find the unique, unset (required) variables in a template
    """
    env = Environment()
    template_source = env.parse(template_str)
    return meta.find_undeclared_variables(template_source)

def make_empty_csv_from_template(template_str, output_file):
    df =  pd.DataFrame(columns=list(get_template_vars(template_str)))
    df.to_csv(output_file)
    return

if __name__=="__main__":
    using_template = "templates/Create_Roles.SQL"
    df = pd.read_csv("data/test.csv")
    
    tmps = template_df(df, template_file = "templates/test_tmplt")
    with open(using_template, 'r') as f:
        tmp_str = f.read()
