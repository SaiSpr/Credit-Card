import streamlit as st
import json

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

st.title("Bank Loan Detection Web App")

st.image("image.jpg")






data = {"name": "John Doe", "age": 30, "email": "johndoe@example.com"}

url = "https://credit-card-production.up.railway.app/flow"

response = requests.post(url, json=data)
  

if response.status_code == 200:
    print("Data successfully sent to FastAPI app")
else:
    print(f"Error: {response.status_code}")
    


response = requests.get("https://credit-card-production.up.railway.app/json")

if response.status_code == 200:
    data = response.json()
    # do something with the data
else:
    print(f"Error: {response.status_code}")
    
    
    
    
#test    
    
    

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










st.sidebar.header('Input Features of The Transaction')



 
# Liste clients id sidebar 
list_client_prod = df_test_prod['SK_ID_CURR'].tolist()
client_id = st.sidebar.selectbox("Client Id list",list_client_prod)
# types = int(client_id)


oldbalanceorg = int(client_id)


if st.button("Detection Result"):
    values = {

    "oldbalanceorig": oldbalanceorg
    }


#     st.write(f"""### These are the transaction details:\n
#     Sender ID: {sender_name}
#     Receiver ID: {receiver_name}

#     4. Sender Balance Before Transaction: {oldbalanceorg}\n

#                 """)
    
    id = oldbalanceorg
    st.write(f"""Client_id is {id}""")
    res = requests.post(f"https://credit-card-production.up.railway.app/predict",json=values)
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
