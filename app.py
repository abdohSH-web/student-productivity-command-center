import pandas as pd 
data = {
    'Date': ['2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15',
             '2026-10-19', '2026-10-20', '2026-10-21', '2026-10-22'],
    'Category': ['English', 'Python', 'Python', 'Graphic Design',
                 'English', 'Python', 'Graphic Design', 'English'],
    'Subject': ['Third Conditional', 'OOP', 'Pandas groupby', 'Blending',
                'Vocabulary', 'File I/O', 'Typography', 'Essay writing'],
    'Time': [60, 45, 90, 30, 45, 120, 60, 30],
    'Understanding': [5, 3, 4, 2, 4, 5, 3, 4],
    'Notes': ['..', '...', '....', '.....', '..', '...', '....', '.....']
}

df = pd.DataFrame(data)
# print(df)

# total_mins_per_category = df.groupby('Category')['Time'].sum()
# print(total_mins_per_category)

#Convert to date
df['Date'] = pd.to_datetime(df['Date'])

# print(df['Date'].dt.month)
# print(df['Date'].dt.year)
# print(df['Date'].dt.day_name())
week = df['Date'].dt.isocalendar().week
mins_per_week = df.groupby(week)['Time'].sum()
print(mins_per_week)



