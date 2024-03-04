import os
import streamlit as st
#Load environment variables

from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI

from langchain.sql_database import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate 

from langchain.llms import OpenAI
from langchain.agents import load_agent
from dotenv import load_dotenv
load_dotenv()
#Get the secret key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI APP TO CHAT WITH SQLLITE DB")
st.header="ASK ANYTHING ABOUT YOUR DB[Employers and Departments]"
query=st.text_input("ask question about Employers and Departments")
# cs="mssql+pymssql://sa:xxxxx@localhost/test"
# cs="mssql+pymssql://sa:xxxxx@localhost/test"
# db_engine=sql_toolkit.fromurl(cs)
db= SQLDatabase.from_uri("sqlite:///Employee.db")

llm=ChatOpenAI(temperature=0.6,model="gpt-4")
# llm=OpenAI (temperature=0.6,model="gpt-4")
sql_toolkit=SQLDatabaseToolkit(db=db,llm=llm)
sql_toolkit.get_tools()

prompt=ChatPromptTemplate.from_messages(
    [
        ("system",
        """
        you are a very intelligent AI assistant who is expert in identifing relevant questions from user and converting
        into sql queriers to generate coorect answer.
        Please use the belo context to write the SQLLite  queries and return the response as JSONf ormat only
        context:DB Name:Employee.db
        you must query against the connected database,it has total 2 tables,these are employees,department.
        employees table has id, name, position, department, hireDate, salary.It gives the employees information.
        departments table hasid, name, location .This gives department specific information.
        employees and departments are related by departmentid column in employees table and ID column in department table.
        
        example queries: select * from employees where department='IT'
        select * from department where location='Hyderabad'
        Dispalt the employers and their department names
        eg:select * from employess e join department d on e.departmentid=d.id
        """
        ),
        ("user","{question} ai: ")
    ]

        )
agent=create_sql_agent(llm=llm,toolkit=sql_toolkit,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
                       ,verbose=True
                       ,max_execution_time=100
                       ,max_iterations=1000
                       )

if st.button("Submit",type="primary"):
    if query is not None:
        response=agent.run(prompt.format_prompt(question=query))
        # response = agent({"input":prompt.format_prompt(question=query)})         
        st.write(response)