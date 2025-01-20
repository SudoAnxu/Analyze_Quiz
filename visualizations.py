import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_score_distribution(historical_data):
    """Plot the distribution of scores from historical quizzes."""
    plt.figure(figsize=(10, 6))
    sns.histplot(historical_data['score'], bins=10, kde=True)
    plt.title('Score Distribution of Historical Quizzes')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.axvline(historical_data['score'].mean(), color='red', linestyle='dashed', linewidth=1, label='Mean Score')
    plt.legend()
    plt.show()

def plot_accuracy_over_time(historical_data):
    """Plot accuracy over time for historical quizzes."""
    plt.figure(figsize=(10, 6))
    historical_data['submitted_at'] = pd.to_datetime(historical_data['submitted_at'])
    historical_data.sort_values('submitted_at', inplace=True)
    sns.lineplot(x='submitted_at', y='accuracy', data=historical_data, marker='o')
    plt.title('Accuracy Over Time')
    plt.xlabel('Date')
    plt.ylabel('Accuracy (%)')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

def plot_performance_by_topic(historical_data):
    """Plot average scores by quiz topic."""
    plt.figure(figsize=(12, 8))
    topic_performance = historical_data.groupby('quiz_topic')['score'].mean().reset_index()
    sns.barplot(x='score', y='quiz_topic', data=topic_performance, palette='viridis')
    plt.title('Average Score by Quiz Topic')
    plt.xlabel('Average Score')
    plt.ylabel('Quiz Topic')
    plt.show()

def plot_correct_incorrect_answers(current_data):
    """Plot the number of correct and incorrect answers for the current quiz."""
    labels = ['Correct Answers', 'Incorrect Answers']
    sizes = [current_data['correct_answers'], current_data['incorrect_answers']]
    colors = ['#4CAF50', '#FF5733']
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Current Quiz Performance')
    plt.show()

