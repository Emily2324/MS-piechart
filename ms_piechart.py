import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Market Share Pie Chart", layout="wide")
st.title("Market Share Pie Chart Generator")

# Upload Excel file
file = st.file_uploader("Upload Excel File", type="xlsx")

# Country input
country = st.text_input("Enter Country Name").strip().title()

if file and country:
    try:
        # Load and prepare data
        df = pd.read_excel(file)
        df["Country/Territory"].fillna(method="ffill", inplace=True)

        if country not in df["Country/Territory"].values:
            st.error(f"'{country}' is not an available country.")
        else:
            country_df = df[df["Country/Territory"] == country].copy()
            country_df = country_df[country_df["Market Share Q4 2024"].notna()]
            country_df["Share"] = country_df["Market Share Q4 2024"].str.rstrip('%').astype(float)
            country_df = country_df.sort_values("Share", ascending=True)

            explode = [0.03] * len(country_df)
            colors = plt.cm.Set3(range(len(country_df)))

            # Plot pie chart
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(7, 7), facecolor='black')

            def autopct_fn(pct):
                return f"{pct:.1f}%" if pct >= 3 else ""

            wedges, texts, autotexts = ax.pie(
                country_df["Share"],
                autopct=autopct_fn,
                startangle=140,
                explode=explode,
                colors=colors,
                shadow=True,
                textprops={'fontsize': 12}
            )

            for i, (wedge, pct) in enumerate(zip(wedges, country_df["Share"])):
                if pct < 3:
                    ang = (wedge.theta2 + wedge.theta1)/2
                    x = wedge.r * 1.2 * math.cos(math.radians(ang))
                    y = wedge.r * 1.2 * math.sin(math.radians(ang))
                    ax.annotate(
                        f"{pct:.1f}%",
                        xy=(x, y),
                        ha='center',
                        va='center',
                        color='white',
                        fontsize=10,
                        fontweight='bold'
                    )

            ax.legend(wedges, country_df["Company"], title="Company", loc="center left", bbox_to_anchor=(1, 0.5))
            ax.set_title(f"{country}", fontsize=18, weight='bold', color='white')
            plt.axis('equal')
            plt.tight_layout()
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
