import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime
from load_data import get_data

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
fty =['NT1','NT2']
nha_may = st.sidebar.selectbox("Chọn nhà máy",options=fty,index=fty.index(st.session_state.factory))
reports = ['Tổng hợp','Công nhân Cắt','Công nhân may','Công nhân QC1','Công nhân Là','Công nhân QC2','Công nhân đóng gói','Công nhân NDC','Công nhân phụ','Quản lý']
bao_cao = st.sidebar.selectbox("Chọn báo cáo",options= reports,index=0)

st.markdown(f'<h1 class="centered-title">BÁO CÁO THƯỞNG NĂNG SUẤT ({bao_cao})</h1>', unsafe_allow_html=True)
if bao_cao == 'Công nhân may':
    df_cn_may = get_data(DB='INCENTIVE',query=f"SELECT * FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_CN_MAY WHERE NHA_MAY = '{nha_may}' ORDER BY CHUYEN")
    df_cn_may['XUONG'] = df_cn_may['CHUYEN'].str[0:1] + 'P0' + df_cn_may['CHUYEN'].str[1:2]
    df_cn_may['SAH'] = df_cn_may['EFF_TB']*df_cn_may['TONG_TGLV']
    df_cn_may_selected = df_cn_may.query('NHA_MAY == @nha_may')
    df_cn_may_selected = df_cn_may_selected[~df_cn_may_selected['CHUYEN'].str.contains('TNC')]
    xuong = st.sidebar.multiselect("Chọn xưởng",options=df_cn_may_selected['XUONG'].unique(),default=df_cn_may_selected['XUONG'].unique())
    df_cn_may_selected= df_cn_may_selected[df_cn_may_selected['XUONG'].isin(xuong)]
    ###
    cols = st.columns([1,1,12])
    with cols[0]:
        nam_opt = df_cn_may_selected['NAM'].sort_values(ascending=False).unique()
        nam = st.selectbox("Chọn năm",options=nam_opt)
    with cols[1]:   
        df_cn_may_selected = df_cn_may_selected.query('NAM == @nam')
        thang_opt = df_cn_may_selected['THANG'].sort_values(ascending=False).unique()
        thang = st.selectbox("Chọn tháng",options=thang_opt)
    with cols[2]:  
        df_cn_may_selected = df_cn_may_selected.query('NAM == @nam and THANG == @thang')
        chuyen = st.multiselect("Chọn chuyền",options= df_cn_may_selected['CHUYEN'].unique(),default=df_cn_may_selected['CHUYEN'].unique())
    df_cn_may_selected = df_cn_may_selected[df_cn_may_selected['CHUYEN'].isin(chuyen)]
    df_cn_may_selected['Hiệu suất'] = df_cn_may_selected['EFF_TB'].apply(lambda x: f"{x:.0%}")
    df_cn_may_selected['Tiền thưởng'] = df_cn_may_selected['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
    ###
    so_ngay_min = df_cn_may_selected['SO_NGAY'].min()
    so_ngay_max = df_cn_may_selected['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",min_value= so_ngay_min,max_value=so_ngay_max,value=[so_ngay_min,so_ngay_max])
    df_cn_may_selected = df_cn_may_selected.query('SO_NGAY >= @so_ngay_from and SO_NGAY <=@so_ngay_to')
    ###
    cols = st.columns([1,4,2])
    with cols[0]:
        so_cn = df_cn_may_selected['MST'].count()
        Eff_tb = df_cn_may_selected['SAH'].sum()/df_cn_may_selected['TONG_TGLV'].sum()
        Incentive_tb = df_cn_may_selected['TONG_THUONG'].mean()
        so_ngay_tb = df_cn_may_selected['SO_NGAY'].mean()
        st.info("Tổng quan")
        st.metric(label="Số ngày làm việc trung bình",value= f"{so_ngay_tb:,.0f}")
        st.metric(label="Số công nhân",value= f"{so_cn:,.0f}")
        st.metric(label="Hiệu suất trung bình",value= f"{Eff_tb:,.0%}")
        st.metric(label="Tiền thưởng trung bình",value= f"{Incentive_tb:,.0f}")
    with cols[1]:   
        SCP_order = ['U','N','S','M']
        fig = px.scatter(
            df_cn_may_selected,
            x= "EFF_TB",
            y= "TONG_THUONG",
            color= "SCP",
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            },
            size= "TONG_TGLV",
            hover_data={
                'MST':True,
                'HO_TEN' : True,
                'CHUYEN' : True,
                'EFF_TB' : False,
                'TONG_THUONG' : False,
                'Hiệu suất' : True,
                'Tiền thưởng' : True,
                'SCP' : False
            },
            category_orders= {'SCP' : SCP_order},
            # symbol='XUONG',
            size_max= 10
        )
        fig.update_layout(
            xaxis_title = 'Hiệu suất trung bình',
            yaxis_title = "Tổng thưởng (VNĐ)",
            title = "Phân bổ tiền thưởng theo hiệu suất"
        )
        fig.update_xaxes(
            tickformat = '.0%',
        )
        fig.update_traces(
            marker = dict(line = dict(width = 1,color = 'white')),
        )
        st.plotly_chart(fig,use_container_width=True)
        # st.dataframe(df_cn_may_selected)
    with cols[2]:
        SCP_order = ['U','N','S','M']
        fig = px.pie(
            df_cn_may_selected[df_cn_may_selected['SCP'].isin(SCP_order)],
            color="SCP",
            names="SCP",
            category_orders={"SCP" : SCP_order},
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            }
        )
        fig.update_layout(
            title = "Tỉ lệ công nhân theo SCP"
        )
        fig.update_traces(
            textinfo = 'percent+label',
            textposition = 'inside',
            textfont = dict(size = 14)
        )
        st.plotly_chart(fig,use_container_width=True)
    cols = st.columns(3)
    with cols[0]:
        fig = px.histogram(
            df_cn_may_selected,
            x= "EFF_TB",
            text_auto= True
        )
        fig.update_layout(
            title = "Phân bổ công nhân theo hiệu suất",
            xaxis_title = "Hiệu suất",
            yaxis_title = "Số công nhân"
        )
        fig.update_xaxes(
            tickformat = ".0%"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        st.plotly_chart(fig,use_container_width=True)
    with cols[1]:
        SCP_order = ['U','N','S','M']
        fig = px.box(
            df_cn_may_selected,
            x= "SCP",
            y= "TONG_THUONG",
            color="SCP",
            category_orders= {"SCP" : SCP_order},
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            }
        )
        fig.update_layout(
            title = "Phân bổ tiền thưởng theo bậc kỹ năng",
            yaxis_title = "Tiền thưởng"
        )
        st.plotly_chart(fig,use_container_width=True)
    with cols[2]:
        df_cn_may_selected_SCP = df_cn_may_selected.groupby(by="SCP").agg({"TONG_THUONG" : 'mean'}).reset_index()
        df_cn_may_selected_SCP['Tổng thưởng'] = df_cn_may_selected_SCP['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
        SCP_order = ['U','N','S','M']
        fig = px.bar(
            df_cn_may_selected_SCP,
            x='SCP',
            y= "TONG_THUONG",
            text= 'Tổng thưởng',
            color="SCP",
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            },
            category_orders={"SCP" : SCP_order}
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = 'Tiền thưởng trung bình theo bậc kỹ năng',
            yaxis_title = 'Tiền thưởng'
        )
        st.plotly_chart(fig,use_container_width=True)
if bao_cao == 'Tổng hợp':
    df_nhom_cat = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY,N'Cắt' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_CAT WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_may = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,'May' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_CN_MAY WHERE NHA_MAY = '{nha_may}' 
                           """)
    
    df_nhom_qc1 = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'QC1' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC1 WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_la = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'Là' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_LA WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_qc2 = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'QC2' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC2 WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_hoan_thien = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'Hoàn thiện' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_DONG_GOI WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_NDC = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'NDC' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_NDC WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_phu = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'CN Phụ' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_PHU WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df_nhom_quan_ly = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'Quản lý' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_QUAN_LY WHERE NHA_MAY = '{nha_may}'
                           """)
    
    df = pd.concat([df_nhom_cat,df_nhom_may,df_nhom_qc1,df_nhom_la,df_nhom_qc2,df_nhom_hoan_thien,df_nhom_NDC,df_nhom_phu,df_nhom_quan_ly])
    df['XUONG'] = df['CHUYEN'].apply(lambda x: (x[:1] + 'NDC') if 'NDC' in x \
        else (x[:1] + 'TNC') if 'TNC' in x \
        else (x[:1] + 'P0' + x[1:2]))
    # xuong = df['XUONG'].unique()
    # sel_xuong = st.sidebar.multiselect("Chọn xưởng",options=xuong,default=xuong)
    # df = df[df['XUONG'].isin(sel_xuong)]
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    thang = df[df['NAM']==sel_nam]['THANG'].sort_values(ascending = False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    so_ngay_min = df[(df['NAM']==sel_nam) & (df['THANG']==sel_thang)]['SO_NGAY'].min()
    so_ngay_max = df[(df['NAM']==sel_nam) & (df['THANG']==sel_thang)]['SO_NGAY'].max()
    sel_so_ngay_min,sel_so_ngay_max = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df = df.query("THANG == @sel_thang and NAM == @sel_nam and SO_NGAY >= @sel_so_ngay_min and SO_NGAY <= @sel_so_ngay_max")
    # st.dataframe(df)
    # st.write(df.shape)
    cols = st.columns(2)
    with cols[0]:
        tong_thuong = df['TONG_THUONG'].sum()
        st.metric("Tổng tiền thưởng Incentive toàn nhà máy",value=f"{tong_thuong:,.0f} VNĐ")
        ###
        df_tong_thuong = df.groupby(by=['NHOM']).agg({'TONG_THUONG' : 'sum'}).reset_index()
        df_tong_thuong['Tổng tiền thưởng'] = df_tong_thuong['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")
        category_orders={'NHOM' : ['Cắt','May','QC1','Là','QC2','Hoàn thiện','NDC','CN Phụ','Quản lý']}
        fig = px.bar(
            df_tong_thuong,
            y='NHOM',
            x='TONG_THUONG',
            text= 'Tổng tiền thưởng',
            category_orders=category_orders
        )
        fig.update_layout(
            title = 'Tổng tiền thưởng theo từng nhóm',
            xaxis_title = 'Nhóm',
            yaxis_title = 'Tổng tiền thưởng'
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_tien = df_tong_thuong['TONG_THUONG'].max()*1.2
        fig.update_xaxes(
            range = [0,max_tien]
        )
        st.plotly_chart(fig,use_container_width=True)
    with cols[1]:
        tbthuong = df['TONG_THUONG'].mean()
        st.metric("Trung bình tiền thưởng 1 công nhân",value=f"{tbthuong:,.0f} VNĐ")
        ###        
        df_tb_thuong = df.groupby(by=['NHOM']).agg({'TONG_THUONG' : 'mean'}).reset_index()
        df_tb_thuong['Tổng tiền thưởng'] = df_tb_thuong['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
        category_orders={'NHOM' : ['Cắt','May','QC1','Là','QC2','Hoàn thiện','NDC','CN Phụ','Quản lý']}
        fig = px.bar(
            df_tb_thuong,
            y='NHOM',
            x='TONG_THUONG',
            # color='XUONG',
            # barmode='group',
            text= 'Tổng tiền thưởng',
            category_orders=category_orders
        )
        fig.update_layout(
            title = 'Trung bình tiền thưởng 1 công nhân theo từng nhóm',
            xaxis_title = 'Nhóm',
            yaxis_title = 'Trung bình tiền thưởng'
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_tien_tb = df_tb_thuong['TONG_THUONG'].max()*1.2
        fig.update_xaxes(
            range = [0,max_tien_tb]
        )
        st.plotly_chart(fig,use_container_width=True)
    cols = st.columns([1,2])
    with cols[0]:
        df_xuong_nhom = df.groupby(by = ['XUONG','NHOM']).agg({'TONG_THUONG' : 'sum'}).reset_index()
        # st.write(df_xuong_nhom)
        fig = px.sunburst(
            df_xuong_nhom,
            path= ['XUONG','NHOM'],
            color='NHOM',
            values='TONG_THUONG',
            title= 'Phân bổ tổng tiền thưởng theo xưởng, nhóm'
        )
        
        st.plotly_chart(fig,use_container_width=True)
    with cols[1]:
        df_xuong_nhom_tb = df.groupby(by = ['XUONG','NHOM']).agg({'TONG_THUONG' : 'mean'}).reset_index()
        # st.write(df_xuong_nhom_tb)
        fig = px.bar(
            df_xuong_nhom_tb,
            x= 'NHOM',
            y='TONG_THUONG',
            color='XUONG',
            barmode='group',
            category_orders=category_orders    
        )
        fig.update_layout(
            title= 'Trung bình tiền thưởng theo xưởng, nhóm',
            xaxis_title = 'Nhóm',
            yaxis_title = 'Trung bình tiền thưởng',
            bargap=0.1
            )
        
        st.plotly_chart(fig,use_container_width=True)
        