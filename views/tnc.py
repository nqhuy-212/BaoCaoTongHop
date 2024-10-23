import streamlit as st 

st.logo("logo_white.png",size= 'large')
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 200 px;
        color: 'rgb(255,255,255)';
        font-size : 48px;
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(f'<h1 class="centered-title">BÁO CÁO HIỆU SUẤT CÔNG NHÂN TNC</h1>', unsafe_allow_html=True)