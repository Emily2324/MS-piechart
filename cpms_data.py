import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np

st.set_page_config(page_title="Data Analyzer", layout="wide")

def run_market_share_app():
  # Set browser tab title and layout
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
def run_company_profile_app():
    st.title("Company Profile Analyzer")
    files = st.file_uploader(
        "Upload company profile files", 
        type="xlsx", 
        accept_multiple_files=True
    )
    if not files:
      st.info("Please upload at least one company profile file to continue.")
      return
    corp_name = st.text_input("Enter Corporation Name").strip()
    # quarter dropdown (adjust year range as desired)
    years = list(range(2019, 2027))
    quarter_options = [f"Q{q} {y}" for y in years for q in (1,2,3,4)]
    curr_q = st.selectbox("Select Current Quarter", quarter_options)
    comp_type = st.selectbox("Select Comparison Type", ["QoQ", "YoY"])
    show_line = st.checkbox("Show % Change Line", value=False)
    show_grid = st.checkbox("Show Background Gridlines", value=False)

    # Compute comparison label
    def get_prev_q(qstr):
        q, y = qstr.split()
        year = int(y)
        num  = int(q[1])
        return f"Q4 {year-1}" if num == 1 else f"Q{num-1} {year}"

    def get_prev_y(qstr):
        q, y = qstr.split()
        return f"{q} {int(y)-1}"

    prev_q = get_prev_q(curr_q) if comp_type=="QoQ" else get_prev_y(curr_q)

    # Restrict to chosen metrics
    desired = [
        "Total subscriptions",
        "4G penetration", "5G penetration",
        "4G subscriptions", "5G subscriptions",
        "Market share - subscriptions",
        "Service revenues", "Data revenues", "Data share of service revenues",
        "ARPU", "Data ARPU", "Data share of ARPU",
        "CAPEX", "CAPEX to revenue ratio", "CAPEX per subscriber"
    ]
    percent_metrics = {
        "4G penetration", "5G penetration",
        "Market share - subscriptions",
        "Data share of service revenues",
        "Data share of ARPU",
        "CAPEX to revenue ratio"
    }

    # Peek first file to build metric dropdown
    df0 = pd.read_excel(files[0], index_col=0)
    available = [m for m in desired if m in df0.index]
    metric = st.selectbox("Select Metric", available)
    if not metric:
        st.error("No valid metrics found in the first file.")
        return
    
    def parse_val(x):
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return np.nan
        # percent metrics → always return percent units (e.g. 3.0 for 3%)
        if metric in percent_metrics:
            if isinstance(x, str) and "%" in x:
                return float(x.rstrip("%"))
            else:
                return float(x) * 100  # covers numeric 0.03 → 3.0
        # everything else → plain number
        if isinstance(x, str):
            return float(x.replace(",", ""))
        return float(x)
    
    # Gather data
    results = []
    def parse_val(x):
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return np.nan
        if isinstance(x, str):
            x = x.strip()
            if "%" in x:
                return float(x.rstrip("%"))
            return float(x.replace(",", ""))
        return float(x)

    for file in files:
        # Extract operator name from filename
        name = file.name.removesuffix(".xlsx")
        prefix = "Company Profile Sheet "
        company = name[len(prefix):]

        df = pd.read_excel(file, index_col=0)
        # Safely grab both quarters (may not exist)
        v_curr = df.at[metric, curr_q] if metric in df.index and curr_q in df.columns else None
        v_prev = df.at[metric, prev_q] if metric in df.index and prev_q in df.columns else None

        n_curr = parse_val(v_curr)
        n_prev = parse_val(v_prev)
        pct_chg = ((n_curr - n_prev) / n_prev * 100) if (n_prev and not np.isnan(n_prev)) else np.nan

        results.append({
            "company":     company,
            "prev":        n_prev,
            "curr":        n_curr,
            "pct_change":  pct_chg
        })

    # Plot
    df_res = pd.DataFrame(results)
    n = len(df_res)
    denom = max(n, 6)
    bar_width = 0.8 / denom 
    gap       = bar_width * 0.3
    offset    = bar_width/2 + gap/2
    x           = np.arange(n)
    prev_color = 'skyblue'
    curr_color = 'royalblue'
    line_color = 'lightgreen'
    fig, ax = plt.subplots(figsize=(8,5))
    # previous quarter bars (light blue)
    ax.bar(
        x - offset,
        df_res["prev"],
        width=bar_width,
        label=prev_q,
        color=prev_color
    )
    # current quarter bars (dark blue)
    ax.bar(
        x + offset,
        df_res["curr"],
        width=bar_width,
        label=curr_q,
        color=curr_color
    )
    if show_grid:
        ax.grid(
            True, 
            axis = 'y',
            linestyle = '--',
            linewidth = 0.5,
            alpha = 0.3
        )
    ax.set_xticks(x)
    ax.set_xticklabels(df_res["company"], rotation=45, ha="right")
    ax.set_ylabel(metric)
    ax.legend(loc="upper left")

    if metric in percent_metrics:
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}%"))

    if show_line:
        ax2 = ax.twinx()
        ax2.plot(
            x,
            df_res["pct_change"],
            marker="o",
            markersize = 3,
            color=line_color,
            label="% Change"
        )
        ax2.set_ylabel("% Change")
        ax2.legend(loc="upper right")

    plt.title(f"{corp_name} — {metric} {curr_q} vs {prev_q}")
    plt.tight_layout()
    st.pyplot(fig)

def main():
    # initialize mode
    if "mode" not in st.session_state:
        st.session_state.mode = None

    st.title("Data Analyzer")
    st.write("Select Data type:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Market Share"):
            st.session_state.mode = "market"
    with col2:
        if st.button("Company Profile"):
            st.session_state.mode = "profile"

    # dispatch
    if st.session_state.mode == "market":
        run_market_share_app()
    elif st.session_state.mode == "profile":
        run_company_profile_app()
    else:
        st.write("Please choose a data type above.")

if __name__ == "__main__":
    main()
