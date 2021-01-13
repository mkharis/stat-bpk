import streamlit as st
import home, page1, page2, page3, page4, page5, page6

st.sidebar.write('STAT-BPK')

menu = ('Home', 'Descriptive and Exploration', 'Comparable Dynamic-Graph', 'Prediction Models', 'Sentiment Analysis', 'Topic Modelling', 'Social Network Analysis')

halaman = st.sidebar.radio('Menu', menu)

if halaman == menu[0]:
    home.show()
if halaman == menu[1]:
    page1.show(menu[1])
if halaman == menu[2]:
    page2.show(menu[2])
if halaman == menu[3]:
    page3.show(menu[3])
if halaman == menu[4]:
    page4.show(menu[4])
if halaman == menu[5]:
    page5.show(menu[5])
if halaman == menu[6]:
    page6.show(menu[6])
