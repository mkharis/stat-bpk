import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import db
from pmdarima.arima import auto_arima

def show(title):
    st.title(title)

    lk = db.get_lk()
    lk_df = pd.DataFrame(lk, columns=['id', 'lk', 'bagian', 'tingkat'])

    masalah = db.get_masalah()
    masalah_df = pd.DataFrame(masalah, columns=['id', 'masalah', 'jenis', 'tingkat'])

    masalah_dengan_nilai = db.get_masalah_dengan_nilai()
    masalah_dengan_nilai_df = pd.DataFrame(masalah_dengan_nilai, columns=['id', 'masalah', 'jenis', 'tingkat'])

    st.header('Institution and Problem')

    with st.beta_expander('Choose Institution'):
        option_tingkat = st.selectbox('Choose Institution Level', lk_df['tingkat'].unique())
        option_lembaga = st.selectbox('Choose Institution', lk_df.loc[lk_df['tingkat'] == option_tingkat, 'lk'].tolist())
        id_lembaga = lk_df.loc[(lk_df['tingkat'] == option_tingkat) & (lk_df['lk'] == option_lembaga), 'id'].tolist()[0]

    with st.beta_expander('Choose Problem'):
        option_utama = st.selectbox('Choose Main Problem', ('Permasalahan Kelemahan Sistem Pengendalian Intern', 'Permasalahan Ketidakpatuhan terhadap Ketentuan Peraturan Perundang-undangan'))
        if option_utama == 'Permasalahan Kelemahan Sistem Pengendalian Intern':
            option_jenis = st.selectbox('Choose Kind of Problem', masalah_df.loc[masalah_df['tingkat'] == option_tingkat, 'jenis'].unique())
            option_masalah = st.selectbox('Choose Problem', masalah_df.loc[(masalah_df['tingkat'] == option_tingkat) & (masalah_df['jenis'] == option_jenis), 'masalah'].tolist())
            id_masalah = masalah_df.loc[(masalah_df['tingkat'] == option_tingkat) & (masalah_df['jenis'] == option_jenis) & (masalah_df['masalah'] == option_masalah), 'id'].tolist()[0]
        else:
            option_jenis = st.selectbox('Choose Kind of Problem', masalah_dengan_nilai_df.loc[masalah_dengan_nilai_df['tingkat'] == option_tingkat, 'jenis'].unique())
            option_masalah = st.selectbox('Choose Problem', masalah_dengan_nilai_df.loc[(masalah_dengan_nilai_df['tingkat'] == option_tingkat) & (masalah_dengan_nilai_df['jenis'] == option_jenis), 'masalah'].tolist())
            id_masalah = masalah_dengan_nilai_df.loc[(masalah_dengan_nilai_df['tingkat'] == option_tingkat) & (masalah_dengan_nilai_df['jenis'] == option_jenis) & (masalah_dengan_nilai_df['masalah'] == option_masalah), 'id'].tolist()[0]

    if option_utama == 'Permasalahan Kelemahan Sistem Pengendalian Intern':
        temuan = db.get_temuan(str(id_lembaga), str(id_masalah))
        temuan_df = pd.DataFrame(temuan, columns=['jumlah', 'tahun', 'semester'])
        temuan_df.loc[:, 'data'] = 'Truth'

        st.header('Prediction')

        col1, col2 = st.beta_columns(2)

        with col1:
            slider_prediksi = st.slider('Number of Predictions', 1, 10, 1, key='prediksi')

        with col2:
            slider_ma = st.slider('Number of Moving Averages', 2, len(temuan_df.index), 2, key='ma')

        for i in range(slider_prediksi):
            tahun_before = temuan_df.iloc[-1, temuan_df.columns.tolist().index('tahun')]
            semester_before = temuan_df.iloc[-1, temuan_df.columns.tolist().index('semester')]
            if semester_before == 1:
                tahun = tahun_before
                semester = 2
            else:
                tahun = tahun_before + 1
                semester = 1
            temuan_df = temuan_df.append(pd.DataFrame({
                'jumlah': [np.nan],
                'tahun': [tahun],
                'semester': [semester],
                'data': ['Prediction']
            }), ignore_index=True)

        temuan_model = auto_arima(temuan_df.loc[~temuan_df['jumlah'].isna(), 'jumlah'], start_p=0, start_q=0, max_p=len(temuan_df.index), max_q=len(temuan_df.index), max_order=None, seasonal=False, n_fits=50)

        temuan_df.loc[temuan_df['jumlah'].isna(), 'jumlah'] = temuan_model.predict(slider_prediksi)

        temuan_ma = temuan_df['jumlah'].rolling(slider_ma).mean()
        temuan_df = temuan_df.append(pd.DataFrame({
            'jumlah': temuan_ma,
            'tahun': temuan_df['tahun'],
            'semester': temuan_df['semester'],
            'data': 'Moving Average'
        }), ignore_index=True)

        temuan_df.loc[:, 'tahun_semester'] = temuan_df[['tahun', 'semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)

        st.subheader('Number of Problems \'{}\' on {}'.format(option_masalah, option_lembaga))
        temuan_fig = px.line(temuan_df, x='tahun_semester', y='jumlah', color='data',  labels={'tahun_semester': 'Year Semester', 'jumlah': 'Number of Problem', 'data': 'Data'}, template='simple_white')
        temuan_fig.update_traces(mode='markers+lines', hovertemplate=None)
        temuan_fig.update_layout(hovermode='x')
        st.plotly_chart(temuan_fig, use_container_width=True)

        rata_asli = temuan_df[temuan_df['data'] == 'Truth'].iloc[-slider_prediksi:, temuan_df.columns.tolist().index('jumlah')].mean()
        rata_prediksi = temuan_df.loc[temuan_df['data'] == 'Prediction', 'jumlah'].mean()

        if rata_asli == rata_prediksi:
            st.write('Based on the prediction, the number of problems \'{}\' on {} for the following years is almost the same as in the previous years'.format(option_masalah, option_lembaga))
        elif rata_asli > rata_prediksi:
            st.write('Based on the prediction, the number of problems \'{}\' on {} for the following years tended to be lower than in the previous years'.format(option_masalah, option_lembaga))
        else:
            st.write('Based on the prediction, the number of problems \'{}\' on {} for the following years tended to be higher than in the previous years'.format(option_masalah, option_lembaga))

    else:
        temuan = db.get_temuan_dengan_nilai(str(id_lembaga), str(id_masalah))
        temuan_df = pd.DataFrame(temuan, columns=['jumlah', 'nilai', 'tahun', 'semester'])
        temuan_df.loc[:, 'data'] = 'Truth'

        temuan_jumlah_df = temuan_df[['jumlah', 'tahun', 'semester', 'data']]
        temuan_nilai_df = temuan_df[['nilai', 'tahun', 'semester', 'data']]

        st.header('Prediction')

        st.subheader('Number of Problems')

        col1_jumlah, col2_jumlah = st.beta_columns(2)

        with col1_jumlah:
            slider_prediksi_jumlah = st.slider('Number of Predictions', 1, 10, 1, key='prediksi1')

        with col2_jumlah:
            slider_ma_jumlah = st.slider('Number of Moving Averages', 2, len(temuan_df.index), 2, key='ma1')

        for i in range(slider_prediksi_jumlah):
            tahun_before = temuan_jumlah_df.iloc[-1, temuan_jumlah_df.columns.tolist().index('tahun')]
            semester_before = temuan_jumlah_df.iloc[-1, temuan_jumlah_df.columns.tolist().index('semester')]
            if semester_before == 1:
                tahun = tahun_before
                semester = 2
            else:
                tahun = tahun_before + 1
                semester = 1
            temuan_jumlah_df = temuan_jumlah_df.append(pd.DataFrame({
                'jumlah': [np.nan],
                'tahun': [tahun],
                'semester': [semester],
                'data': ['Prediction']
            }), ignore_index=True)

        temuan_jumlah_model = auto_arima(temuan_jumlah_df.loc[~temuan_jumlah_df['jumlah'].isna(), 'jumlah'], start_p=0, start_q=0, max_p=len(temuan_jumlah_df.index), max_q=len(temuan_jumlah_df.index), max_order=None, seasonal=False, n_fits=50)

        temuan_jumlah_df.loc[temuan_jumlah_df['jumlah'].isna(), 'jumlah'] = temuan_jumlah_model.predict(slider_prediksi_jumlah)

        temuan_jumlah_ma = temuan_jumlah_df['jumlah'].rolling(slider_ma_jumlah).mean()
        temuan_jumlah_df = temuan_jumlah_df.append(pd.DataFrame({
            'jumlah': temuan_jumlah_ma,
            'tahun': temuan_jumlah_df['tahun'],
            'semester': temuan_jumlah_df['semester'],
            'data': 'Moving Average'
        }), ignore_index=True)

        temuan_jumlah_df.loc[:, 'tahun_semester'] = temuan_jumlah_df[['tahun', 'semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)

        st.subheader('Number of Problems \'{}\' on {}'.format(option_masalah, option_lembaga))
        temuan_jumlah_fig = px.line(temuan_jumlah_df, x='tahun_semester', y='jumlah', color='data',  labels={'tahun_semester': 'Year Semester', 'jumlah': 'Number of Problem', 'data': 'Data'}, template='simple_white')
        temuan_jumlah_fig.update_traces(mode='markers+lines', hovertemplate=None)
        temuan_jumlah_fig.update_layout(hovermode='x')
        st.plotly_chart(temuan_jumlah_fig, use_container_width=True)

        rata_asli_jumlah = temuan_jumlah_df[temuan_jumlah_df['data'] == 'Truth'].iloc[-slider_prediksi_jumlah:, temuan_jumlah_df.columns.tolist().index('jumlah')].mean()
        rata_prediksi_jumlah = temuan_jumlah_df.loc[temuan_jumlah_df['data'] == 'Prediction', 'jumlah'].mean()

        if rata_asli_jumlah == rata_prediksi_jumlah:
            st.write('Based on the prediction, the number of problems \'{}\' on {} for the following years is almost the same as in the previous years'.format(option_masalah, option_lembaga))
        elif rata_asli_jumlah > rata_prediksi_jumlah:
            st.write('Based on the prediction, the number of problems \'{}\' on {} for the following years tended to be lower than in the previous years'.format(option_masalah, option_lembaga))
        else:
            st.write('Based on the prediction, the number of problems \'{}\' on {} for the following years tended to be higher than in the previous years'.format(option_masalah, option_lembaga))

        st.subheader('Amount of Loss')

        col1_nilai, col2_nilai = st.beta_columns(2)

        with col1_nilai:
            slider_prediksi_nilai = st.slider('Number of Prediction', 1, 10, 1, key='prediksi2')

        with col2_nilai:
            slider_ma_nilai = st.slider('Number of Moving Averages', 2, len(temuan_df.index), 2, key='ma2')

        for i in range(slider_prediksi_nilai):
            tahun_before = temuan_nilai_df.iloc[-1, temuan_nilai_df.columns.tolist().index('tahun')]
            semester_before = temuan_nilai_df.iloc[-1, temuan_nilai_df.columns.tolist().index('semester')]
            if semester_before == 1:
                tahun = tahun_before
                semester = 2
            else:
                tahun = tahun_before + 1
                semester = 1
            temuan_nilai_df = temuan_nilai_df.append(pd.DataFrame({
                'nilai': [np.nan],
                'tahun': [tahun],
                'semester': [semester],
                'data': ['Prediction']
            }), ignore_index=True)

        temuan_nilai_model = auto_arima(temuan_nilai_df.loc[~temuan_nilai_df['nilai'].isna(), 'nilai'], start_p=0, start_q=0, max_p=len(temuan_nilai_df.index), max_q=len(temuan_nilai_df.index), max_order=None, seasonal=False, n_fits=50)

        temuan_nilai_df.loc[temuan_nilai_df['nilai'].isna(), 'nilai'] = temuan_nilai_model.predict(slider_prediksi_nilai)

        temuan_nilai_ma = temuan_nilai_df['nilai'].rolling(slider_ma_nilai).mean()
        temuan_nilai_df = temuan_nilai_df.append(pd.DataFrame({
            'nilai': temuan_nilai_ma,
            'tahun': temuan_nilai_df['tahun'],
            'semester': temuan_nilai_df['semester'],
            'data': 'Moving Average'
        }), ignore_index=True)

        temuan_nilai_df.loc[:, 'tahun_semester'] = temuan_nilai_df[['tahun', 'semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)

        st.subheader('Amount of Loss \'{}\' on {}'.format(option_masalah, option_lembaga))
        temuan_nilai_fig = px.line(temuan_nilai_df, x='tahun_semester', y='nilai', color='data',  labels={'tahun_semester': 'Year Semester', 'nilai': 'Amount of Loss (Million Rp)', 'data': 'Data'}, template='simple_white')
        temuan_nilai_fig.update_traces(mode='markers+lines', hovertemplate=None)
        temuan_nilai_fig.update_layout(hovermode='x')
        st.plotly_chart(temuan_nilai_fig, use_container_width=True)

        rata_asli_nilai = temuan_nilai_df[temuan_nilai_df['data'] == 'Truth'].iloc[-slider_prediksi_nilai:, temuan_nilai_df.columns.tolist().index('nilai')].mean()
        rata_prediksi_nilai = temuan_nilai_df.loc[temuan_nilai_df['data'] == 'Prediction', 'nilai'].mean()

        if rata_asli_nilai == rata_prediksi_nilai:
            st.write('Based on the prediction, the amount of loss \'{}\' on {} for the following years is almost the same as in the previous years'.format(option_masalah, option_lembaga))
        elif rata_asli_nilai > rata_prediksi_nilai:
            st.write('Based on the prediction, the amount of loss \'{}\' on {} for the following years tended to be lower than in the previous years'.format(option_masalah, option_lembaga))
        else:
            st.write('Based on the prediction, the amount of loss \'{}\' on {} for the following years tended to be higher than in the previous years'.format(option_masalah, option_lembaga))
