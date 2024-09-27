import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit page configuration
st.set_page_config(
    page_title="Comprehensive Scorecard Generator",  # Page title in the browser tab
    layout="wide"  # Sets the layout to wide
)

# Streamlit app layout
st.title("Comprehensive Scorecard Generator")

# File uploader for the CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

# Custom function for styling KPI cards
def display_kpi_card(title, value, delta=None, delta_color="normal", icon=None, color="lightblue"):
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 10px; border-radius: 5px;">
            <div style="font-size: 20px; color: black;">{title}</div>
            <div style="font-size: 28px; font-weight: bold; color: black;">{value}</div>
            {'<div style="font-size: 16px; color: green;">' + icon + '</div>' if icon else ''}
            {'<div style="font-size: 16px; color:' + delta_color + ';">' + delta + '</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

# Function to validate if a dataframe is empty or not
def is_valid_dataframe(df):
    return not df.empty and len(df.columns) > 0

# Check if a CSV file is uploaded
if uploaded_file is not None:
    try:
        # Read the uploaded CSV file into a pandas dataframe
        df = pd.read_csv(uploaded_file)

        # Validate the dataframe
        if not is_valid_dataframe(df):
            st.error("Uploaded file is empty or does not contain valid data.")
        else:
            # Function to generate scorecard for unique usernames
            def generate_unique_username_scorecard(df):
                unique_usernames = df['username'].nunique()
                display_kpi_card("Active Players", unique_usernames, icon="👤", color="#6fa8dc")

            # Function to generate scorecard for total cost
            def generate_total_cost_scorecard(df):
                total_cost = df['total_cost'].sum()
                display_kpi_card("Total Cost", f"${total_cost:,.2f}", icon="💰", color="#ff9999")
                return total_cost

            # Function to generate scorecard for total reward
            def generate_total_reward_scorecard(df):
                total_reward = df['rewards'].sum()
                display_kpi_card("Total Reward", f"${total_reward:,.2f}", icon="🏆", color="#b6d7a8")
                return total_reward

            # Function to generate scorecard for profit margin
            def generate_profit_margin_scorecard(total_cost, total_reward):
                if total_cost != 0:
                    profit_margin = ((total_reward - total_cost) / total_cost) * 100
                    display_kpi_card("Profit Margin", f"{profit_margin:.2f}%", icon="📈", color="#c9daf8")
                else:
                    display_kpi_card("Profit Margin", "N/A", icon="📈", color="#c9daf8")

            # Function to generate summary table
            def generate_summary_table(df):
                summary = df.groupby(['ref_provider', 'product_name_en']).agg(
                    unique_player_count=pd.NamedAgg(column='username', aggfunc='nunique'),
                    total_cost=pd.NamedAgg(column='total_cost', aggfunc='sum'),
                    total_reward=pd.NamedAgg(column='rewards', aggfunc='sum')
                )
                summary['total_winloss'] = summary['total_reward'] - summary['total_cost']
                summary = summary.reset_index()
                st.dataframe(summary)

            # Function to generate top 10 winners by net gain/loss
            def generate_top_winners_bar_chart(df):
                user_summary = df.groupby('username').agg(
                    total_rewards=pd.NamedAgg(column='rewards', aggfunc='sum'),
                    total_cost=pd.NamedAgg(column='total_cost', aggfunc='sum')
                )
                user_summary['net_gain_loss'] = user_summary['total_rewards'] - user_summary['total_cost']
                top_winners = user_summary.sort_values(by='net_gain_loss', ascending=False).head(10).reset_index()
                fig = px.bar(
                    top_winners, 
                    x='net_gain_loss', 
                    y='username', 
                    orientation='h', 
                    title="Top 10 Winners by Net Gain/Loss",
                    labels={'net_gain_loss': 'Net Gain/Loss', 'username': 'Username'},
                    color='net_gain_loss',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig)

            # Display the uploaded CSV file
            st.write("Uploaded Data")
            st.dataframe(df)

            # Display the summary table
            st.subheader("Summary Table by ref_provider and product_name_en")
            generate_summary_table(df)

            # Create four columns for the KPI cards
            col1, col2, col3, col4 = st.columns(4)

            # Place the Total Rewards Amount scorecard in the first column
            with col1:
                total_reward = generate_total_reward_scorecard(df)

            # Place the Total Costs Amount scorecard in the second column
            with col2:
                total_cost = generate_total_cost_scorecard(df)

            # Place the unique username scorecard in the third column
            with col3:
                generate_unique_username_scorecard(df)

            # Place the profit margin scorecard in the fourth column
            with col4:
                generate_profit_margin_scorecard(total_cost, total_reward)

            # Add vertical space between sections
            st.write("")  # Adds a blank line
            st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more space if needed

            # Place the top winners bar chart in the main area
            st.subheader("Top 10 Winners by Net Gain/Loss")
            generate_top_winners_bar_chart(df)
    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV file is empty. Please upload a valid file.")
    except pd.errors.ParserError:
        st.error("Error parsing the CSV file. Please ensure it is formatted correctly.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
else:
    st.info("Please upload a CSV file to generate a scorecard.")
