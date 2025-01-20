import requests
import pandas as pd
from visualizations import (
    plot_score_distribution,
    plot_accuracy_over_time,
    plot_performance_by_topic,
    plot_correct_incorrect_answers
)

# Define API endpoints
quiz_details_endpoint = "https://www.jsonkeeper.com/b/LLQT"
current_quiz_endpoint = "https://api.jsonserve.com/rJvd7g"
historical_quiz_endpoint = "https://api.jsonserve.com/XgAgFJ"

def fetch_data(url):
    """Fetch data from the given URL and return the JSON response."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from {url}: {e}"

def write_to_file(content, filename="output.txt"):
    """Write content to a text file."""
    with open(filename, "a") as file:
        file.write(content + "\n")

def analyze_quiz_details(quiz_details):
    """Analyze and write details of the quiz to a file."""
    quiz_info = quiz_details['quiz']
    output = ["Quiz General Information:"]
    output.append(f"Type: {quiz_info.get('type')}")
    output.append(f"Is Mandatory: {quiz_info.get('is_mandatory')}")
    output.append(f"Topic ID: {quiz_info.get('topic_id')}")
    output.append(f"Topic: {quiz_info.get('topic')}")
    output.append(f"Is Published: {quiz_info.get('is_published')}")
    
    # Analyze options
    output.append("\nOptions:")
    for option in quiz_info.get('options', []):     
        output.append(f"Option ID: {option['id']}, Description: {option['description']}, Is Correct: {option['is_correct']}")
    
    write_to_file("\n".join(output))

def analyze_current_quiz(current_quiz_data):
    """Analyze and write details of the current quiz to a file."""
    output = ["\nCurrent Quiz Information:"]
    output.append(f"User ID: {current_quiz_data['user_id']}")
    output.append(f"Score: {current_quiz_data['score']}")
    output.append(f"Accuracy: {current_quiz_data['accuracy']}")
    output.append(f"Correct Answers: {current_quiz_data['correct_answers']}")
    output.append(f"Incorrect Answers: {current_quiz_data['incorrect_answers']}")
    output.append(f"Total Questions: {current_quiz_data['total_questions']}")
    output.append(f"Rank: {current_quiz_data['rank_text']}")
    
    # Analyze response map
    output.append("\nUser Responses:")
    for question_id, selected_option in current_quiz_data['response_map'].items():
        output.append(f"Question ID: {question_id}, Selected Option: {selected_option}")

    write_to_file("\n".join(output))

def analyze_historical_quiz(historical_quiz_data):
    """Analyze and write details of the historical quiz to a file."""
    output = ["\nHistorical Quiz Information:"]
    
    # Checking if historical_quiz_data is a list
    if isinstance(historical_quiz_data, list):
        for quiz in historical_quiz_data:
            output.append(f"User ID: {quiz['user_id']}")
            output.append(f"Score: {quiz['score']}")
            output.append(f"Accuracy: {quiz['accuracy']}")
            output.append(f"Correct Answers: {quiz['correct_answers']}")
            output.append(f"Incorrect Answers: {quiz['incorrect_answers']}")
            output.append(f"Total Questions: {quiz['total_questions']}")
            output.append(f"Rank: {quiz['rank_text']}")
            
            # Analyze response map
            output.append("\nUser Responses:")
            for question_id, selected_option in quiz['response_map'].items():
                output.append(f"Question ID: {question_id}, Selected Option: {selected_option}")
            output.append("\n" + "-"*50)  # Separator for each quiz record
    else:
        output.append("Historical quiz data is not in the expected format.")
        
    write_to_file("\n".join(output))

def prepare_current_quiz_data(current_quiz_data):
    """Extract and organize current quiz data."""
    correct_answers = current_quiz_data['correct_answers']
    total_questions = current_quiz_data['total_questions']
    
    return {
        "user_id": current_quiz_data['user_id'],
        "score": current_quiz_data['score'],
        "accuracy": current_quiz_data['accuracy'].replace("%", ""),
        "correct_answers": correct_answers,
        "incorrect_answers": total_questions - correct_answers,  # Calculate incorrect answers
        "total_questions": total_questions,
        "response_map": current_quiz_data['response_map'],
        "quiz_id": current_quiz_data['quiz']['id'],
        "quiz_topic": current_quiz_data['quiz']['topic']
    }

def prepare_historical_quiz_data(historical_quiz_data):
    """Extract and organize historical quiz data from the last 5 quizzes."""
    prepared_data = []
    for quiz in historical_quiz_data:
        prepared_data.append({
            "user_id": quiz['user_id'],
            "score": quiz['score'],
            "accuracy": quiz['accuracy'].replace("%", ""),
            "correct_answers": quiz['correct_answers'],
            "total_questions": quiz['total_questions'],
            "response_map": quiz['response_map'],
            "quiz_id": quiz['quiz']['id'],
            "quiz_topic": quiz['quiz']['topic'],
            "submitted_at": quiz['submitted_at'],  # Include submitted_at here
            "created_at": quiz['created_at'],
            "updated_at": quiz['updated_at']
        })
    return pd.DataFrame(prepared_data)

def analyze_performance(current_data, historical_data):
    """Analyze the user performance data."""
    historical_accuracy = historical_data['accuracy'].astype(float).mean()
    
    # Identifying weak areas based on the defined score threshold
    weak_areas = historical_data[historical_data['score'] < 70]
    
    output = ["Current Performance:"]
    output.append(f"Score: {current_data['score']}, Accuracy: {current_data['accuracy']}")
    output.append(f"Historical Average Accuracy: {historical_accuracy:.2f}%")

    if not weak_areas.empty:
        output.append("Weak Areas:")
        output.append(weak_areas[['quiz_topic', 'score', 'quiz_id']].to_string(index=False))  # Ensure quiz_id is included
    else:
        output.append("No weak areas identified.")
    
    write_to_file("\n".join(output))  # Write performance analysis to file
    return weak_areas  # This will return an empty DataFrame if no weak areas are found

def generate_recommendations(weak_areas):
    recommendations = []
    
    # Checking if weak_areas is a DataFrame and not empty
    if isinstance(weak_areas, pd.DataFrame) and not weak_areas.empty:
        for index, row in weak_areas.iterrows():
            recommendations.append(f"Focus on improving your score in quiz ID {row['quiz_id']}.")
    else:
        recommendations.append("No major weaknesses identified. Keep up the good work!")

    return recommendations

def define_student_persona(historical_data):
    """Define the student persona based on historical data."""
    strengths = historical_data[historical_data['score'] >= 70]  # Define strengths assuming score >= 70 is good
    weaknesses = historical_data[historical_data['score'] < 70]  # Define weaknesses assuming score < 70 is bad
    
    persona = {
        "strengths": strengths['quiz_topic'].unique().tolist(),
        "weaknesses": weaknesses['quiz_topic'].unique().tolist()
    }
    
    output = [f"Student Persona:\nStrengths: {persona['strengths']}\nWeaknesses: {persona['weaknesses']}"]
    write_to_file("\n".join(output))
    return persona

def analyze_historical_quiz(historical_quiz_df):
    """Analyze and write details of the historical quiz to a file."""
    output = ["\nHistorical Quiz Information:"]
    
    # Checking if historical_quiz_df is a DataFrame
    if isinstance(historical_quiz_df, pd.DataFrame):
        for index, quiz in historical_quiz_df.iterrows():
            output.append(f"User ID: {quiz['user_id']}")
            output.append(f"Score: {quiz['score']}")
            output.append(f"Accuracy: {quiz['accuracy']}")
            output.append(f"Correct Answers: {quiz['correct_answers']}")
            output.append(f"Incorrect Answers: {quiz['total_questions'] - quiz['correct_answers']}")
            output.append(f"Total Questions: {quiz['total_questions']}")
            output.append(f"Rank: {quiz['quiz_topic']}")
            output.append(f"Submitted At: {quiz['submitted_at']}")
            
            # Analyze response map
            output.append("\nUser Responses:")
            for question_id, selected_option in quiz['response_map'].items():
                output.append(f"Question ID: {question_id}, Selected Option: {selected_option}")
            output.append("\n" + "-"*50)  # Separator for each quiz record
    else:
        output.append("Historical quiz data is not in the expected format.")

    write_to_file("\n".join(output))

def main():
    # Fetching data from the endpoints
    quiz_details = fetch_data(quiz_details_endpoint)
    current_quiz_data = fetch_data(current_quiz_endpoint)
    historical_quiz_data = fetch_data(historical_quiz_endpoint)

    # Preparing data
    prepared_current_data = prepare_current_quiz_data(current_quiz_data)
    prepared_historical_data = prepare_historical_quiz_data(historical_quiz_data)

    # Converting historical quiz data to DataFrame
    historical_quiz_df = pd.DataFrame(prepared_historical_data)

    # Analyzing the fetched data
    if quiz_details:
        write_to_file("\nQuiz Details:")
        analyze_quiz_details(quiz_details)
    
    if current_quiz_data:
        write_to_file("\nCurrent Quiz Analysis:")
        analyze_current_quiz(current_quiz_data)
    
    if historical_quiz_df is not None and not historical_quiz_df.empty:
        write_to_file("Columns in Historical Quiz Data:")
        write_to_file(str(historical_quiz_df.columns))
        write_to_file("\nHistorical Quiz Analysis:")
        weak_areas = analyze_historical_quiz(historical_quiz_df)

    # Visualizing the data
    if historical_quiz_df is not None and not historical_quiz_df.empty:
        plot_score_distribution(historical_quiz_df)
        plot_accuracy_over_time(historical_quiz_df)
        plot_performance_by_topic(historical_quiz_df)
    
    if current_quiz_data:
        plot_correct_incorrect_answers(prepared_current_data)

    # Generating recommendations
    recommendations = generate_recommendations(weak_areas)
    write_to_file("\nRecommendations:")
    for rec in recommendations:
        write_to_file(f"- {rec}")

    # Defining student persona
    define_student_persona(historical_quiz_df)

if __name__ == "__main__":
    main()