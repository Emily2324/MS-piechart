import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# Set browser tab title and layout
st.set_page_config(page_title="Market Share Chart Generator", layout="wide")
st.title("Market Share Chart Generator")

# Upload Excel file
file = st.file_uploader("Upload Excel File", type="xlsx")

# Country input
country = st.text_input("Enter Country Name").strip()

# Add chart type and metric selection
chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart"])
metric_option = st.selectbox("Select Market Share Metric", 
                             ["Subscription Market Share", "Revenue Market Share"])
year = st.selectbox("Select Year", ["2020", "2021", "2022", "2023", "2024",
                                    "2025", "2026"])
quarter = st.selectbox("Select Quarter", ["Q4", "Q3", "Q2", "Q1"])
bg_color = st.selectbox("Select Background Color", ["Black", "White"])


# Map dropdown selection to actual Excel column name
#column_suffix = f"{quarter} {year}"
metric_column_map = {
    "Subscription Market Share": f"Market Share {quarter} {year}",
    "Revenue Market Share": f"Market Share {quarter} {year}"
}

if file and country:
    try:
        df = pd.read_excel(file)
        
        # Validate country column
        if "Country/Territory" not in df.columns:
            raise KeyError("Missing column: 'Country/Territory'")
        
        df["Country/Territory"].fillna(method="ffill", inplace=True)

        match = df["Country/Territory"].astype(str).str.strip().str.lower() == country.lower()
        if not match.any():
            st.error(f"'{country}' is not an available country.")
        else:
            official_name = df.loc[match, "Country/Territory"].iloc[0]
            country_df = df[match].copy()

            selected_column = metric_column_map[metric_option]
            if selected_column not in df.columns:
                raise KeyError(f"Missing column: '{selected_column}'")

            country_df = country_df[country_df[selected_column].notna()]
            country_df["Share"] = country_df[selected_column].str.rstrip('%').astype(float)
            country_df = country_df.sort_values("Share", ascending=True)

            colors = plt.cm.Set3(range(len(country_df)))
            plt.style.use("dark_background")
            # Set style and color based on background selection
            if bg_color == "Black":
                plt.style.use("dark_background")
                fig_facecolor = 'black'
                title_color = 'white'
                in_pie_color = 'black'
                out_pie_color = 'white'
                bar_text_color = 'white'
            else:
                plt.style.use("default")
                fig_facecolor = 'white'
                title_color = 'black'
                in_pie_color = 'black'
                out_pie_color = 'black'
                bar_text_color = 'black'
            fig, ax = plt.subplots(figsize=(7, 7), facecolor=fig_facecolor)

            if chart_type == "Pie Chart":
                explode = [0.03] * len(country_df)

                def autopct_fn(pct):
                    return f"{pct:.1f}%" if pct >= 3 else ""
                wedges, texts, autotexts = ax.pie(
                    country_df["Share"],
                    autopct=autopct_fn,
                    startangle=140,
                    explode=explode,
                    colors=colors,
                    shadow=True,
                    textprops={'fontsize': 12, 'color': in_pie_color, 'fontweight': 'bold'}
                )

                for i, (wedge, pct) in enumerate(zip(wedges, country_df["Share"])):
                    if pct < 3:
                        ang = (wedge.theta2 + wedge.theta1) / 2
                        x = wedge.r * 1.2 * math.cos(math.radians(ang))
                        y = wedge.r * 1.2 * math.sin(math.radians(ang))
                        ax.annotate(
                            f"{pct:.1f}%",
                            xy=(x, y),
                            ha='center',
                            va='center',
                            color=out_pie_color,
                            fontsize=10,
                            fontweight='bold'
                        )

                ax.legend(wedges, country_df["Company"], title="Company", 
                          loc="center left", bbox_to_anchor=(1, 0.5))
                ax.set_title(f"{official_name} – {metric_option}({year}{quarter})", fontsize=18,
                              weight='bold', color=title_color)
                plt.axis('equal')

            else:  # Bar chart
                ax.set_title(f"{official_name} – {metric_option}({year}{quarter})", fontsize=16,
                              weight='bold', color=title_color)
                bars = ax.bar(country_df["Company"], country_df["Share"], 
                              color=colors, width=0.5)
                ax.set_ylabel("Market Share (%)", fontsize=12)
                ax.set_xticklabels(country_df["Company"], rotation=45, ha='right')

                # Add data labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f"{height:.1f}%", 
                            ha='center', va='bottom', color= bar_text_color, fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
