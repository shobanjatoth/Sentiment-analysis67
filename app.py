
import streamlit as st
import pandas as pd
import cricket
import cricketh
import preprocessor,helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff







 #cricket data
data=pd.read_csv("deliveries.csv")
data2=pd.read_csv("matches.csv")
data=preprocessor.ipl(data,data2)


#olympic data
df=pd.read_csv("athlete_events.csv")
region_df=pd.read_csv("noc_regions.csv")
df = preprocessor.preprocess(df,region_df)

#tornment data
data1=pd.read_csv("tornament.csv")
data1=preprocessor.tornmet(data1)





# Initialize session state for managing which sport was selected
if "selected_sport" not in st.session_state:
    st.session_state.selected_sport = None

# Main title
st.title("Sports Analysis")

# Create columns for side-by-side buttons
col1, col2 = st.columns(2)

# Olympics button
with col1:
    if st.button("Olympics Analysis", key="olympics", help="Click to analyze Olympics data"):
        st.session_state.selected_sport = "Olympics"

# Cricket button
with col2:
    if st.button("Cricket Analysis", key="cricket", help="Click to analyze Cricket data"):
        st.session_state.selected_sport = "Cricket"

# Olympics Analysis
if st.session_state.selected_sport == "Olympics":
    st.title("Olympics Analysis")
    user_menu = st.sidebar.radio(
        'Select an Option',
        ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis')
    )

    # Medal Tally Analysis
    if user_menu == 'Medal Tally':
        st.sidebar.header("Medal Tally")
        years, country = helper.country_year_list(df)

        selected_year = st.sidebar.selectbox("Select Year", years)
        selected_country = st.sidebar.selectbox("Select Country", country)

        medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

        # Display appropriate titles based on user selections
        if selected_year == 'Overall' and selected_country == 'Overall':
            st.title("Overall Tally")
        elif selected_year != 'Overall' and selected_country == 'Overall':
            st.title("Medal Tally in " + str(selected_year) + " Olympics")
        elif selected_year == 'Overall' and selected_country != 'Overall':
            st.title(selected_country + " overall performance")
        else:
            st.title(selected_country + " performance in " + str(selected_year) + " Olympics")

        # Display the medal tally table
        st.table(medal_tally)

    # Overall Analysis
    elif user_menu == "Overall Analysis":
        editions = df["Year"].unique().shape[0] - 1
        cities = df["City"].unique().shape[0]
        sports = df["Sport"].unique().shape[0]
        events = df["Event"].unique().shape[0]
        athletes = df["Name"].unique().shape[0]
        nations = df["region"].unique().shape[0]

        st.title("Top statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Editions")
            st.title(editions)
        with col2:
            st.header("Cities")
            st.title(cities)
        with col3:
            st.header("Sports")
            st.title(sports)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Events")
            st.title(events)
        with col2:
            st.header("Athletes")
            st.title(athletes)
        with col3:
            st.header("Nations")
            st.title(nations)

        # Participating Nations over time
        nations_over_time = helper.data_over_time(df, 'region')
        fig = px.line(nations_over_time, x="Edition", y="region")
        st.title("Participating Nations over the years")
        st.plotly_chart(fig)

        # Events over time
        events_over_time = helper.data_over_time(df, 'Event')
        fig = px.line(events_over_time, x="Edition", y="Event")
        st.title("Events over the years")
        st.plotly_chart(fig)

        # Athletes over time
        athlete_over_time = helper.data_over_time(df, 'Name')
        fig = px.line(athlete_over_time, x="Edition", y="Name")
        st.title("Athletes over the years")
        st.plotly_chart(fig)

        # Heatmap for number of events per sport
        st.title("No. of Events over time (Every Sport)")
        fig, ax = plt.subplots(figsize=(20, 20))
        event_pivot = df.drop_duplicates(['Year', 'Sport', 'Event']).pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int')
        sns.heatmap(event_pivot, annot=True, ax=ax)
        st.pyplot(fig)

        # Most successful athletes
        st.title("Most successful Athletes")
        sport_list = df['Sport'].unique().tolist()
        sport_list.sort()
        sport_list.insert(0, 'Overall')

        selected_sport = st.selectbox('Select a Sport', sport_list)
        most_successful = helper.most_successful(df, selected_sport)
        st.table(most_successful)

    # Country-wise Analysis
    elif user_menu == 'Country-wise Analysis':
        st.sidebar.title('Country-wise Analysis')
        country_list = df['region'].dropna().unique().tolist()
        country_list.sort()

        selected_country = st.sidebar.selectbox('Select a Country', country_list)

        # Medal tally over the years for the selected country
        country_df = helper.yearwise_medal_tally(df, selected_country)
        fig = px.line(country_df, x="Year", y="Medal")
        st.title(f"{selected_country} Medal Tally over the years")
        st.plotly_chart(fig)

        # Sports in which the country excels
        st.title(f"{selected_country} excels in the following sports")
        pt = helper.country_event_heatmap(df, selected_country)
        if pt.empty:
            st.warning(f"No data available for {selected_country} to plot the heatmap.")
        else:
            fig, ax = plt.subplots(figsize=(20, 20))
            sns.heatmap(pt, annot=True, ax=ax)
            st.pyplot(fig)

        # Top 10 athletes from the selected country
        st.title(f"Top 10 Athletes of {selected_country}")
        # Get the top 10 athletes for the selected country
        top10_df = helper.most_successful_countrywise(df, selected_country)
        st.table(top10_df)

    # Athlete-wise Analysis
    elif user_menu == 'Athlete wise Analysis':
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])

        # Distribution of Age
        x1 = athlete_df['Age'].dropna()
        x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
        x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
        x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

        fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'], show_hist=False, show_rug=False)
        fig.update_layout(autosize=False, width=1000, height=600)
        st.title("Distribution of Age")
        st.plotly_chart(fig)

        # Age distribution with respect to sports (Gold Medalists)
        st.title("Distribution of Age wrt Sports (Gold Medalists)")
        famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                         'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                         'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                         'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                         'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                         'Tennis', 'Golf', 'Softball', 'Archery',
                         'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                         'Rhythmic Gymnastics', 'Rugby Sevens',
                         'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
        x = []
        name = []

        for sport in famous_sports:
            temp_df = athlete_df[athlete_df['Sport'] == sport]
            x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
            name.append(sport)

        fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
        fig.update_layout(autosize=False, width=1000, height=600)
        st.plotly_chart(fig)

        # Height vs Weight analysis
        st.title('Height Vs Weight')
        sport_list = df['Sport'].unique().tolist()
        sport_list.sort()
        sport_list.insert(0, 'Overall')



        # selected_sport = st.selectbox('Select a Sport', sport_list)
        # temp_df = helper.weight_v_height(df, selected_sport)
        # fig, ax = plt.subplots()
        # sns.scatterplot(data=temp_df, x='Weight', y='Height', hue='Medal', style='Sex', s=60, ax=ax)
        # st.pyplot(fig)

        selected_sport = st.selectbox('Select a Sport', sport_list)

    # Call the function and unpack the return values
        temp_df, error_message = helper.weight_v_height(df, selected_sport)

    # Debug: Check the returned values
        st.write("Debug: error_message:", error_message)
        if error_message:
            st.write(error_message)
        elif isinstance(temp_df, pd.DataFrame):
            fig, ax = plt.subplots()
            sns.scatterplot(data=temp_df, x='Weight', y='Height', hue='Medal', style='Sex', s=60, ax=ax)
            st.pyplot(fig)
        else:
            st.write("Something went wrong. temp_df is not a valid DataFrame.")



        # Men vs Women participation over the years
        st.title("Men Vs Women Participation Over the Years")
        final = helper.men_vs_women(df)
        fig = px.line(final, x="Year", y=["Male", "Female"])
        fig.update_layout(autosize=False, width=1000, height=600)
        st.plotly_chart(fig)

# Cricket Analysis 

if st.session_state.selected_sport == "Cricket":
    st.title("Cricket Analysis")
    user_menu = st.sidebar.radio(
        'Select an Option',
        ('Tournament seasons and results', 'Overall Analysis', 'Player-wise Analysis', 'Team-wise Analysis')
    )
    if user_menu == 'Tournament seasons and results':
        data1 = pd.read_csv("tornament.csv")
        st.table(data1)
    
    elif user_menu == "Overall Analysis":
        Seasons = data["season"].nunique()
        Total_Teams = data["team1"].nunique()
        Total_Batters = data["batter"].nunique()
        Total_Bowlers = data["bowler"].nunique()
        venues = data["venue"].nunique()
        cities = data["city"].nunique()

        st.title("Top Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Seasons")
            st.title(Seasons)
        with col2:
            st.header("Teams")
            st.title(Total_Teams)
        with col3:
            st.header("Batters")
            st.title(Total_Batters)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Bowlers")
            st.title(Total_Bowlers)
        with col2:
            st.header("Cities")
            st.title(cities)
        with col3:
            st.header("Venues")
            st.title(venues)
        
        winning_team_new = helper.winning_team(data1)
        fig = px.bar(winning_team_new, x="Winner", y="count", 
             labels={"Winner": "Team", "count": "Number of Wins"},
             color="Winner",  
             text="count") 
        st.title("IPL Teams with the Highest Number of Titles")
        st.plotly_chart(fig)


        lossing_team_new = helper.loosing_team(data1)
        fig = px.bar(lossing_team_new, x="Runner-up", y="count",
                     labels={"Runner-up": "Team", "count": "Number of lost"},
                     color="Runner-up"
                     )
        st.title("Most Runner-Up Finishes in IPL")
        st.plotly_chart(fig)

        Ipl_team_statics=pd.read_csv("Statics_team.csv")
        st.title("Win-Loss Ratios and Performance Percentages of IPL Teams (2008-2024)")
        st.table(Ipl_team_statics)

        #Barchats
        #loss
        fig = px.bar(Ipl_team_statics, x="Team",y="Lost",
                     labels={"Team": "Teams", "Lost": "Number of lost by a team"},
                     color="Team",  
                     text="Lost"
                     )
        st.title("Most Matches Lost by Teams in IPL")
        st.plotly_chart(fig)
       #Win
        fig = px.bar(Ipl_team_statics, x="Team",y="Won",
                     labels={"Team": "Teams", "Win": "Number of wins by a team"},
                     color="Team",  
                     text="Won"
                     )
        st.title("Most Matches Won by Teams in IPL")
        st.plotly_chart(fig)
         #lost percentage
        fig = px.bar(Ipl_team_statics, x="Team",y="%L",
                     labels={"Team": "Teams", "%L": "Loss Percentage"},
                     color="Team",  
                     text="%L"
                     )
        st.title("Loss Percentage of Teams in IPL")
        st.plotly_chart(fig)
        #win percentage
        fig = px.bar(Ipl_team_statics, x="Team",y="%W",
                     labels={"Team": "Teams", "%W": "Win Percentage"},
                     color="Team",  
                     text="%W"
                     )
        st.title("Win Percentage of Teams in IPL")
        st.plotly_chart(fig)

            
    elif user_menu == 'Player-wise Analysis':
        player= helper.list(data)
        selected_player = st.sidebar.selectbox("Select Player", player)
        player2= helper.calculate_player_card67(data, selected_player)
        st.title(f"Player Card: {selected_player}")
        st.table(player2)

    elif user_menu == 'Team-wise Analysis':
        year, team = helper.list2(data)  # Ensure helper.list2 returns proper values
        selected_team = st.sidebar.selectbox("Select Team", team)
        selected_year = st.sidebar.selectbox("Select Season", year)

    # Fetch team-wise data
        team_data = helper.teams(data, selected_year, selected_team)
        st.title(f"{selected_team}: in : {selected_year}")
        st.table(team_data )



