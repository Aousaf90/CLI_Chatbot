from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain
from sql_query import get_company_data


history = []


def question(selected_company):
    print(f"Selected Company: {selected_company}")

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    )
    
    db = SQLDatabase.from_uri("mysql+mysqlconnector://root:@localhost/cli_chatbot")
    execute_query = QuerySQLDataBaseTool(db=db)
    answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, provide an answer that is filtered by the selected company ({selected_company}). 
    If the SQL result contains products from companies other than the selected company, include a message indicating which company each product belongs to.
    If the question is related to the selected company ({selected_company}), provide an answer specific to this company, unless the user asks a more explicit or detailed question about a different company or product.
    If the question is related to products in general filter them by company ({selected_company})
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer:"""
    )
    company_tables = db.get_usable_table_names()
    if not company_tables:
        return
    
    write_query = create_sql_query_chain(llm, db)
    
    # Define the query with proper filtering for the selected company
    answer = answer_prompt | llm | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        ) | answer
    )
    
    print("Ask DB: \n")
    
    while True:
        user_question = input("\n>> ")
        answer = ""
        
        # Invoke the chain with the selected company
        result = chain.invoke({"question": user_question, "selected_company": selected_company})
        
        for chunk in result:
            print(chunk, end="", flush=True)
            answer += chunk  # Accumulate the chunks into the full answer
        history.append(("system", user_question))
        history.append(("user", answer))
        
        if user_question.lower() == "exit":
            break


if __name__ == "__main__":
    select_company_string = "Select from the given comapny to get stated: "
    company_list = ""
    company_details = {}
    company_data = get_company_data()
    for company in company_data:
        company_details.update({company[0]: company[1]})
        company_id = company[0]
        company_name = company[1]
        company_list += f"{company_id} : {company_name} \n"
    print(company_list)
    selected_company = int(input(select_company_string))
    question(selected_company=company_details[selected_company])
