import streamlit as st
import pandas as pd
from datetime import datetime

st.header("Store Performance Analysis")

st.subheader("Upload files")

wzn_file=None
wzn_file=st.file_uploader("Upload Walzon report here",type=["xlsx","csv"])
st.caption("""The following fields in the excel or csv file are expected:\
	"Order item id","Amz order id","Asin","Order date","Latest ship date",\
	"Orderfulfillment status","Market item cost","Quantity ordered"
											""")



if wzn_file:

	# try:
	wzn=pd.read_excel(wzn_file,usecols=["Order item id",
										"Amz order id",
										"Asin",
										"Order date",
										"Latest ship date",
										"Orderfulfillment status",
										"Market item cost",
										"Quantity ordered"],
					dtype={"Order item id":"string[pyarrow]",
					"Amz order id": "string[pyarrow]",
					"Asin":"string[pyarrow]",
					"Order date":"string[pyarrow]",
					"Latest ship date":"string[pyarrow]",
					"Orderfulfillment status":"string[pyarrow]",
					"Market item cost":"float",
					"Quantity ordered":"float"
					})
	wzn["order_cost"]=wzn["Market item cost"]*wzn["Quantity ordered"]


	wzn.dropna(subset=["Amz order id"],inplace=True)
	date_cols=["Order date","Latest ship date"]
	for col in date_cols:
		wzn[col]=wzn[col].str.extract("([0-9]+),*")
		wzn[col]=wzn[col].astype("int64").apply(lambda x: datetime.fromtimestamp(x)).dt.strftime("%Y-%m-%d")

	wzn.sort_values(by="Order date",ignore_index=True,inplace=True)
	wzn.columns=wzn.columns.str.replace(" ","_").str.lower()

	col_name='order_date'
	col_idx=wzn.columns.tolist().index(col_name)
	first_order_date=wzn.iloc[-1,col_idx]
	last_order_date=wzn.iloc[0,col_idx]
	col1,col2 = st.columns(2)
	col1.markdown(f"**walzon first_order_date:** {first_order_date}")
	col2.write(f"**walzon last_order_date:** {last_order_date}")

	azn_files=None
	azn_files=st.file_uploader("Upload Amazon report here",type=["xlsx","csv"],
													accept_multiple_files=True)


	st.subheader("Walzon shipped orders")
	wzn_shipped=wzn.query("orderfulfillment_status=='Shipped'")
	wzn_shipped.set_index("order_date",inplace=True)




	st.dataframe(wzn_shipped)
	st.markdown("**Chart 1. Payments for orders shipped**")
	st.bar_chart(data=wzn_shipped[['order_cost']])



	capital_invested=st.text_input("Enter invested capital amount",value='15000')
	capital_invested=int(capital_invested)

	wzn_shipped["cum_cash_out"]=wzn_shipped['order_cost'].cumsum()
	wzn_shipped["cash_balance"]=capital_invested-wzn_shipped["cum_cash_out"]

	st.dataframe(wzn_shipped)
	st.markdown("**Chart 2. Walzon cash balance**")
	st.line_chart(data=wzn_shipped[['cash_balance']])
	st.caption("""This chart includes only amounts paid for order purchases\n
		Amounts received from Amazon and Funds returned will be included in the next release""")

	# load and pre-process amazon reports

	azn=pd.DataFrame()
	for fn in azn_files:
	  azn=pd.concat([azn,pd.read_csv(fn)])

	azn.drop_duplicates(subset=['Order ID'],inplace=True)
	azn.Date=pd.to_datetime(azn.Date)
	azn.sort_values(by='Date',inplace=True,ascending=False,ignore_index=True)
	azn.columns=azn.columns.str.replace(" ","_").str.lower()
	azn['date']=azn.date.dt.strftime("%Y-%m-%d")
	azn.rename(columns={"order_id":'amz_order_id'},inplace=True)

	st.dataframe(azn)

	st.subheader("Profit from Operations")

	df=azn.merge(wzn,on="amz_order_id",how="left")
	df.rename(columns={"Total (USD)":"net_amz_payment",
	                   "Transaction type":"transaction_type",
	                   "Market item cost":"market_item_cost"},inplace=True)

	
	df_result=df.query("transaction_type=='Order Payment'")
	df_result['profit']=df_result['total_(usd)']-df_result['order_cost']
	st.markdown(f"**Profit from transactions:** {df_result['profit'].sum()}")
	st.markdown("Table 4. Walzon file merge with Amazon reports")
	st.dataframe(df_result)
	st.caption("""
		Table 4 includes those transaction only which were included by Amazon into uploaded reports\
		 and for which Order Payments were made. <NA> means that transactions included into Amazon\
		 report were not included into Walzon report. 
		""")

	# except:
	# 	st.write("failed to upload; please check that the file is excel or csv and if all required columns are in the file ")
