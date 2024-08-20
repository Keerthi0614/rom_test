#Import the required Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import pickle 
from statistics import mean, median

filename_LS ='ROM.pkl'

# Add a title and intro text
st.title('ROM')
st.text('This is a web app to estimate the suction efficeincy of the aspirator')

# Select the line to predict the quality data
#st.header('Select the Float Line')
#lines = ["BWI"]
#beam_type = ["Narrow","Wide"]
#line_choice = st.selectbox("Select Float Line",lines)
#if line_choice == 'BWI':
beam_width = 220
rz_vol = 0.008888 #m3
rz_area = 0.0404 #m2
m_file = open(r'/workspaces/rom_test/ROM.pkl','rb')
ROM_Model = pickle.load(m_file)
# if line_choice == 'CNN':
#    beam_width = 202
#    rz_vol = 0.0061408 #m3
#    rz_area = 0.0304 #m2
#    ROM_Model = pickle.load(open('ROM.pkl', 'rb'))
# elif line_choice == 'JHD':
#    beam_width = 175
#    beam_choice = st.selectbox("Select Beam Type",beam_type)
#    if beam_choice == 'Narrow':
#       rz_vol = 0.00451647 #m3
#       rz_area = 0.0258084 #m2
#       ROM_Model = pickle.load(open('ROM.pkl', 'rb'))
#    elif beam_choice == 'Wide':
#       rz_vol = 0.004667901 #m3
#       rz_area = 0.02667372 #m2
#       ROM_Model = pickle.load(open('ROM.pkl', 'rb'))
# elif line_choice == 'BWI':
#    beam_width = 220
#    rz_vol = 0.008888 #m3
#    rz_area = 0.0404 #m2
#    ROM_Model = pickle.load(open('ROM.pkl', 'rb'))

est_options = ["Suction Efficiency"]
options_sel = st.selectbox("Select Estimator",est_options)
sidebar = st.sidebar  
# Enter the necessary information 
sidebar.header('Enter Process Parameters')
pull = sidebar.number_input('Pull Rate (t/d): ')
glass_thickness_list = [3.5,3.9,4.9,5.9]
glass_thickness_sel = sidebar.selectbox("Select Glass Thickness",glass_thickness_list)
if glass_thickness_sel == 3.5:
   glass_thickness = 3.5
elif glass_thickness_sel == 3.9:
   glass_thickness = 3.9
elif glass_thickness_sel == 4.9:
   glass_thickness = 4.9
elif glass_thickness_sel == 5.9:
   glass_thickness = 5.9
bath_pressure = sidebar.number_input('Bath Pressure (Pa): ')
gross_width = sidebar.number_input('Gross Width (mm): ')
lehr_speed_calc = pull/(3.615*glass_thickness*(gross_width/1000))
sidebar.metric("Lehr Speed Estimated(m/min):",round(lehr_speed_calc,2))
lehr_speed_act = sidebar.number_input('Lehr Speed Actual (m/min): ')
lehr_offset = lehr_speed_act-lehr_speed_calc
lehr_speed = lehr_speed_calc + lehr_offset
sidebar.metric("Lehr Speed offset:",round(lehr_offset,2))
sidebar.metric("Lehr Speed Corrected (m/min):",round(lehr_speed,2))
temp = sidebar.number_input('Temperature (C): ')
b_g_distance = sidebar.number_input('Beam-Glass Distance (mm): ')
silane = sidebar.number_input('Silane (lpm): ')
ethylene = sidebar.number_input('Ethylene (lpm): ')
n2 = sidebar.number_input('N2 (lpm): ')
asp_a = sidebar.number_input('Aspirator Horizontal Distance (mm): ')
asp_b = sidebar.number_input('Aspirator Vertical Distance (mm): ')
suction_right = sidebar.number_input('Suction Pressure Right(mmWC): ')
suction_left = sidebar.number_input('Suction Pressure Left(mmWC): ')
# Button to initalize estimator function
predict = sidebar.button("Calculate")
sidebar.write(predict)
# Estimator Function
if predict :
# Run the model with the inputs used
   total_flow = round(((silane+ethylene+n2)*(0.0000208433333333333)),5)
   ROM_predicted = ROM_Model.predict([[bath_pressure,suction_right,suction_left,total_flow,(lehr_speed_act/60),b_g_distance,asp_a,asp_b]])
   vel_inlet = ROM_predicted[0,0]
   vel_rz = ROM_predicted[0,1]
   vel_el = ROM_predicted[0,2]
   vel_asp = ROM_predicted[0,3]
   vel_port = ROM_predicted[0,4]
   mf_rz = ROM_predicted[0,5]
   mf_el = ROM_predicted[0,6]
   mf_asp = ROM_predicted[0,7]
   mf_port = ROM_predicted[0,8]
   # Calculating the retention time
   retention_time = beam_width/(vel_rz*100)
   # Suction Efficiency
   ratio = (mf_el/mf_asp)*100
   # Display Gas Outputs 
   col1,col2,col3,col4 = st.columns(4)
   col1.metric("Total Mass Flow (kg/sec):",total_flow)
   col2.metric("Gas Velocity (m/s)",round(vel_rz,2))
   col3.metric("Retention Time (sec)",round(retention_time,2))
   col4.metric("Suction Efficiency (%)",round(ratio,2))
   # Velocity Range
   velocity = [vel_inlet,vel_rz,vel_el,vel_asp]
   mass_flow = [total_flow,mf_rz,mf_el,mf_asp]
   # Convert to dataframe 
   final_ds = [['Inlet',vel_inlet,total_flow],['Reaction Zone',vel_rz,mf_rz],['Exit Lip',vel_el,mf_el],['Aspirator Inlet',vel_asp,mf_asp]]
   final_df = pd.DataFrame(final_ds, columns=['Location', 'Velocity','Mass Flow'])
   # Plot the Data
   #fig_vel = st.bar_chart(final_df, x="Location", y="Velocity")
   fig_vel = px.line(final_df,x="Location", y="Velocity",markers=True)
   #fig_mf = st.bar_chart(final_df, x="Location", y="Mass Flow")
   fig_mf = px.line(final_df,x="Location", y="Mass Flow",markers=True)
   #tab1,tab2 = st.tab(["Velocity","Mass Flow"])
   #with tab1:
   st.header('Velocity')
   st.plotly_chart(fig_vel)
   #with tab2:
   st.header('Mass Flow')
   st.plotly_chart(fig_mf)