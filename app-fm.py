import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="EY Financial Model", page_icon="🧊", layout="wide", initial_sidebar_state="auto")

###Model input and assumptions/ streamlit sidebar###

st.sidebar.title("Business Assumptions")

#Initial input and model assumptions
st.sidebar.subheader("Setup")


model_start = st.sidebar.number_input("Model start", min_value=2020, value=2020, max_value=2100)
forecast_period = st.sidebar.number_input("Forecast period", min_value=3, value=5, max_value=51)

#income statement inputs
st.sidebar.subheader("P&L Assumptions")


revenue_units = st.sidebar.number_input("Number of units sold", min_value=1, value=240000)
revenue_price = st.sidebar.number_input("Price", min_value=0, value=5)
revenue_units_growth = st.sidebar.number_input("Revenue growth",value=0.1)
gross_margin =  st.sidebar.number_input("Gross margin",value=0.60, min_value=0.00, max_value=1.00)
sm_margin = st.sidebar.number_input("S&M as percentage of revenue",value=0.20, min_value=0.00, max_value=1.00)
ga_margin = st.sidebar.number_input("G&A as percentage of revenue",value=0.10, min_value=0.00, max_value=1.00)
depreciation_rate = st.sidebar.number_input("Depreciation rate",value=0.10, min_value=0.00, max_value=1.00)
tax_rate = st.sidebar.number_input("Tax rate",value=0.00, min_value=0.00, max_value=1.00)

#balance sheet input
st.sidebar.subheader("Balance sheet Assumptions")

capex_year0 = st.sidebar.number_input("Annual capital expenditure",value=350000, min_value=0)
capex_growth = st.sidebar.number_input("capital expenditure growth",value=-1.00)
dso = st.sidebar.number_input("Day of outstanding recievables",value=15, min_value=0)
dio = st.sidebar.number_input("Days of outstanding inventory",value=60, min_value=0)
dpo = st.sidebar.number_input("Days of outstanding payables",value=30, min_value=0)
prep_sm_gm = st.sidebar.number_input("Prepayments as percentage of operating expenses",value=0.10, min_value=0.00, max_value=1.00)
arrued_sm_gm = st.sidebar.number_input("Accruals as percentage of operating expenses",value=0.083, min_value=0.00, max_value=1.00)
#equity assumptions
cap_injection1 = st.sidebar.number_input("Capital injection at year 1",value=400000, min_value=0)

#Valuation assumptions
st.sidebar.subheader("Valuation assumptions")

cost_of_capital = st.sidebar.number_input("Cost of capital",value=0.10, min_value=0.00, max_value=1.00)
terminal_growth = st.sidebar.number_input("Terminal growth rate",value=0.02, min_value=0.00, max_value=1.00)





###financial model calculations###



period = range(model_start,model_start+forecast_period)
bs_columns = ["beginning balance", "change", "ending balance"]

def revenue_calc ():
  pd.options.display.float_format = '${:,.0f}'.format
  columns = ["units", "price", "revenue"]
  df = pd.DataFrame(columns=columns, index=period)
  df["price"] = revenue_price
  units_list = [revenue_units]
  for yr in range(forecast_period-1):
    units_list.append(units_list[yr] * (1 + revenue_units_growth))
  df["units"] = units_list
  df["revenue"] = df["units"] * df["price"]
  return df["revenue"]

df_revenue = revenue_calc()


def cos_calc():
  columns = ["cost of sales"]
  df = pd.DataFrame(columns=columns, index=period)
  df["cost of sales"] = revenue_calc() * (1 - gross_margin)
  return df["cost of sales"]

df_cos = cos_calc()


def sm_calc():
  columns = ["selling & marketing expenses"]
  df = pd.DataFrame(columns=columns, index=period)
  df["selling & marketing expenses"] = revenue_calc() * (sm_margin)
  return df["selling & marketing expenses"]

df_sm = sm_calc()


def ga_calc():
  columns = ["general & admin expenses"]
  df = pd.DataFrame(columns=columns, index=period)
  df["general & admin expenses"] = revenue_calc() * (ga_margin)
  return df["general & admin expenses"]

df_ga = ga_calc()

def fixed_assets_calc():
  columns = ["depreciation rate", "beginning cost","additions", "ending cost", "beginning depreciation", "deprecaition", "ending depreciation" , "NBV"]
  df = pd.DataFrame(columns=columns, index=period)
  
  df['depreciation rate'] = depreciation_rate / 1
  additions_list = [capex_year0]
  for yr in range(forecast_period-1):
    additions_list.append(additions_list[yr] * (1 + capex_growth))
  df['additions'] = additions_list
  
  beg_list = [0]
  for yr in range(forecast_period-1):
    beg_list.append(additions_list[yr] + beg_list[yr])
  df['beginning cost'] = beg_list
  
  df['ending cost'] = df['beginning cost'] + df['additions']
  df['deprecaition'] = df['ending cost'] * df['depreciation rate']
  
  beg_dep_list = [0]
  for yr in range(forecast_period-1):
    beg_dep_list.append(beg_dep_list[yr] + df["deprecaition"][model_start+yr])
  df["beginning depreciation"] = beg_dep_list
  
  df['ending depreciation'] = df['beginning depreciation'] + df['deprecaition']
  df['NBV'] = df['ending cost'] - df['ending depreciation']

  return df['additions'], df['deprecaition'], df['NBV']

additions_r, depreciation_r, NBV_r = fixed_assets_calc()

def recievables_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  df['ending balance'] = (revenue_calc() / 365) * dso
  beg_bal_list = [0]
  for yr in range(forecast_period-1):
    beg_bal_list.append(df['ending balance'][model_start + yr])
  df['beginning balance'] = beg_bal_list
  df['change'] = df['ending balance'] - df['beginning balance']
  return df['ending balance'], df['change']

rec_bal, rec_change = recievables_calc()


def inventory_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  df['ending balance'] = (cos_calc() / 365) * dio
  beg_bal_list = [0]
  for yr in range(forecast_period-1):
    beg_bal_list.append(df['ending balance'][model_start + yr])
  df['beginning balance'] = beg_bal_list
  df['change'] = df['ending balance'] - df['beginning balance']
  return df['ending balance'], df['change']

inv_bal, inv_change = inventory_calc()


def payables_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  df['ending balance'] = (cos_calc() / 365) * dpo
  beg_bal_list = [0]
  for yr in range(forecast_period-1):
    beg_bal_list.append(df['ending balance'][model_start + yr])
  df['beginning balance'] = beg_bal_list
  df['change'] = df['ending balance'] - df['beginning balance']
  return df['ending balance'], df['change']

pay_bal, pay_change = payables_calc()


def prepayments_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  df['ending balance'] = (sm_calc() + ga_calc()) * prep_sm_gm
  beg_bal_list = [0]
  for yr in range(forecast_period-1):
    beg_bal_list.append(df['ending balance'][model_start + yr])
  df['beginning balance'] = beg_bal_list
  df['change'] = df['ending balance'] - df['beginning balance']
  return df['ending balance'], df['change']

prep_bal, prep_change = prepayments_calc()


def accrulas_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  df['ending balance'] = (sm_calc() + ga_calc()) * arrued_sm_gm
  beg_bal_list = [0]
  for yr in range(forecast_period-1):
    beg_bal_list.append(df['ending balance'][model_start + yr])
  df['beginning balance'] = beg_bal_list
  df['change'] = df['ending balance'] - df['beginning balance']
  return df['ending balance'], df['change']

accrued_bal, accrued_change = accrulas_calc()

# debt calculations

def share_capital_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  cap_inj_list = []
  for yr in range(forecast_period-1):
    cap_inj_list.append(0)
  cap_inj_list.insert(0,cap_injection1)
  df['change'] = cap_inj_list

  beg_bal_list = [0]
  for yr in range(forecast_period-1):
    beg_bal_list.append(beg_bal_list[yr] + df['change'][model_start + yr])
  df['beginning balance'] = beg_bal_list
  df['ending balance'] = df['beginning balance'] + df['change']
  
  return df['ending balance'], df['change']

share_bal, share_add = share_capital_calc()

def income_statement_calc():
  columns_is = ["revenue",
                "cost of sales",
                "gross profit",
                "selling & marketing expenses",
                "general & admin expenses",
                "EBITDA",
                "depreciation",
                "EBIT",
                "taxes",
                "net income"]
  df = pd.DataFrame(columns=columns_is, index=period)
  #df = pd.options.display.float_format = '${:,.0f}'.format
  df['revenue'] = df_revenue
  df['cost of sales'] = -df_cos
  df['gross profit'] = df['revenue'] + df['cost of sales']
  df['selling & marketing expenses'] = -df_sm
  df['general & admin expenses'] = -df_ga
  df['EBITDA'] = df['gross profit'] + df['selling & marketing expenses'] + df['general & admin expenses']
  df['depreciation'] = -depreciation_r
  df['EBIT'] = df['EBITDA'] + df['depreciation']
  df['taxes'] = df['EBIT'] * (-tax_rate)
  df['net income'] = df['EBIT'] + df['taxes']
  return df

df_is = income_statement_calc()
final_is = df_is.T
final_is_s = final_is.style.format('${:,.0f}')



def retained_calc():
  df = pd.DataFrame(columns=bs_columns, index=period)
  df['change'] = df_is['net income']

  beg_list = [0]
  for yr in range(forecast_period-1):
    beg_list.append(beg_list[yr] + df['change'][model_start + yr])
  df['beginning balance'] = beg_list
  df['ending balance'] = df['beginning balance'] + df['change']
  return df['ending balance']

retained_bal = retained_calc()


def cashflow_calc():
  columns_cf = ['EBITDA',
                'change in recievables',
                'change in inventory',
                'change in payables',
                'change in prepayments',
                'change in accrued expenses',
                'total change in WC',
                'taxes','operating cash flow',
                'capital expenditure',
                'free cash flow',
                'capital injection',
                'total change in cash',
                'beginning cash balance',
                'ending cash balance']
  df = pd.DataFrame(columns=columns_cf, index=period)
  df['EBITDA'] = df_is['EBITDA']
  df['change in recievables'] = -rec_change
  df['change in inventory'] = -inv_change
  df['change in payables'] = pay_change
  df['change in prepayments'] = -prep_change
  df['change in accrued expenses'] = accrued_change
  df['total change in WC'] = df['change in recievables'] + df['change in inventory'] + df['change in payables'] + df['change in prepayments'] + df['change in accrued expenses']
  df['taxes'] = df_is['taxes']
  df['operating cash flow'] = df['EBITDA'] + df['total change in WC'] + df['taxes']
  df['capital expenditure'] = -additions_r
  df['free cash flow'] = df['operating cash flow'] + df['capital expenditure']
  df['capital injection'] = share_add
  df['total change in cash'] = df['free cash flow'] + df['capital injection']

  beg_bal = [0]
  for yr in range(forecast_period-1):
    beg_bal.append(beg_bal[yr] + df['total change in cash'][model_start + yr])
  df['beginning cash balance'] = beg_bal
  df['ending cash balance'] = df['beginning cash balance'] + df['total change in cash']

  return df, df['ending cash balance']

df_cf, cash_bal = cashflow_calc()
final_cf = df_cf.T
final_cf_s = final_cf.style.format('${:,.0f}')


def balance_sheet_calc():
  columns_bs = ["cash balance",
                "accounts recievables",
                "inventory",
                "prepayments",
                "total current assets",
                "fixed assets",
                "total assets",
                "accounts payable",
                "accrued expenses",
                "total liabilities",
                "share capital",
                "retained earnings",
                "total equity",
                "total equity and liabilities",
                "balance check"]

  df = pd.DataFrame(columns=columns_bs, index=period)

  df['cash balance'] = cash_bal
  df['accounts recievables'] = rec_bal
  df['inventory'] = inv_bal
  df['prepayments'] = prep_bal
  df['total current assets'] = df['cash balance'] + df['accounts recievables'] + df['inventory'] + df['prepayments']
  df['fixed assets'] = NBV_r
  df['total assets'] = df['total current assets'] + df['fixed assets']
  df['accounts payable'] = pay_bal
  df['accrued expenses'] = accrued_bal
  df['total liabilities'] = df['accounts payable'] + df['accrued expenses']
  df['share capital'] = share_bal
  df['retained earnings'] = retained_bal
  df['total equity'] = df['share capital'] + df['retained earnings']
  df['total equity and liabilities'] = df['total equity'] + df['total liabilities']
  df['balance check'] = df['total assets'] - df['total equity and liabilities']
  
  return df

df_bs = balance_sheet_calc()
final_bs = df_bs.T
final_bs_s = final_bs.style.format('${:,.0f}')

###Valuation###

def fcf():
  df_fcf = pd.DataFrame([df_is['revenue'], df_cf['EBITDA'], df_cf['free cash flow']], index=['revenue', 'EBITDA', 'free cash flow'])
  return df_fcf
df_fcf = fcf()
fcf = df_cf['free cash flow']

df_fcf = df_fcf.style.format('${:,.0f}')

def terminal_val():
  cap_value = ((fcf[-1:].values[0] * (1 + terminal_growth)) / (cost_of_capital - terminal_growth))
  discrete_period = forecast_period
  pv_factor = 1 / ((1 + cost_of_capital) ** discrete_period)
  terminal_value = cap_value * pv_factor
  return terminal_value

terminal_value = terminal_val()

terminal_value_s = '${:,.0f}'.format(terminal_value)

def dcf():
  
  discount_factors = [(1 / (1 + cost_of_capital)) ** i for i in range (forecast_period)]
  discounted_cash = fcf * discount_factors
  dcf = sum(discounted_cash) + terminal_value
  return dcf

valuation = dcf()

valuation_s = '${:,.0f}'.format(valuation)


###Charts data###

rev_df = df_is[['revenue']]
ni_df = (df_is['net income'] / df_is['revenue']) * 100
cash_df = df_bs[['cash balance']]
fcf_df = df_cf[['free cash flow']]

###streamlit main body code###


main_select_menu = ['Select view','Dashboard', 'Operating model', 'Valuation']
op_model_menu = ['Income statement', 'Balance sheet', 'Cash flow statement']



st.title("EY Toy Financial Model")
st.subheader("by Khalid AlSaraj")


main_select = st.selectbox('Main menu', main_select_menu)


if main_select == 'Select view':
  st.subheader("Disclaimer")
  st.write("This Toy financial model and valuation has been developed for EY to showcase the development of financial models using Python code rather than typical Excel based models. By Accessing the application, you agree that you will not use it for other purposes without prior consent ")



elif main_select == 'Dashboard':
  st.subheader("Dashboard")

  col1, col2 = st.beta_columns(2)
  col3, col4 = st.beta_columns(2)

  with col1:
    st.header("Revenue")
    st.bar_chart(rev_df)

  with col2:
    st.header("Net Income margin %")
    st.bar_chart(ni_df)

  with col3:
    st.header("Cash balance")
    st.bar_chart(cash_df)

  with col4:
    st.header("Free cash flows")
    st.bar_chart(fcf_df)


elif main_select == 'Operating model':
  op_model = st.selectbox('Financial statement', op_model_menu)

  if op_model == 'Income statement':
    st.subheader("Income statement")
    st.table(final_is_s)

  elif op_model == 'Balance sheet':
    st.subheader("Balance sheet")
    st.table(final_bs_s)

  elif op_model == 'Cash flow statement':
    st.subheader("Cash flow statement")
    st.table(final_cf_s)

elif main_select == 'Valuation':
  st.subheader("Free cash clows")
  st.table(df_fcf)
  st.subheader('Termianl value')
  st.subheader(terminal_value_s)
  st.subheader('Business valuation')
  st.subheader(valuation_s)
  

