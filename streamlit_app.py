import streamlit as st
import json
import requests as re

from streamlit_echarts import st_echarts
import streamlit.components.v1 as components
st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd
import matplotlib.pyplot as plt
import requests
import joblib
import pickle
import shap
import seaborn as sns 
plt.style.use('ggplot')

st.title("Credit Card Fraud Detection Web App")

st.image("image.png")

st.write("""
## About
Credit card fraud is a form of identity theft that involves an unauthorized taking of another's credit card information for the purpose of charging purchases to the account or removing funds from it.

**This Streamlit App utilizes a Machine Learning model served as an API in order to detect fraudulent credit card transactions based on the following criteria: hours, type of transaction, amount, balance before and after transaction etc.**       
""")




data = {"name": "John Doe", "age": 30, "email": "johndoe@example.com"}

url = "https://credit-card-production.up.railway.app/flow"

response = re.post(url, json=data)
json_str = json.dumps(res.json())
resp = json.loads(json_str)  

if response.status_code == 200:
    print("Data successfully sent to FastAPI app")
else:
    print(f"Error: {response.status_code}")
    
#     res = re.post(f"https://credit-card-production.up.railway.app/predict",json=values)
#     json_str = json.dumps(res.json())
#     resp = json.loads(json_str)    
    
    
    
    
    
    
    

def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

# Read 
list_file = open('cols_shap_local.pickle','rb')
cols_shap_local = pickle.load(list_file)
print(cols_shap_local)

#df_test_prod = pd.read_csv('df_test_ok_prod_100.csv', index_col=[0])
df_test_prod = pd.read_csv('df_test_ok_prod_100_V7.csv', index_col=[0])
df_test_prod['LOAN_DURATION'] = 1/df_test_prod['PAYMENT_RATE']
df_test_prod.drop(columns=['TARGET'], inplace=True)
df_test_prod_request  = df_test_prod.set_index('SK_ID_CURR')

df_train = pd.read_csv('df_train_prod_1.csv', index_col=[0])
df_train['LOAN_DURATION'] = 1/df_train['PAYMENT_RATE']


#################################################
def explain_plot(id, pred):
    
    pipe_prod = joblib.load('LGBM_pipe_version7.pkl')
    df_test_prod_1 = df_test_prod.reset_index(drop=True)
    df_test_prod_request_1 = df_test_prod_1.reset_index().set_index(['SK_ID_CURR', 'index'])
    df_shap_local = df_test_prod_request_1[df_test_prod_request_1.columns[df_test_prod_request_1.columns.isin(cols_shap_local)]]
    values_id_client = df_shap_local.loc[[id]]
    

    explainer = shap.TreeExplainer(pipe_prod.named_steps['LGBM'])
      
    observation = pipe_prod.named_steps["transform"].transform(df_shap_local)
    observation_scale = pipe_prod.named_steps["scaler"].transform(observation)

    shap_values = explainer.shap_values(observation_scale)

    if pred == 1:
        p = st_shap(shap.force_plot(explainer.expected_value[1], shap_values[1][values_id_client.index[0][1],:],values_id_client))
    else:
        p = st_shap(shap.force_plot(explainer.expected_value[0], shap_values[0][values_id_client.index[0][1],:],values_id_client))
    return p
###################################################


st.write(df_train.shape)
# Filtrer les clients rembourser et non rembourser 
df_train_rembourse = df_train[df_train['TARGET']== 0.0]
df_train_not_rembourse = df_train[df_train['TARGET']== 1.0]

# Sélectionner les colonnes pour le dashboard
cols_dashbord = ['SK_ID_CURR','AMT_CREDIT', 'AMT_GOODS_PRICE', 'AMT_INCOME_TOTAL', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'AGE', 'LOAN_DURATION']



df_train_not_rembourse = df_train_not_rembourse[cols_dashbord]
df_train_rembourse = df_train_rembourse[cols_dashbord]




# Titre 
st.title("****Scoring crédit pour calculer la probabilité qu’un client rembourse son crédit****")



# logo sidebar 
st.sidebar.image("1200px-Home_Credit_&_Finance_Bank.svg.png", use_column_width=True)



# Liste clients id sidebar 
list_client_prod = df_test_prod['SK_ID_CURR'].tolist()
client_id = st.sidebar.selectbox("Client Id list",list_client_prod)
client_id = int(client_id)






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
types = st.sidebar.selectbox("",(0,1,2,3,4))
x = ''
if types == 0:
    x = 'Cash in'
if types == 1:
    x = 'Cash Out'
if types == 2:
    x = 'Debit'
if types == 3:
    x = 'Payment'
if types == 4:
    x =  'Transfer'
    
amount = st.sidebar.number_input("Amount in $",min_value=0, max_value=110000)
oldbalanceorg = st.sidebar.number_input("""Sender Balance Before Transaction was made""",min_value=0, max_value=110000)
newbalanceorg= st.sidebar.number_input("""Sender Balance After Transaction was made""",min_value=0, max_value=110000)
oldbalancedest= st.sidebar.number_input("""Recipient Balance Before Transaction was made""",min_value=0, max_value=110000)
newbalancedest= st.sidebar.number_input("""Recipient Balance After Transaction was made""",min_value=0, max_value=110000)
isflaggedfraud = 0
if amount >= 200000:
  isflaggedfraud = 1
else:
  isflaggedfraud = 0


if st.button("Detection Result"):
    values = {
    "step": step,
    "types": types,
    "amount": amount,
    "oldbalanceorig": oldbalanceorg,
    "newbalanceorig": newbalanceorg,
    "oldbalancedest": oldbalancedest,
    "newbalancedest": newbalancedest,
    "isflaggedfraud": isflaggedfraud
    }


    st.write(f"""### These are the transaction details:\n
    Sender ID: {sender_name}
    Receiver ID: {receiver_name}
    1. Number of Hours it took to complete: {step}\n
    2. Type of Transaction: {x}\n
    3. Amount Sent: {amount}$\n
    4. Sender Balance Before Transaction: {oldbalanceorg}$\n
    5. Sender Balance After Transaction: {newbalanceorg}$\n
    6. Recepient Balance Before Transaction: {oldbalancedest}$\n
    7. Recepient Balance After Transaction: {newbalancedest}$\n
    8. System Flag Fraud Status(Transaction amount greater than $200000): {isflaggedfraud}
                """)
    
    id = client_id
    st.write(f"""Client_id is {id}""")
    res = re.post(f"https://credit-card-production.up.railway.app/predict",json=values)
    json_str = json.dumps(res.json())
    resp = json.loads(json_str)
    
    st.write(f"""resp is {resp}""")
    st.write(f"""res is {res}""")
    
    if sender_name=='' or receiver_name == '':
        st.write("Error! Please input Transaction ID or Names of Sender and Receiver!")
    else:
        st.write(f"""### The '{x}' transaction that took place between {sender_name} and {receiver_name} is {resp}.""")
        

    pred = resp

#     pred = prediction["prediction"]

#     probability_value_0 = round(prediction["probability_0"] * 100,2)
#     probability_value_1 = round(prediction["probability_1"] * 100,2)


    st.header(f'*Result of the credit application for the customer {client_id}*')

    st.write(pred)
    st.write(type(pred))
    if pred == 1:
      st.error('Crédit Refusé')
      option_1 = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "Pressure",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": probability_value_1, "name": "Probabilité %"}],
                }
            ],
        }

      st_echarts(options=option_1, width="100%", key=0)
      st.header(f'*Les données qui ont le plus influencé le calcul de la prédiction pour le client {client_id}*')

      explain_plot(client_id, pred)
    else:
        st.success('Crédit Accordé')
        option = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "Pressure",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": probability_value_0, "name": "Probabilité %"}],
                }
            ],
        }

        st_echarts(options=option, width="100%", key=0)

        st.header(f'*Les données qui ont le plus influencé le calcul de la prédiction pour le client {client_id}*')
        explain_plot(client_id, pred)   
