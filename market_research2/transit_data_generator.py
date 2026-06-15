def generate_raw_research_ledger(market_date_str, market_tz, birth_override=None):
    """
    Generates a massive, high-precision matrix containing the absolute 
    coordinates of every market body and birth body for every minute.
    """
    birth = birth_override if birth_override is not None else calculate_chart_vector(
        DEFAULT_BIRTH_DATE, DEFAULT_BIRTH_TIME, DEFAULT_BIRTH_TZ, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT
    )
    
    market_base = datetime.datetime.strptime(market_date_str, "%Y.%m.%d").date()
    current_local = datetime.datetime.combine(market_base, datetime.time(9, 0, 0))
    end_local = datetime.datetime.combine(market_base, datetime.time(16, 20, 0))
    
    raw_records = []
    
    while current_local <= end_local:
        time_str = current_local.strftime("%H:%M:%S")
        transit = calculate_chart_vector(market_date_str, time_str, market_tz, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ALT)
        
        row = {"Time": time_str}
        
        # Inject precise Market positions
        for t_name, t_pos in transit.items():
            row[f"M_{t_name}_Total"] = t_pos["Total"]
            row[f"M_{t_name}_D1_Sign"] = t_pos["D1_Sign"]
            row[f"M_{t_name}_D1_Deg"] = t_pos["D1_Deg"]
            row[f"M_{t_name}_D9_Sign"] = t_pos["D9_Sign"]
            row[f"M_{t_name}_D9_Deg"] = t_pos["D9_Deg"]
            row[f"M_{t_name}_Nak_Deg"] = t_pos["Nak_Deg"]
            
        # Inject precise Birth positions for absolute comparison flexibility
        for b_name, b_pos in birth.items():
            row[f"B_{b_name}_Total"] = b_pos["Total"]
            row[f"B_{b_name}_D1_Sign"] = b_pos["D1_Sign"]
            row[f"B_{b_name}_D1_Deg"] = b_pos["D1_Deg"]
            row[f"B_{b_name}_D9_Sign"] = b_pos["D9_Sign"]
            row[f"B_{b_name}_D9_Deg"] = b_pos["D9_Deg"]
            
        raw_records.append(row)
        current_local += datetime.timedelta(minutes=1)
        
    return pd.DataFrame(raw_records)
