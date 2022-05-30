import streamlit as st

st.header("Store Performance Analysis")

st.subheader("Upload files")

wzn_file=None
wzn_file=st.file_uploader("Upload Walzon report here",type=["xlsx","csv"])
st.caption("""The following fields in the excel or csv file are expected:\
	"Order item id","Amz order id","Asin","Order date","Latest ship date",\
	"Orderfulfillment status","Market item cost","Quantity ordered"
											""")

azn_files=None
azn_files=st.file_uploader("Upload Amazon report here",type=["xlsx","csv"],
	accept_multiple_files=True)


if wzn_file:

	try:
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

	except:
		st.write("failed to upload; please check that the file is excel or csv and if all required columns are in the file ")

	wzn.dropna(subset=["Amz order id"],inplace=True)
	date_cols=["Order date","Latest ship date"]
	for col in date_cols:
		wzn[col]=wzn[col].str.extract("([0-9]+),*")
		wzn[col]=wzn[col].astype("int64").apply(lambda x: datetime.fromtimestamp(x)).dt.strftime("%Y-%m-%d")

	wzn.sort_values(by="Order date",ignore_index=True,inplace=True)
	wzn.columns=wzn.columns.str.replace(" ","_").str.lower()
	#st.dataframe(wzn)


	st.subheader("Walzon shipped orders")
	wzn_shipped=wzn.query("orderfulfillment_status=='Shipped'")
	wzn_shipped.set_index("order_date",inplace=True)


	st.dataframe(wzn_shipped)
	st.markdown("**Chart 1. Payments for orders shipped**")
	st.bar_chart(data=wzn_shipped[['order_cost']])
			