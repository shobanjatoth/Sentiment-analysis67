from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import joblib
import os
import warnings

# Suppress version mismatch warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

# Load model and data
model = joblib.load("sentiment_model_nb.pkl")
df = pd.read_csv("cleaned_review.csv").dropna(subset=['clean_review'])

# Create review length column
df["review_length"] = df["clean_review"].apply(lambda x: len(str(x).split()))

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Generate EDA plots
def generate_eda_plots():
    # 1. Sentiment distribution
    fig1 = px.histogram(df, x='sentiment', color='sentiment',
                        title='Sentiment Distribution',
                        template='plotly_white')
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig1.write_image("static/sentiment_dist.png")

    # 2. Review length by sentiment
    fig2 = px.box(df, x='sentiment', y='review_length', color='sentiment',
                  title='Review Length by Sentiment',
                  template='plotly_white')
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig2.write_image("static/review_length_box.png")

    # 3. Top words in each sentiment
    for sentiment, color in zip(["Positive", "Negative", "Neutral"], ["greens", "reds", "blues"]):
        text = " ".join(df[df["sentiment"] == sentiment]["clean_review"])
        words = pd.Series(text.split()).value_counts().head(20).reset_index()
        words.columns = ['word', 'frequency']
        fig = px.bar(words, x='word', y='frequency', title=f"Top Words in {sentiment} Reviews",
                     color='frequency', color_continuous_scale=color,
                     template='plotly_white')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis_tickangle=-45)
        fig.write_image(f"static/top_words_{sentiment.lower()}.png")

# Generate plots once
generate_eda_plots()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    review_text = None
    if request.method == 'POST':
        review_text = request.form['review']
        prediction = model.predict([review_text])[0]
    return render_template('predict.html', prediction=prediction, review=review_text)

@app.route('/eda')
def eda():
    return render_template('eda.html')

if __name__ == "__main__":
    app.run(debug=True)

