import streamlit as st 
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd




def layout():
    # inset start
    st.set_page_config(page_title = "This is a Multipage WebApp") 
    st.sidebar.success("What do you want to do") 
    # inset stop
    st.markdown("# The magic travel agent")
   
    st.markdown("")
    
    img_path = Path(__file__).parents[0] / "Page1figure.jpeg"
    img=Image.open(img_path)
    st.image(img, caption='Traveling by YBDM')
    st.markdown("This is an example of the traveling agent ...")
    


    read_css()


def read_css():
    css_path = Path(__file__).parents[0] / "style.css"

    with open(css_path) as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    layout()