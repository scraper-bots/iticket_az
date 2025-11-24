#!/usr/bin/env python3
"""
Generate insightful charts from iTicket.az event data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import glob
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create charts directory
os.makedirs('charts', exist_ok=True)

# Load the most recent CSV file
csv_files = glob.glob('iticket_events_*.csv')
if not csv_files:
    print("Error: No CSV files found!")
    exit(1)

latest_csv = sorted(csv_files)[-1]
print(f"Loading data from: {latest_csv}")
df = pd.read_csv(latest_csv)

print(f"Total events: {len(df)}")
print(f"Columns: {df.columns.tolist()}\n")

# Convert date columns
date_columns = ['event_starts_at', 'event_ends_at', 'sell_starts_at', 'sell_ends_at']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Extract useful date features
df['event_month'] = df['event_starts_at'].dt.to_period('M').astype(str)
df['event_day_of_week'] = df['event_starts_at'].dt.day_name()
df['event_hour'] = df['event_starts_at'].dt.hour

# Calculate event duration in hours
df['duration_hours'] = (df['event_ends_at'] - df['event_starts_at']).dt.total_seconds() / 3600

print("Generating charts...\n")

# Chart 1: Events by Category
print("1. Events by Category Distribution")
plt.figure(figsize=(12, 6))
category_counts = df['category_slug'].value_counts()
ax = category_counts.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('Event Distribution by Category', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Category', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.xticks(rotation=45, ha='right')
for i, v in enumerate(category_counts.values):
    ax.text(i, v + 2, str(v), ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/01_events_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 2: Price Distribution
print("2. Ticket Price Distribution")
plt.figure(figsize=(12, 6))
prices = df[['min_price', 'max_price']].values.flatten()
prices = prices[~np.isnan(prices)]
plt.hist(prices, bins=50, color='mediumseagreen', edgecolor='black', alpha=0.7)
plt.title('Distribution of Ticket Prices', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Price (AZN)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.axvline(prices.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {prices.mean():.2f} AZN')
plt.legend()
plt.tight_layout()
plt.savefig('charts/02_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 3: Events Timeline
print("3. Events Timeline")
plt.figure(figsize=(14, 6))
events_by_month = df.groupby('event_month').size().sort_index()
plt.plot(events_by_month.index, events_by_month.values, marker='o', linewidth=2,
         markersize=8, color='darkblue', markerfacecolor='lightblue', markeredgewidth=2)
plt.title('Event Count Over Time', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/03_events_timeline.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 4: Top 15 Venues by Event Count
print("4. Top Venues by Event Count")
plt.figure(figsize=(12, 8))
top_venues = df['venue_name'].value_counts().head(15)
ax = top_venues.plot(kind='barh', color='coral', edgecolor='black')
plt.title('Top 15 Venues by Number of Events', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Number of Events', fontsize=12)
plt.ylabel('Venue', fontsize=12)
for i, v in enumerate(top_venues.values):
    ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/04_top_venues.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 5: Average Price by Category
print("5. Average Price by Category")
plt.figure(figsize=(12, 6))
avg_price_by_cat = df.groupby('category_slug')[['min_price', 'max_price']].mean()
x = np.arange(len(avg_price_by_cat))
width = 0.35
fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, avg_price_by_cat['min_price'], width, label='Min Price',
               color='lightcoral', edgecolor='black')
bars2 = ax.bar(x + width/2, avg_price_by_cat['max_price'], width, label='Max Price',
               color='lightblue', edgecolor='black')
ax.set_title('Average Ticket Prices by Category', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Average Price (AZN)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(avg_price_by_cat.index, rotation=45, ha='right')
ax.legend()
plt.tight_layout()
plt.savefig('charts/05_avg_price_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 6: Events by Age Restriction
print("6. Events by Age Restriction")
plt.figure(figsize=(10, 6))
age_counts = df['age_limit'].value_counts().sort_index()
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(age_counts)))
ax = age_counts.plot(kind='bar', color=colors, edgecolor='black')
plt.title('Event Distribution by Age Restriction', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Age Limit', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.xticks(rotation=0)
for i, v in enumerate(age_counts.values):
    ax.text(i, v + 2, str(v), ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/06_age_restrictions.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 7: Ticket Availability Distribution
print("7. Ticket Availability Distribution")
plt.figure(figsize=(12, 6))
availability = df['available_tickets_count'].dropna()
plt.hist(availability, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.title('Distribution of Available Tickets per Event', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Available Tickets', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.axvline(availability.median(), color='red', linestyle='--', linewidth=2,
            label=f'Median: {availability.median():.0f}')
plt.legend()
plt.tight_layout()
plt.savefig('charts/07_ticket_availability.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 8: Price Range by Category (Box Plot)
print("8. Price Range by Category")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
df_melted = df.melt(id_vars=['category_slug'], value_vars=['min_price', 'max_price'],
                    var_name='price_type', value_name='price')
df_melted = df_melted.dropna(subset=['price'])
sns.boxplot(data=df_melted, y='category_slug', x='price', hue='price_type', ax=ax1, palette='Set2')
ax1.set_title('Price Range Distribution by Category', fontsize=14, fontweight='bold')
ax1.set_xlabel('Price (AZN)', fontsize=11)
ax1.set_ylabel('Category', fontsize=11)
ax1.legend(title='Price Type')

# Violin plot as alternative view
sns.violinplot(data=df_melted, y='category_slug', x='price', ax=ax2, color='lightcoral')
ax2.set_title('Price Distribution Density by Category', fontsize=14, fontweight='bold')
ax2.set_xlabel('Price (AZN)', fontsize=11)
ax2.set_ylabel('')
plt.tight_layout()
plt.savefig('charts/08_price_range_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 9: Events by Day of Week
print("9. Events by Day of Week")
plt.figure(figsize=(12, 6))
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_counts = df['event_day_of_week'].value_counts().reindex(day_order, fill_value=0)
colors_days = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else '#4ECDC4' for day in day_order]
ax = day_counts.plot(kind='bar', color=colors_days, edgecolor='black')
plt.title('Event Distribution by Day of Week', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Day of Week', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.xticks(rotation=45, ha='right')
for i, v in enumerate(day_counts.values):
    ax.text(i, v + 2, str(v), ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/09_events_by_day.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 10: Venue Geographic Distribution
print("10. Venue Geographic Distribution")
plt.figure(figsize=(12, 8))
venue_data = df[['venue_name', 'venue_latitude', 'venue_longitude']].drop_duplicates()
venue_data = venue_data.dropna(subset=['venue_latitude', 'venue_longitude'])
venue_data['venue_latitude'] = pd.to_numeric(venue_data['venue_latitude'], errors='coerce')
venue_data['venue_longitude'] = pd.to_numeric(venue_data['venue_longitude'], errors='coerce')
venue_data = venue_data.dropna()
plt.scatter(venue_data['venue_longitude'], venue_data['venue_latitude'],
           s=200, alpha=0.6, c='red', edgecolors='black', linewidths=2)
plt.title('Venue Geographic Distribution (Baku)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Longitude', fontsize=12)
plt.ylabel('Latitude', fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/10_venue_map.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 11: Event Duration Analysis
print("11. Event Duration Analysis")
plt.figure(figsize=(12, 6))
duration_data = df['duration_hours'].dropna()
duration_data = duration_data[duration_data > 0]  # Remove invalid durations
plt.hist(duration_data, bins=30, color='mediumorchid', edgecolor='black', alpha=0.7)
plt.title('Distribution of Event Durations', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Duration (Hours)', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.axvline(duration_data.median(), color='red', linestyle='--', linewidth=2,
            label=f'Median: {duration_data.median():.1f} hours')
plt.legend()
plt.tight_layout()
plt.savefig('charts/11_event_duration.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 12: Availability vs Price Correlation
print("12. Ticket Availability vs Price Relationship")
fig, ax = plt.subplots(figsize=(12, 6))
scatter_data = df[['available_tickets_count', 'max_price', 'category_slug']].dropna()
categories = scatter_data['category_slug'].unique()
colors_cat = plt.cm.tab10(np.linspace(0, 1, len(categories)))
for i, cat in enumerate(categories):
    cat_data = scatter_data[scatter_data['category_slug'] == cat]
    ax.scatter(cat_data['max_price'], cat_data['available_tickets_count'],
              alpha=0.6, s=80, label=cat, color=colors_cat[i], edgecolors='black', linewidths=0.5)
ax.set_title('Ticket Availability vs Maximum Price by Category', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Maximum Price (AZN)', fontsize=12)
ax.set_ylabel('Available Tickets', fontsize=12)
ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/12_availability_vs_price.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 13: Event Start Time Distribution
print("13. Event Start Time Distribution")
plt.figure(figsize=(12, 6))
hour_counts = df['event_hour'].value_counts().sort_index()
plt.bar(hour_counts.index, hour_counts.values, color='teal', edgecolor='black', alpha=0.7)
plt.title('Events by Start Time (Hour of Day)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Hour (24-hour format)', fontsize=12)
plt.ylabel('Number of Events', fontsize=12)
plt.xticks(range(0, 24))
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/13_event_start_times.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 14: Category Distribution by Month (Stacked Bar)
print("14. Category Distribution Over Time")
category_by_month = df.groupby(['event_month', 'category_slug']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(14, 6))
category_by_month.plot(kind='bar', stacked=True, ax=ax, colormap='tab10', edgecolor='black', linewidth=0.5)
ax.set_title('Category Distribution Over Time', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Number of Events', fontsize=12)
ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('charts/14_category_by_month.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 15: Top 10 Most Expensive Events
print("15. Most Expensive Events")
plt.figure(figsize=(12, 8))
top_expensive = df.nlargest(10, 'max_price')[['slug', 'max_price', 'category_slug']].copy()
top_expensive['slug'] = top_expensive['slug'].str.replace('-', ' ').str.title()
colors_exp = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_expensive)))
ax = plt.barh(range(len(top_expensive)), top_expensive['max_price'], color=colors_exp, edgecolor='black')
plt.yticks(range(len(top_expensive)), top_expensive['slug'])
plt.title('Top 10 Most Expensive Events', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Maximum Price (AZN)', fontsize=12)
plt.ylabel('Event', fontsize=10)
for i, v in enumerate(top_expensive['max_price'].values):
    plt.text(v + 20, i, f'{v:.0f} AZN', va='center', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/15_most_expensive_events.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*50)
print("All charts generated successfully!")
print("Charts saved in: ./charts/")
print("="*50)
