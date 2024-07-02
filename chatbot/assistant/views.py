from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UserInputForm
from .models import Conversation, DatasetEntry, Label, PredictedCategory
from .pipeline import clean_text, tfidf_vectorizer, voting_classifier
from django.utils import timezone
import openai
from django.db import transaction
import os
import json
from fuzzywuzzy import fuzz

# Set your OpenAI API key
openai.api_key = 'sk-proj-ponELUze39kLA3NR56jaT3BlbkFJcOQVQGYGrCkcCpeziM4I'  # Replace with your actual API key

# Get the directory of the current file
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the answers.json file
answers_file_path = os.path.join(current_directory, 'answers.json')

# Load predefined answers from JSON file
with open(answers_file_path, 'r') as file:
    predefined_answers = json.load(file)

# Function to get the most similar response based on user input
def get_most_similar_response(user_input, predefined_responses):
    max_similarity = 0
    most_similar_response = None
    
    for response in predefined_responses:
        similarity = fuzz.token_set_ratio(user_input, response)
        print(f"Similarity between user input and response '{response}': {similarity}")
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_response = response
    
    return most_similar_response
@csrf_exempt
@transaction.atomic
def chat(request):
    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data['user_input']
            # user_id = 1  # For simplicity, assuming no user authentication

            # Clean the user input
            cleaned_input = clean_text(user_input)

            # Vectorize the cleaned input using TF-IDF
            X_input = tfidf_vectorizer.transform([cleaned_input])

            # Make prediction using the trained model
            prediction_result = voting_classifier.predict_proba(X_input)
            predicted_category_index = prediction_result.argmax()
            predicted_category_probability = prediction_result[0, predicted_category_index]

            # Get or create the label object for the predicted category
            predicted_category = voting_classifier.classes_[predicted_category_index]
            print(f"Predicted category: {predicted_category}")

            # Save user query to Conversation
            user_message = Conversation.objects.create( role='user',
                                                        content=user_input,
                                                        timestamp=timezone.now())
            
            # Save user query to DatasetEntry with roles as 'parent'
            dataset_entry = DatasetEntry.objects.create( content=user_input, roles='parent',
                                                        timestamp=timezone.now())

            # Associate label with DatasetEntry
            label, _ = Label.objects.get_or_create(name=predicted_category)
            dataset_entry.labels.add(label)

            # Save predicted category to PredictedCategory
            predicted_category_entry = PredictedCategory.objects.create(conversation=user_message, predicted_label=label,
                                                                        probability=predicted_category_probability, timestamp=timezone.now())

            # Get predefined response based on predicted category
            predefined_response, probability = get_predefined_response(predicted_category, predicted_category_probability, user_input)

            # Return the predefined response or generate one if not found
            if predefined_response is not None:
                response = predefined_response
            else:
                response = generate_assistant_response(user_input)

                # Save assistant's response to Conversation
            assistant_message = Conversation.objects.create( role='assistant',
                                                             content=response,
                                                             timestamp=timezone.now())

            # Return a JSON response with the generated response and predicted category
            return JsonResponse({'response': response, 'predicted_category': predicted_category})
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        form = UserInputForm()
        chat_history = Conversation.objects.all()
        return render(request, 'chatbot.html', {'form': form, 'chat_history': chat_history})



    
def get_predefined_response(predicted_category, probability, user_input):
    print(f"Predicted category: {predicted_category}, Probability: {probability}")

    if predicted_category in predefined_answers:
        # print(f"Predefined answers for category: {predefined_answers[predicted_category]}")

        # Determine the appropriate responses based on the user's role (teacher or parent)
        if predicted_category == "teacher":
            responses = predefined_answers[predicted_category]['teacher']
        else:
            responses = predefined_answers[predicted_category]['parent']

        most_similar_response = get_most_similar_response(user_input, responses)
        return most_similar_response, probability
    else:
        return None, None





def generate_assistant_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": " You are Jazz, an A.I. powered assistant FOR THIS PARTICULAR MUSIC SCHOOL. NO OTHER KNOWLEDGE WHATSOEVER AND YOU REFUSE TO ANSWER ANY OTHER KNOWLEDGE FROM YOUR DOMAIN OR SCOPE. DOTN REFER AS MUSIC EDUCATION. JUST MUSIC SCHOOL"},
            {"role": "user", "content": user_input},
        ],
        temperature=0.1,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0.2,
        stop=None,
    )
    return response.choices[0].message['content']