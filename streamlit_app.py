import streamlit as st
import chatgpt
import time

st.title("RealEstateGPT")
num_records = 10

st.write('This works best for one zip code, but you can try more.')
st.write('Example 1: Give me 1 zip code that is near a big national park and is a big city or town.')
st.write('Example 2: Give me 1 zip code that is in a historic city and tell me about the city.')
st.write('Example 3: Give me 5 zip codes that are near a big national park.')

streamlit_analytics.start_tracking()
input = st.text_input("Please enter a GPT input:")
streamlit_analytics.stop_tracking()
get_res = chatgpt.get_response(input)
zipcode = chatgpt.get_zip_code(get_res)
response = chatgpt.request_zillow_page(zipcode)
coords = chatgpt.parse_coords(response)

zillow_records = chatgpt.pull_zillow_records(coords)
zillow_links = chatgpt.return_df(zillow_records)

st.write(chatgpt.get_assistant_msg(get_res))
st.write(zillow_links)






