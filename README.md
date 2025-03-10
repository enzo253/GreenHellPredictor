GREEN HELL PREDICTOR

Overview

The Green Hell Predictor is a data-driven web application designed to predict and analyse car performance metrics, including estimated lap times on the Nürburgring racetrack. The app leverages Python, Streamlit, Plotly, and AI models to fill in missing car specifications and generate insightful visualisations.

Features

Car Specification Analysis: Displays detailed car specifications with AI-generated predictions for missing values.

Performance Prediction: Uses AI to predict Nürburgring lap times based on car specs.

Interactive Visualisations: Includes scatter plots, line charts, radar charts, and heatmaps for performance analysis.

Dynamic Data Management: Utilises a PostgreSQL database for efficient data retrieval and storage.

Tech Stack

Python (Pandas, NumPy, Plotly, Together API, Requests, BeautifulSoup)

Streamlit (For the interactive web interface)

PostgreSQL (Database management)

AWS (For deployment)

AI Model: Utilises meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo for accurate predictions

Installation

Clone this repository:

git clone <repository-url>
cd GreenHellPredictor

Install the required dependencies:

pip install -r requirements.txt

Set up your environment variables:
Create a .env file with the following:

MY_CAR_KEY=<Your Railway Database URL>
TOGETHER_API=<Your Together AI API Key>

Run the application:

streamlit run GREEN_HELL_APP.py

Usage

Car Selection: Choose a car from the dropdown to view its specifications.

AI Prediction: The app predicts missing values and displays them in the car specifications table.

Performance Analysis: Visualise car performance using dynamic charts, including:

Radar charts for key performance indicators

3D scatter plots for speed, weight, and acceleration

Correlation heatmaps for performance metric relationships

Challenges Faced

Data Imputation: Handling missing car specs by integrating AI models to predict values.

Visualisation Issues: Resolving layout and theme inconsistencies for seamless data presentation.

AWS Deployment: Overcoming package size limitations by optimising dependencies.

Future Improvements

Enhance AI model performance for even more accurate predictions.

Implement additional filters for improved car selection and comparison.

Introduce user authentication to allow saving and tracking favourite car analyses.

Acknowledgements

Special thanks to Together AI for their powerful language model and to the automotive data sources that made this project possible.

Contact

For questions or contributions, feel free to reach out at enzo.wurtele@outlook.com
