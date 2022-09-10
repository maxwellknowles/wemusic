#requirements
import pandas as pd
import streamlit as st
import gspread
from gspread_pandas import Spread,Client
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from streamlit_option_menu import option_menu
from stytch import Client as stytch_client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#Authentication - without user
spotify_cid = st.secrets["spotify_cid"]
spotify_secret = st.secrets["spotify_secret"]
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_cid, client_secret=spotify_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

st.set_page_config(page_title="WeMusic Beta", page_icon=":musical_note:", layout="wide",initial_sidebar_state="expanded")

#grabbing secrets and google sheets credentials
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
spreadsheet_key = st.secrets["spreadsheet_key"]

#menu of for flipper experience
with st.sidebar:
    choose = option_menu("WeMusic Beta", ["MeProfile", "WeArtists"],
                            icons=['person-circle','people'],
                            menu_icon="music-note-beamed", default_index=1, #orientation="horizontal",
                            styles={
        "container": {"padding": "10!important", "background-color": "#AB545B"},
        "icon": {"color": "white", "font-size": "30px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#54ABA4"},
        "nav-link-selected": {"background-color": "#7854AB"},
    }
    )

genres_list = ["None","Indie","Alternative","Hip Hop","Rock","Pop","Jazz","Country","Folk","Gospel","EDM","Instrumental"]

if choose == "MeProfile":
    st.header("MeProfile")
    
    if not st.experimental_get_query_params():
        user_email = st.text_input("Enter email to begin session", key=1000)

        if user_email:

            client = stytch_client(
                project_id=st.secrets["project_id"],
                secret=st.secrets["secret"],
                environment="live",
            )
            resp = client.magic_links.email.login_or_create(
                email=user_email
            )

            st.success("Please check your email for a magic link to sign in safely :smile:")

    if st.experimental_get_query_params():
        user_email = st.text_input("Now enter email to pull up your account data or create", key=3000)
        
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
        gc = gspread.authorize(credentials)
        sheet = gc.open('WeMusic')
        sheet_instance = sheet.get_worksheet(0)
        profiles = sheet_instance.get_all_records()
        profiles = pd.DataFrame.from_dict(profiles)
        if user_email:
            if user_email not in list(profiles['email']):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("__About You__")
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
                profile_details = [user_email, name, pronouns, artist_name, influences, genres, teammates, spotify, apple_music, soundcloud]
                profiles.loc[len(profiles)]=profile_details

                if st.button("Finish"):
                    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                    client = Client(scope=scope,creds=credentials)
                    spread = Spread('WeMusic',client = client)
                    spread.df_to_sheet(profiles, index=False, sheet='profiles', start='A1', replace=True)
                    st.success("Congrats! You can see your account at https://maxwellknowles-wemusic-wemusic-hz9pvc.streamlitapp.com/#meprofile")
                    user_email = user_email

            else: 
                profiles_select = profiles[(profiles['email']==user_email)]
                profiles_select = profiles_select.reset_index(drop=True)
                st.subheader(":musical_note: Welcome, "+profiles_select['artist_name'][0])
                col1, col2 = st.columns(2)
                with col1:
                    st.write("__About You__")
                    spotify_link = profiles_select['spotify'][i]
                    try:
                        artist = sp.artist(spotify_link)
                        st.image(artist['images'][1]['url'])
                    except Exception:
                        st.image("data:image/png;base64,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")
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
                            spotify = profiles_select['spotify'][0]
                            apple_music = profiles_select['apple_music'][0]
                            soundcloud = profiles_select['soundcloud'][0]
                            profile_details = [user_email, name, pronouns, artist_name, influences, genres, teammates, spotify, apple_music, soundcloud]
                            profiles = profiles[(profiles['email']!=user_email)]
                            profiles = profiles.reset_index(drop=True)
                            profiles.loc[len(profiles)]=profile_details
                            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                            credentials = service_account.Credentials.from_service_account_info(st.secrets["google_key_file"], scopes=scope,)
                            gc = gspread.authorize(credentials)
                            sheet = gc.open('WeMusic')
                            sheet_instance = sheet.get_worksheet(0)
                            client = Client(scope=scope,creds=credentials)
                            spread = Spread('WeMusic',client = client)
                            spread.df_to_sheet(profiles, index=False, sheet='profiles', start='A1', replace=True)
                            st.success("Updated genres!")
                    st.write("Your Teammates: "+profiles_select['teammates'][0])
                    with st.expander("Edit Teammates"):
                        teammates = st.multiselect("Teammates", list(profiles['artist_name']))
                        if st.button("Complete Teammate Edits"):
                            name = profiles_select['name'][0]
                            pronouns = profiles_select['pronouns'][0]
                            artist_name = profiles_select['artist_name'][0]
                            influences = profiles_select['influences'][0]
                            genres = profiles_select['genres'][0]
                            spotify = profiles_select['spotify'][0]
                            apple_music = profiles_select['apple_music'][0]
                            soundcloud = profiles_select['soundcloud'][0]
                            profile_details = [user_email, name, pronouns, artist_name, influences, genres, teammates, spotify, apple_music, soundcloud]
                            profiles = profiles[(profiles['email']!=user_email)]
                            profiles = profiles.reset_index(drop=True)
                            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                            profiles.loc[len(profiles)]=profile_details
                            client = Client(scope=scope,creds=credentials)
                            spread = Spread('WeMusic',client = client)
                            spread.df_to_sheet(profiles, index=False, sheet='profiles', start='A1', replace=True)
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
    profiles_filter = pd.DataFrame(columns=["email","name","pronouns","artist_name","influences","genres","teammates","spotify","apple_music","soundcloud"])
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

    col1, col2 = st.columns(2)

    with col1:
        for i in range(len(profiles_filter['name'])):
            mod = i % 2
            if mod > 0:
                spotify_link = profiles_filter['spotify'][i]
                try:
                    artist = sp.artist(spotify_link)
                    st.image(artist['images'][1]['url'])
                except Exception:
                    st.image("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAh1BMVEX///8AAAA9PT36+voKCgozMzNVVVX09PT39/cWFhYEBATy8vIYGBgODg4HBwdpaWkcHBxxcXGMjIze3t7l5eXKysrs7Oxzc3M4ODh7e3tiYmKJiYnBwcGDg4PY2Niqqqqzs7Ofn59FRUUnJydCQkIqKirGxsalpaVdXV2UlJRNTU2ysrK8vLy1sja6AAAKl0lEQVR4nO1daZeyOgz2CgooyiKouKPjMo7///ddZ5y3CxRom7Zw5vh8FdsG0mxN0l7vjTfeeOONN97QCGt2OeRxtoiC1SqIFlmcHy4zq+1VCSE5rG/98D8mwv5tfUjaXmEzxo/t0WOTQMI7bh/jttdaCWuTDZppwBhkmw5y2vg6nIhQ8cJkeO3Uh3Gu96k4FS9M71en7fX/Ig0kvgX1XYK0bRp6PTcX2hdVGORuq2TMtxwiig/edt4aGUlkNy3PDs+DZb+/HJzD5mejdvTLfFGzwcN7FH+lCcUvbpJ+xdG9QlP+kLIw/1WcbdUbDofxpnY980089KtI2RoWYVf2e50M8xnfALO8Qu+EV70rp5AumUvILkKa2rosmK+jv9O17gLcbFSe3V9I6YI0Yoi9UWZEFm9O5anvX9JWk7U/lsc7bVSumD3vojSrHXHuiyrMGGI802xP7kp63F8rMPvm6xKHDbTulLz46rxYETs7cZEUO1czMgNuUJhrslYo9cclzRRoYq+kKHRXik2KZFWYYKnFZkkL336pwfZOC1vQ0zDHF/3h7U8t392KC9N8qZ7hk35VR6DErcbsg57pU+3wGTX4VPHoNGLaqs5Ujh1RQ581G0PpmZouUjcyLU1u2i1tZ0hNGKgal6JjpJWt/iEeaaCE4itPvzn3gw3lrSjhLmqfn7RJqyJ2lK+iYMdTcndp0KeeU4YEmKG/yNGORh1qh9IoQM2Ykor2bjiI5t6JyW2QtZKQ9tXQeOzcIsWwD7AgXZJN7y2cAVjkN1nKMwTpfxxbCc66pEMvrU5y8nW0FPt3SKaQ9Bl3xEY/tRZhnhNBG1vKyLMIJ8czFTNjYEfo+IHMPiXiPiNDdgkbG8LuktDwG4I3jdiJ1YiJpQi/UpdgzZuO1YmAUCcnUeFJmIrn1g8rHeKtCjJXivly2uJGZyxnJLYcQnq3vEFeILZJX+R/V/y/o661iYGwhPf8/3KwU2Mb86TqMcPaOeTf79uOMdY3COba8v5njqlfdibthTA0Jrz2EqHTO5Bb8Q+psAhOcKRvpXdtYrjhjcvnY+Hwz6RTqW4J5niu8BCxQ9a61yYGLINsnl2CH/eU2CbzdLNJlbgzY2zQcwguF8cbYvDUyef9d3Lv/gknZo3fcbMuydHDPtRLT4dUBHd0g1ptDn7JzV4vFtfAHTIvngg+EQCPsjHbD5oexdJ6Apv0wswzCWGKiRBETQPhCBAsAr6vSOaawkKfWDU0xIYcLBhA1uKeTcYTowNk3BlmmHqRiu33O2S+S01yHSyIiwN29dY8DlFCWGBek+73dLshmw9/6mHdY2P0Jn2I2VtM9ShgARjaQhJ4Wvc+rkom29XT8d8Isv3wdq/LGcRxFwgj31irJwExqi88vGUhmRUCppozMgVp2JBdgvbfpJr7cXQRcviYN9FRzxVNwG5fddQRR+UugJmGrKXTgMQued42srNqvlozamXvCyfA8Jj/K+2tMZqoVkY3YMxcegEQwxp98VGVcn+geSDphE3C9wcQAZyjUR4VT2yVzJOWl10GxDPB9laVn4jsGIjw1U9IDyn3qnAuegCyRfSzFt4kHvv3BE0DctZdDjpGoAAmjp6yw1UH9DvsyJCRO18ERPySQom923GMAhbvaDS1oBHMORqHzTpoAaC9Th2uVEHgiIMFVA/EfiH9fz+DnMOnu9xYFjYBBpqQeP1g/oxMC2jiXcRePgbE2fkGctyYvGOheaARxqSh3pUzmF4NtJuZ0g8rTHAa95a5fgRwbBw77ix9hF0v8OmOW1v2KpVQQgEbD6ylYjUCPxXZ1ZQhe/DjVay6D4xfc/SrghSzS6XkgoW1XnDQaCxXEyl+Gz7Tk5KKb6KmIgS9JpZcQn4uUB/+YsbcJ0s1x/ZIU7C8XeTUn5XM1bPWJfayY0Wn3cicY2kkpMYajx4aMUs3j+ern2dUNZOXPW249PFI4cIE1WWwdDdSl0vIFNYhOPlh6Hvh96GOdYgGP99lMogOz6+R3D3/+Wt4DmAGNmJb1uECOmASSr+hkQQ+js2G2evVj5PkFZDbrTwUu/PCDGBjI7OQZTXCCZnfPCrIOA2Xn7vfXWGl67NPHyl6C2k5X0sImLX2XtnGssPwNOj3B6Efln8chbIMVstawM1urWQavEiGZms3O0z8Ov1GL4QFWy7OUSt+QQrRXUq2qplKeXG1ChFkotylvscPJTJuHHprLBMlR2OLC5M1oOnORNyBrzcaAWZ8ndXeDE9YoWAf8MD4FeBYnVnr44fwNql3rORd3S9oNyfRSHC9qysffOAILdaDHdWpRn3wQToclAI/iEDa6C+QEcIOvcoG6DhCpE3gzuR9oSFAJxsyVdBiS9CYaAiZSgaxZ2DOekpgIc+xKYgteaxwle6jhyFWBdZ0rCB50FPuwSMBodNXfNBTwTpyR2935soEIRTWbjp6w8LAFxm2z16aGIRSIRoPQ+WOp5W0NxThAXzaWiW15RIGjBOSo39VJQzIpXAYJ6Q5hUMuqcY0IRxJNXJpTqYJ4Ulzws8IiEPThOATyuq3LZUKaJoQnlRAqeRMw4RwJWcSZ/38PolhQvjSZXECM789apYQXKczrU2Ox4YTd5DGLCGcKeUEb3HX6JolhDfJX6Lswigh3GUXEoUwRgnBy2tqkoJjX1y1foYJEShNEi8WM0mIQLFYL0fP+nz1lAYJESrfEy6oNEgIjvPw1EgSJa5c1RFZXwG46v+JElcetic2lGAAUDewl8EniLA1A051UwrRMnDyD10tzOfUDN1slYDtd+56I2KXwNP2VEGmeQWZXAmvaVcELHoFZFAXG7zgULlAgxcyK1z0WEwPLCIwK3ScTfyvE8xFMJZY8tKOaEvVAckl35aqW43CxvKNwv5O6zaqmV7L24TYIDIlqwRztdve8EHQIZOoRjacFE6yUAhww8mOtABNiNJfuRagHWnKSjqg0pW3HWiTS7aTlu+63rHGxYAF/JVW0n+nuXer7dbHVLv1A3S41hrgJ1TATEG/SPpKAmOakb6SQElgiir0nBiyVh5UFhi0lPQXVCugkRELkrQTFV5AQjc1Gmrf8mNNF6mUrrbR7DOmdP6tIr56gb5sSCt7WWu695DiAHTh+qcPfdc/FRLZlPfpLV7IpaqkkIa1plM97YP6OdLChaUDDTvlUjg18rXsxtKldTfVl9YVc7r1XFrHuEbQ3iq8y3ucmbpGsMe42FHZjYjOtpjQrfFixx7rqk0ld0Yz7rDWe9XmU6xkxRkVXH4amL/8tMe+jva4l57X3X+UxztBWsfxT826INiLpObetHhB8BM7Zhp5uNiIXdm8idq9svkbe+gl2rvKS7SBfYVE4VZea+4N40f9teaPeFhVBTTZmg+fzRc1Za3+MVjv04RSMs4s3a+DY9XV7E/YkGJ9ABLGndHFpYWn83c9+/nEqGcvPrtoLcDMUmSy8NftkfENN1eS5jTIWwkt00gDaIlr0IHz1h84+6F06dt0uG/9sJXE+FqhF+q/xfDaKSpesDbZoLFnMcZomV06k7JTgvPYHjkEmXfcPjr4KYpIHvHqI2R+nNHpYxU/OpWY1whrlh6ucbaIgtUqiBZZfD2ks+7y0htvvPHGG2/8CfwPaKOSGjVvDHEAAAAASUVORK5CYII=")
                st.write(profiles_filter['artist_name'][i])
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
            else:
                pass
    with col2:
        for i in range(len(profiles_filter['name'])):
            mod = i % 2
            if mod == 0:
                spotify_link = profiles_filter['spotify'][i]
                try:
                    artist = sp.artist(spotify_link)
                    st.image(artist['images'][1]['url'])
                except Exception:
                    st.image("data:image/png;base64,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")
                st.write(profiles_filter['artist_name'][i])
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
            else:
                pass
