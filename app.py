import pandas as pd 
import os
import streamlit as st 
import matplotlib.pyplot as plt 
from itertools import combinations
from collections import Counter
from PIL import Image



image = Image.open('kpi.jpg')

st.image(image, use_column_width=True)

st.header('Retail Analysis to measure business KPI')
st.write("""
***
""")
st.subheader('Merge the 12 months of sales data into a single CSV file')

files = [file for file in os.listdir('./Sales_Data')]

st.markdown("""

""")

all_months_data = pd.DataFrame()

for file in files:
    df = pd.read_csv("./Sales_Data/"+file)
    all_months_data = pd.concat([all_months_data, df])

all_months_data.to_csv("all_data.csv", index=False)

all_data = pd.read_csv("all_data.csv")    
st.dataframe(all_data)

st.write("""
***
""")

st.subheader('Cleaning the data')

### Display and Drop rows with NAN
st.write("""
***Display rows with NAN***
""")
df_nan = all_data[all_data.isna().any(axis=1)]
st.dataframe(df_nan)
st.write("""
***
""")

all_data = all_data.dropna(how='all')   # To drop the rows with NAN

### find 'Order Date' in 'Order Date' and delete it.
st.write("""
***Find and delete all rows in 'Order Date' with 'Order Date' instead of a real date ***
""")
contains_or = all_data[all_data['Order Date'].str[0:2] == 'Or']
st.dataframe(contains_or)

### To delete the 'Or' 
all_data = all_data[all_data['Order Date'].str[0:2] != 'Or']

### Convert columns to the correct type
all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])   # converts to interger
all_data['Price Each'] = pd.to_numeric(all_data['Price Each'])   # converts to float

st.subheader('Augument the data with additional columns for Month, Sales and City ')

### Add a month column
all_data['Month'] = all_data['Order Date'].str[0:2]
all_data['Month'] = all_data['Month'].astype('int32')

### Add a sales column
all_data['Sales'] = all_data['Quantity Ordered'] * all_data['Price Each']

### Add a city column using the .apply() 
all_data['City'] = all_data['Purchase Address'].apply(lambda x: x.split(',')[1] + ' (' + x.split(',')[2].split(' ')[1] + ')')

st.dataframe(all_data)

st.write("""
***
""")
st.header('Answering business questions with our data')

st.subheader('Question 1: What was the best month for sales? How much was earned that month?')
best_month = all_data.groupby('Month').sum()
st.dataframe(best_month)

#### Bar chart to visualize the best month
st.set_option('deprecation.showPyplotGlobalUse', False)
months = range(1,13)
plt.bar(months, best_month['Sales'])
plt.xticks(months)
plt.ylabel('Sales in USD ($)')
plt.xlabel('Month Number')
st.pyplot()

st.write("""
***The best month for sales was December. A total of $4,613,443.34 was earned in December.***
""")
st.write("""
***
""")
st.subheader('Question 2: What city has the highest number of sales?')
best_city = all_data.groupby('City').sum()
st.dataframe(best_city)

#### Bar chart to visualize the city with highest sales
st.set_option('deprecation.showPyplotGlobalUse', False)
cities = [city for city, df in all_data.groupby('City')]
plt.bar(cities, best_city['Sales'])
plt.xticks(cities, rotation='vertical', size=8)
plt.ylabel('Sales in USD ($)')
plt.xlabel('City Name')
st.pyplot()

st.write("""
***The city with the highest number of sales is San Francisco with a total of $8,262,203.91 in sales.***
""")
st.write("""
***
""")
st.subheader('Question 3: What time should we display advertisements to maximize the likelihood of customers buying the products?')
all_data['Order Date'] = pd.to_datetime(all_data['Order Date'])

all_data['Hour'] = all_data['Order Date'].dt.hour
all_data['Minute'] = all_data['Order Date'].dt.minute

hours = [hour for hour, df in all_data.groupby('Hour')]
plt.plot(hours, all_data.groupby(['Hour']).count())
plt.xlabel('Hour')
plt.ylabel('Number of Orders')
plt.xticks(hours)
plt.grid(color='b', linestyle='-', linewidth=0.3)
st.pyplot()
st.write("""
***Peak sales happened around 12:00pm and 7:00pm. Those are the best times to display the advertisements.***
""")
st.write("""
***
""")
st.subheader('Question 4: What products are most often sold together?')
df = all_data[all_data['Order ID'].duplicated(keep=False)] # Checks for all the rows on Order ID to find out which ones are duplicated.
### Group the products with the same Order ID together
df['Grouped'] = df.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))
df = df[['Order ID', 'Grouped']].drop_duplicates()
st.dataframe(df)

st.write("""Counting Unique Products""")
count = Counter()
for row in df['Grouped']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))

for key, value in count.most_common(13):
    st.write(key, value)

st.write("""
    ***The products that are mostly sold together are iPhones and Lightning Charging Cable. 
    It was sold 1005 times.***
""")

st.write("""
***
""")
st.subheader('Question 5: What product sold the most? Why did it sell the most?')
product_group = all_data.groupby('Product')
quantity_ordered = product_group.sum()['Quantity Ordered']
st.dataframe(quantity_ordered)

products = [product for product, df in product_group]

plt.bar(products, quantity_ordered)
plt.ylabel('Quantity Ordered')
plt.xlabel('Product')
plt.xticks(products, rotation='vertical', size=8)
st.pyplot()
st.write("""
    ***The product that sold the most was AAA Batteries (4-pack).***
""")

st.write("""
    #### Comparing the prices of the products with the quantity ordered.
""")
prices = all_data.groupby('Product').mean()['Price Each']
st.dataframe(prices)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.bar(products, quantity_ordered, color='g')
ax2.plot(products, prices, 'b-')

ax1.set_xlabel('Product Name')
ax1.set_ylabel('Quantity Ordered', color='g')
ax2.set_ylabel('Price ($)', color='b')
ax1.set_xticklabels(products, rotation='vertical', size=8)
st.pyplot()

st.write("""
    ***From the graph, it shows that an increase in price leads to a decrease in the quantity ordered and vice versa.***
""")







