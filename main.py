# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 04:21:59 2023

@author: HRGiri
"""
import streamlit as st
import pandas as pd
import numpy as np
# You can access the image with PIL.Image for example
import io
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

API_URL = "https://xdwvg9no7pefghrn.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
	"Accept": "image/png",
	"Authorization": "Bearer VknySbLLTUjbxXAXCjyfaFIPwUTCeRXbFSOjwRiCxsxFyhbnGjSFalPKrpvvDAaPVzWEevPljilLVDBiTzfIbWFdxOkYJxnOPoHhkkVGzAknaOulWggusSFewzpqsNWM",
	"Content-Type": "application/json"
}

# Fetch the generated image
@st.cache_data     # Stored as cache for same query
def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.content

# Layout structure
col_widths = {
        1: [[1]],
        2: [[1,1]],
        3: [[1,1,1]],
        4: [[1,1],[1,1]],
        5: [[1,1],[1,2,1],[1,1]],
        6: [[1,1,1],[1,1,1]],
        7: [[1,4,4,1],[1,1,1],[1,4,4,1]],
        8: [[1,1,1],[1,4,4,1],[1,1,1]],
        9: [[1,1,1],[1,1,1],[1,1,1]],
        10: [[1,6,6,6,1],[1,1,1,1],[1,6,6,6,1]],
        }

st.title('Comic Creator')

num_panels = st.number_input("How many panels do you want in your comic strip?", value=1, min_value=1, max_value=10)
st.write('Building a comic strip of ', num_panels, ' panels')


# Create as many text_input fields as num_panels
inputs = [''] * num_panels
for num in range(num_panels):
    inputs[num] = st.text_input(f"Panel {num +1}", key=f"input{num}")    
    if inputs[num] != '':
        inputs[num] += ", in comic style"
    print(inputs[num])

# Fetch images from texts in the text_inputs and store in a list
images = [None] * num_panels
for num in range(num_panels):
    if inputs[num] != "":
        with st.spinner('Wait for it...'):
            image_bytes = query({
             	"inputs": inputs[num],
            })            
            images[num] = Image.open(io.BytesIO(image_bytes))            

if None not in images:
    st.write("Here's your comic strip...")

# Display the images according to the layout
with st.container():
    index = 0
    for r, row in enumerate(col_widths[num_panels]):
        cols = st.columns(row)
        contains_space = sum(row) > len(row)
        for c, col in enumerate(cols):
            with col:
                if contains_space and row[c] == 1:
                    continue    # Empty for filling out space
                if images[index] is not None:
                    st.image(images[index])
                    index += 1

if None not in images:
    # Construct a single image for download
    row_cols = col_widths[num_panels]
    num_rows = len(row_cols)
    num_cols = min([len(cols) for cols in row_cols])
    vpadding = 20
    hpadding = 20
    height = num_rows * 512 + (num_rows + 1) * vpadding
    width = num_cols * 512 + (num_cols + 1) * hpadding
    full_image = Image.new('RGB', (width, height), color=(255,255,255))
    
    index = 0
    for r, row in enumerate(col_widths[num_panels]):         
        contains_space = sum(row) > len(row)
        space = 1 / max(row)
        upper = vpadding + r * (512 + vpadding)
        lower = upper + 512
        left = hpadding
        for c, col in enumerate(row):  
            if contains_space and row[c] == 1:                
                right = left + 256                
                left = right + hpadding
                continue
            if images[index] is not None:
                right = left + 512                                
                full_image.paste(images[index], (left, upper, right, lower))                
                index += 1
                left = right + hpadding
    # Add title
    # title = st.text_input(f"Add a title", key=f"title")
    
    fp = io.BytesIO()
    full_image.save(fp, 'jpeg')
    data = fp.getvalue()
    # if title != '':
    #     new_image = Image.new('RGB', (width, height + 100), color=(255,255,255))
    #     new_image.paste(full_image,(0,100))
    #     # Call draw Method to add 2D graphics in an image
    #     I1 = ImageDraw.Draw(new_image)
    #     # Custom font style and font size
    #     # myFont = ImageFont.truetype('serif', 65)
    #     # Add Text to an image
    #     I1.text((30,30), title, fill=(0, 0, 0))
    #     fp = io.BytesIO()
    #     new_image.save(fp, 'jpeg')
    #     data = fp.getvalue()
    
    # Finally download the file
    dowload = st.download_button(
        label="Download your comic",
        data=data,
        file_name="comic.jpg",
        mime="image/jpeg"
    )
