import streamlit as st

st.header("Store Performance Analysis")

st.subheader("Upload files")

wzn_file=None
wzn_file=st.file_uploader("Upload Walzon report here",type=["xlsx","csv"])
st.caption("""The following fields in the excel or csv file are expected:\
	"Order item id","Amz order id","Asin","Order date","Latest ship date",\
	"Orderfulfillment status","Market item cost","Quantity ordered"
											""")