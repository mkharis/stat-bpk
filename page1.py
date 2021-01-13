import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import db

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

    with st.beta_expander('Choose Kind of Problem'):
        option_utama = st.selectbox('Choose Main Problem', ('Permasalahan Kelemahan Sistem Pengendalian Intern', 'Permasalahan Ketidakpatuhan terhadap Ketentuan Peraturan Perundang-undangan'))
        if option_utama == 'Permasalahan Kelemahan Sistem Pengendalian Intern':
            option_jenis = st.selectbox('Choose Kind of Problem', masalah_df.loc[masalah_df['tingkat'] == option_tingkat, 'jenis'].unique())
        else:
            option_jenis = st.selectbox('Choose Kind of Problem', masalah_dengan_nilai_df.loc[masalah_dengan_nilai_df['tingkat'] == option_tingkat, 'jenis'].unique())

    if option_utama == 'Permasalahan Kelemahan Sistem Pengendalian Intern':
        temuan = db.get_temuan_by_lk_only(str(id_lembaga))
        temuan_df = pd.DataFrame(temuan, columns=['jumlah', 'tahun', 'semester', 'masalah', 'jenis'])
        temuan_df = temuan_df[temuan_df['jenis'] == option_jenis]
        temuan_df = temuan_df.groupby(['tahun', 'semester']).sum().reset_index()

        st.header('Historical Table')

        temuan_table = temuan_df.copy()
        temuan_table.columns = ['Year', 'Semester', 'Number of Problems']

        st.subheader('Number of Problems \'{}\' in {}'.format(option_jenis, option_lembaga))
        st.write(temuan_table)

        st.header('Historical Report')

        temuan_table.loc[:, 'Year Semester'] = temuan_table[['Year', 'Semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)

        st.subheader('Number of Problems \'{}\' in {}'.format(option_jenis, option_lembaga))
        temuan_report = px.line(temuan_table, x='Year Semester', y='Number of Problems', template='simple_white')
        temuan_report.update_traces(mode='markers+lines', hovertemplate=None)
        temuan_report.update_layout(hovermode='x')
        st.plotly_chart(temuan_report, use_container_width=True)

        st.write('The lowest number of problems was in period {} semester {}; about {} problems.'.format(temuan_df.loc[temuan_df['jumlah'].idxmin(), 'tahun'], temuan_df.loc[temuan_df['jumlah'].idxmin(), 'semester'], temuan_df['jumlah'].min()))
        st.write('The highest number of problems was in period {} semester {}; about {} problems.'.format(temuan_df.loc[temuan_df['jumlah'].idxmax(), 'tahun'], temuan_df.loc[temuan_df['jumlah'].idxmax(), 'semester'], temuan_df['jumlah'].max()))
        st.write('The average number of problems was about {} problems.'.format(temuan_df['jumlah'].mean()))

        st.header('Basic Statistics')

        col1, col2, col3, col4, col5 = st.beta_columns(5)

        with col1:
            st.subheader('Minimum')
            st.write('{}'.format(np.round(temuan_df['jumlah'].min(), 2)))

        with col2:
            st.subheader('Quantile 1')
            st.write('{}'.format(np.round(temuan_df['jumlah'].quantile(0.25), 2)))

        with col3:
            st.subheader('Median')
            st.write('{}'.format(np.round(temuan_df['jumlah'].quantile(0.5), 2)))

        with col4:
            st.subheader('Quantile 3')
            st.write('{}'.format(np.round(temuan_df['jumlah'].quantile(0.75), 2)))

        with col5:
            st.subheader('Maximum')
            st.write('{}'.format(np.round(temuan_df['jumlah'].max())))

        st.subheader('Box Plot')
        temuan_box = px.box(temuan_table, y='Number of Problems', template='simple_white')
        st.plotly_chart(temuan_box, use_container_width=True)

        st.subheader('Violin Plot')
        temuan_violin = px.violin(temuan_table, y='Number of Problems', template='simple_white')
        st.plotly_chart(temuan_violin, use_container_width=True)

    else:
        temuan = db.get_temuan_dengan_nilai_by_lk_only(str(id_lembaga))
        temuan_df = pd.DataFrame(temuan, columns=['jumlah', 'nilai', 'tahun', 'semester', 'masalah', 'jenis'])
        temuan_df = temuan_df[temuan_df['jenis'] == option_jenis]
        temuan_df = temuan_df.groupby(['tahun', 'semester']).sum().reset_index()

        st.header('Historical Table')

        temuan_table = temuan_df.copy()
        temuan_table.columns = ['Year', 'Semester', 'Number of Problems', 'Amount of Loss (Million Rp)']

        st.subheader('Number of Problems and Amount of Loss \'{}\' in {}'.format(option_jenis, option_lembaga))
        st.write(temuan_table)

        st.header('Historical Report')

        temuan_table.loc[:, 'Year Semester'] = temuan_table[['Year', 'Semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)

        st.subheader('Number of Problems \'{}\' in {}'.format(option_jenis, option_lembaga))
        temuan_report = px.line(temuan_table, x='Year Semester', y='Number of Problems', template='simple_white')
        temuan_report.update_traces(mode='markers+lines', hovertemplate=None)
        temuan_report.update_layout(hovermode='x')
        st.plotly_chart(temuan_report, use_container_width=True)

        st.write('The lowest number of problems was in period {} semester {}; about {} problems.'.format(temuan_df.loc[temuan_df['jumlah'].idxmin(), 'tahun'], temuan_df.loc[temuan_df['jumlah'].idxmin(), 'semester'], temuan_df['jumlah'].min()))
        st.write('The highest number of problems was in period {} semester {}; about {} problems.'.format(temuan_df.loc[temuan_df['jumlah'].idxmax(), 'tahun'], temuan_df.loc[temuan_df['jumlah'].idxmax(), 'semester'], temuan_df['jumlah'].max()))
        st.write('The average number of problems was about {} problems.'.format(temuan_df['jumlah'].mean()))

        st.subheader('Amount of Loss \'{}\' in {}'.format(option_jenis, option_lembaga))
        temuan_report = px.line(temuan_table, x='Year Semester', y='Amount of Loss (Million Rp)', template='simple_white')
        temuan_report.update_traces(mode='markers+lines', hovertemplate=None)
        temuan_report.update_layout(hovermode='x')
        st.plotly_chart(temuan_report, use_container_width=True)

        st.write('The lowest amount of loss was in period {} semester {}; about {} million rupiah.'.format(temuan_df.loc[temuan_df['jumlah'].idxmin(), 'tahun'], temuan_df.loc[temuan_df['jumlah'].idxmin(), 'semester'], temuan_df['jumlah'].min()))
        st.write('The highest amount of loss was in period {} semester {}; about {} million rupiah.'.format(temuan_df.loc[temuan_df['jumlah'].idxmax(), 'tahun'], temuan_df.loc[temuan_df['jumlah'].idxmax(), 'semester'], temuan_df['jumlah'].max()))
        st.write('The average amount of loss was about {} million rupiah.'.format(temuan_df['jumlah'].mean()))
        st.header('Basic Statistics')

        st.subheader('Number of Problems')
        col1_1, col2_1, col3_1, col4_1, col5_1 = st.beta_columns(5)

        with col1_1:
            st.subheader('Minimum')
            st.write('{}'.format(np.round(temuan_df['jumlah'].min(), 2)))

        with col2_1:
            st.subheader('Quantile 1')
            st.write('{}'.format(np.round(temuan_df['jumlah'].quantile(0.25), 2)))

        with col3_1:
            st.subheader('Median')
            st.write('{}'.format(np.round(temuan_df['jumlah'].quantile(0.5), 2)))

        with col4_1:
            st.subheader('Quantile 3')
            st.write('{}'.format(np.round(temuan_df['jumlah'].quantile(0.75), 2)))

        with col5_1:
            st.subheader('Maximum')
            st.write('{}'.format(np.round(temuan_df['jumlah'].max())))

        st.subheader('Amount of Loss (Million Rp)')
        col1_2, col2_2, col3_2, col4_2, col5_2 = st.beta_columns(5)

        with col1_2:
            st.subheader('Minimum')
            st.write('{}'.format(np.round(temuan_df['nilai'].min(), 2)))

        with col2_2:
            st.subheader('Quantile 1')
            st.write('{}'.format(np.round(temuan_df['nilai'].quantile(0.25), 2)))

        with col3_2:
            st.subheader('Median')
            st.write('{}'.format(np.round(temuan_df['nilai'].quantile(0.5), 2)))

        with col4_2:
            st.subheader('Quantile 3')
            st.write('{}'.format(np.round(temuan_df['nilai'].quantile(0.75), 2)))

        with col5_2:
            st.subheader('Maximum')
            st.write('{}'.format(np.round(temuan_df['nilai'].max())))

        st.subheader('Box Plot Number of Problems')
        temuan_box = px.box(temuan_table, y='Number of Problems', template='simple_white')
        st.plotly_chart(temuan_box, use_container_width=True)

        st.subheader('Box Plot Amount of Loss')
        temuan_box = px.box(temuan_table, y='Amount of Loss (Million Rp)', template='simple_white')
        st.plotly_chart(temuan_box, use_container_width=True)

        st.subheader('Violin Plot Number of Problems')
        temuan_violin = px.violin(temuan_table, y='Number of Problems', template='simple_white')
        st.plotly_chart(temuan_violin, use_container_width=True)

        st.subheader('Violin Plot Amount of Loss')
        temuan_violin = px.violin(temuan_table, y='Amount of Loss (Million Rp)', template='simple_white')
        st.plotly_chart(temuan_violin, use_container_width=True)
