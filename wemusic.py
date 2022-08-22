#requirements
import pandas as pd
import streamlit as st
import gspread
from df2gspread import df2gspread as d2g
from gspread_pandas import Spread,Client
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from streamlit_option_menu import option_menu
from streamlit_echarts import st_echarts
import streamlit.components.v1 as components
from mixpanel import Mixpanel
import json

st.set_page_config(page_title="Dome Flipper Experience", page_icon=":musical_note:", layout="wide",initial_sidebar_state="expanded")

#grabbing secrets and google sheets credentials
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
secret = st.secrets["google_key_file"]
credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
spreadsheet_key = st.secrets["spreadsheet_key"]

#menu of for flipper experience
with st.sidebar:
    choose = option_menu("WeMusic", ["MeProfile", "WeArtists"],
                            icons=['person-circle','people'],
                            menu_icon="music-note-beamed", default_index=1, #orientation="horizontal",
                            styles={
        "container": {"padding": "10!important", "background-color": "#AB545B"},
        "icon": {"color": "white", "font-size": "30px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#54ABA4"},
        "nav-link-selected": {"background-color": "#7854AB"},
    }
    )

genres_list = ["None","Indie","Alternative","Hip Hop","Rock","Pop","Jazz","Country"]

if choose == "MeProfile":
    st.header("MeProfile")
    user_email = st.text_input("Enter email to sign in or create account")
    if user_email:
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
        gc = gspread.authorize(credentials)
        sheet = gc.open('WeMusic')
        sheet_instance = sheet.get_worksheet(0)
        profiles = sheet_instance.get_all_records()
        profiles = pd.DataFrame.from_dict(profiles)
        if user_email not in list(profiles['email']):
            col1, col2 = st.columns(2)
            with col1:
                st.write("__About You__")
                photo = st.text_input("Paste in a link to an online photo (maybe from Spotify)")
                name = st.text_input("Name")
                pronouns = st.text_input("Pronouns")
                artist_name = st.text_input("Artist Name")

            with col2:
                st.write("__Artist Details__")
            
                if 'n_influences' not in st.session_state:
                    st.session_state.n_influences = 0
                influences = []

                add = st.button(label="Add Influence")
                remove = st.button(label="Remove Influence")

                if add:
                    st.session_state.n_influences += 1
                    #st.experimental_rerun()

                if remove:
                    st.session_state.n_influences -= 1
                    #st.experimental_rerun()

                for i in range(st.session_state.n_influences):
                    #add inputs here
                    influence = st.text_input("Influence "+str(i+1), key=i) #pass index as key
                    tup = (influence)
                    influences.append(tup)
                
                genres = st.multiselect("Genres", genres_list)

                teammates = st.multiselect("Teammates", list(profiles['artist_name']))

            st.write("__Your Links__")
            spotify = st.text_input("Link to Spotify")
            apple_music = st.text_input("Link to Apple Music")
            soundcloud = st.text_input("Link to Soundcloud")

            #artist details brought together in list
            profile_details = [user_email, name, pronouns, artist_name, influences, genres, teammates, photo, spotify, apple_music, soundcloud]
            profiles.loc[len(profiles)]=profile_details

            if st.button("Finish"):
                client = Client(scope=scope,creds=credentials)
                spreadsheetname = "WeMusic"
                spread = Spread(spreadsheetname,client = client)
                col = ['user_email', 'name', 'pronouns', 'artist_name', 'influences', 'genres', 'teammates', 'photo', 'spotify', 'apple_music', 'soundcloud']
                spread.df_to_sheet([profiles.columns.values.tolist()] + profiles.values.tolist())
                st.success("Congrats! You may sign in now at http://localhost:8501/#meprofile")
                user_email = user_email
        else:
            profiles_select = profiles[(profiles['email']==user_email)]
            profiles_select = profiles_select.reset_index(drop=True)
            st.subheader(":musical_note: Welcome, "+profiles_select['artist_name'][0])
            col1, col2 = st.columns(2)
            with col1:
                st.image(profiles_select['photo'][0])
                st.write("__About You__")
                st.write("Name: "+profiles_select['name'][0])
                st.write("Pronouns: "+profiles_select['pronouns'][0])
                st.write("Artist Name: "+profiles_select['artist_name'][0])
                st.write("__Artist Details__")
                st.write("Influences: "+profiles_select['influences'][0])
                st.write("Genres: "+profiles_select['genres'][0])
                with st.expander("Edit Genres"):
                    genres = st.multiselect("Genres", genres_list)
                    if st.button("Complete Genre Edits"):
                        name = profiles_select['name'][0]
                        pronouns = profiles_select['pronouns'][0]
                        artist_name = profiles_select['artist_name'][0]
                        influences = profiles_select['influences'][0]
                        teammates = profiles_select['teammates'][0]
                        photo = profiles_select['photo'][0]
                        spotify = profiles_select['spotify'][0]
                        apple_music = profiles_select['apple_music'][0]
                        soundcloud = profiles_select['soundcloud'][0]
                        profile_details = [user_email, name, pronouns, artist_name, influences, genres, teammates, photo, spotify, apple_music, soundcloud]
                        profiles = profiles[(profiles['email']!=user_email)]
                        profiles = profiles.reset_index(drop=True)
                        profiles.loc[len(profiles)]=profile_details
                        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                        credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
                        gc = gspread.authorize(credentials)
                        sheet = gc.open('WeMusic')
                        sheet_instance = sheet.get_worksheet(0)
                        col = ['user_email', 'name', 'pronouns', 'artist_name', 'influences', 'genres', 'teammates', 'photo', 'spotify', 'apple_music', 'soundcloud']
                        sheet_instance.update(col + profiles.values.tolist())
                        #client = Client(scope=scope,creds=credentials)
                        #spreadsheetname = "WeMusic"
                        #spread = Spread(spreadsheetname,client = client)
                        #col = ['user_email', 'name', 'pronouns', 'artist_name', 'influences', 'genres', 'teammates', 'photo', 'spotify', 'apple_music', 'soundcloud']
                        #spread.df_to_sheet(profiles[col],sheet = spreadsheetname,index = False)
                        st.success("Updated genres!")
                user_email = user_email
                st.write("Your Teammates: "+profiles_select['teammates'][0])
                with st.expander("Edit Teammates"):
                    teammates = st.multiselect("Teammates", list(profiles['artist_name']))
                    if st.button("Complete Teammate Edits"):
                        name = profiles_select['name'][0]
                        pronouns = profiles_select['pronouns'][0]
                        artist_name = profiles_select['artist_name'][0]
                        influences = profiles_select['influences'][0]
                        genres = profiles_select['genres'][0]
                        photo = profiles_select['photo'][0]
                        spotify = profiles_select['spotify'][0]
                        apple_music = profiles_select['apple_music'][0]
                        soundcloud = profiles_select['soundcloud'][0]
                        profile_details = [user_email, name, pronouns, artist_name, influences, genres, teammates, photo, spotify, apple_music, soundcloud]
                        profiles = profiles[(profiles['email']!=user_email)]
                        profiles = profiles.reset_index(drop=True)
                        
                        profiles.loc[len(profiles)]=profile_details
                        client = Client(scope=scope,creds=credentials)
                        spreadsheetname = "WeMusic"
                        spread = Spread(spreadsheetname,client = client)
                        col = ['user_email', 'name', 'pronouns', 'artist_name', 'influences', 'genres', 'teammates', 'photo', 'spotify', 'apple_music', 'soundcloud']
                        spread.df_to_sheet(profiles[col],sheet = spreadsheetname,index = False)
                        st.success("Updated teammates!")
            with col2:
                st.write("__Your Links__")
                st.write("Spotify: "+profiles_select['spotify'][0])
                st.write("Apple Music: "+profiles_select['apple_music'][0])
                st.write("SoundCloud: "+profiles_select['soundcloud'][0])

if choose == "WeArtists":
    st.header("WeArtists")
    st.subheader("**Independent doesn't mean alone**")
    st.write("Don't have thousands of followers or monthly listeners? Not getting recommended on streaming platforms?")
    st.write("Partner up with other small artists you dig and promote each other's work: __*co-promotion*__ as a substitute for algorithmic placement!")
    st.write("Just imagine — 3 artists with 1000 followers gives each of them 2000 new people to reach! We just have to work together.")
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
    gc = gspread.authorize(credentials)
    sheet = gc.open('WeMusic')
    sheet_instance = sheet.get_worksheet(0)
    profiles = sheet_instance.get_all_records()
    profiles = pd.DataFrame.from_dict(profiles)
    
    filter = st.selectbox("Filter by Genre",genres_list)
    profiles_filter = pd.DataFrame(columns=["email","name","pronouns","artist_name","influences","genres","teammates","photo","spotify","apple_music","soundcloud"])
    if filter == "None":
        profiles_filter = profiles
    else:
        for i in range(len(profiles['name'])):
            if filter in profiles['genres'][i]:
                profiles_filter = profiles_filter.append({'email':profiles['email'][i], 
                'name':profiles['name'][i], 
                'pronouns':profiles['pronouns'][i], 
                'artist_name':profiles['artist_name'][i], 
                'influences':profiles['influences'][i], 
                'genres':profiles['genres'][i], 
                'teammates':profiles['teammates'][i], 
                'photo':profiles['photo'][i],
                'spotify':profiles['spotify'][i],
                'apple_music':profiles['apple_music'][i],
                'soundcloud':profiles['soundcloud'][i]},ignore_index=True)

    for i in range(len(profiles_filter['name'])):
        col1, col2 = st.columns([1,3], gap="medium")

        with col1:
            st.image(profiles_filter['photo'][i])
            st.write(profiles_filter['artist_name'][i])
        with col2:
                with st.expander("Profile: "+profiles_filter['artist_name'][i]):
                    st.write("__Artist Details__")
                    st.write("Name: "+profiles_filter['name'][i])
                    st.write("Pronouns: "+profiles_filter['pronouns'][i])
                    st.write("Artist Name: "+profiles_filter['artist_name'][i])
                    st.write("Influences: "+profiles_filter['influences'][i])
                    st.write("Genres: "+profiles_filter['genres'][i])
                    st.write("Your Teammates: "+profiles_filter['teammates'][i])
                    st.write("Spotify: "+profiles_filter['spotify'][i])
                    st.write("Apple Music: "+profiles_filter['apple_music'][i])
                    st.write("SoundCloud: "+profiles_filter['soundcloud'][i])
                    st.write("__Contact__", key=i)
                    st.write("Email: "+profiles_filter['email'][i])
                    st.write("Reach out to this person to see if they'd be up for being a co-promotion teammate! If they're up for it, add them as a teammate on your profile :)", key = i)
