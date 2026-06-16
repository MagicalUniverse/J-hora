def style_transit_df(df):
    def highlight_row(row):
        # 1. Color alternating days
        day = int(row['Entry'].split()[0])
        bg_color = '#f0f0f0' if day % 2 == 0 else '#ffffff'
        
        # 2. Logic for Business Hours (09:00 - 16:20)
        # We check if the event overlaps with the window
        # Entry time <= 16:20 AND Exit time >= 09:00
        entry_time = row['Entry'].split()[1]
        exit_time = row['Exit'].split()[1]
        
        is_biz_hour = (entry_time <= "16:20") and (exit_time >= "09:00")
        
        text_weight = 'bold' if is_biz_hour else 'normal'
        text_color = '#000000' if is_biz_hour else '#666666'
        
        return [f'background-color: {bg_color}; font-weight: {text_weight}; color: {text_color}'] * len(row)

    return df.style.apply(highlight_row, axis=1)

# Apply the updated style to your result dataframe
style_transit_df(df_results)
