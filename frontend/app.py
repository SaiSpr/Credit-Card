import streamlit as st
import json
import requests as re

st.title("Credit Card Fraud Detection Web App")

st.image("image.png")

st.write("""
## About
Credit card fraud is a form of identity theft that involves an unauthorized taking of another's credit card information for the purpose of charging purchases to the account or removing funds from it.

**This Streamlit App utilizes a Machine Learning API in order to detect fraudulent credit card  based on the following criteria: hours, type of transaction, amount, balance before and after transaction etc.** 


st.sidebar.header('Input Features of The Transaction')

sender_name = st.sidebar.text_input("""Input Sender ID""")
receiver_name = st.sidebar.text_input("""Input Receiver ID""")
step = st.sidebar.slider("""Number of Hours it took the Transaction to complete: """)
types = st.sidebar.subheader(f"""
                 Enter Type of Transfer Made:\n\n\n\n
                 0 for 'Cash In' Transaction\n 
                 1 for 'Cash Out' Transaction\n 
                 2 for 'Debit' Transaction\n
                 3 for 'Payment' Transaction\n  
                 4 for 'Transfer' Transaction\n""")



if st.button("Detection Result"):
    values = {

    "oldbalanceorig": oldbalanceorg

    }


    st.write(f"""### These are the transaction details:\n
    Sender ID: {sender_name}
    Receiver ID: {receiver_name}

    1. Sender Previous Balance Before Transaction: {oldbalanceorg}\n

                """)

    res = re.post(f"http://backend.docker:8000/predict/",json=values)
    json_str = json.dumps(res.json())
    resp = json.loads(json_str)
    
    if sender_name=='' or receiver_name == '':
        st.write("Error! Please input Transaction ID or Names of Sender and Receiver!")
    else:
        st.write(f"""### The '{x}' transaction that took place between {sender_name} and {receiver_name} is {resp[0]}.""")

    data = {"name": "John Doe", "age": 30, "email": "johndoe@example.com"}

    url = "http://backend.docker:8000/flow"

    response = requests.post(url, json=data)
  

    if response.status_code == 200:
      print("Data successfully sent to FastAPI app")
    else:
      print(f"Error: {response.status_code}")
    


    response = requests.get("http://backend.docker:8000/json")

    if response.status_code == 200:
      data = response.json()
      # do something with the data
    else:
      print(f"Error: {response.status_code}")








