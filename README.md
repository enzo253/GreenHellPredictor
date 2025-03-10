# Green Hell Predictor

## Overview
Green Hell Predictor is a Streamlit application designed to predict car performance metrics based on available data. The app utilizes AI models to fill in missing specifications and predict Nürburgring lap times. It also provides interactive visualizations for detailed performance analysis.

## Features
- Select a car to view its specifications.
- Uses AI to predict missing data fields.
- Predicts Nürburgring lap times based on car specifications.
- Interactive visualizations such as 3D scatter plots, radar charts, and heatmaps.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/green-hell-predictor.git
   cd green-hell-predictor
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following keys:
   ```env
   MY_CAR_KEY=<your_postgres_connection_string>
   TOGETHER_API=<your_together_ai_key>
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run GREEN_HELL_APP.py
   ```

## Requirements
```
streamlit
pandas
psycopg2
requests
together
plotly
beautifulsoup4
dotenv
```

## Usage

1. Select a car from the dropdown menu to view its specifications.
2. If any data points are missing, the AI will predict and fill them automatically.
3. Use the sidebar options to toggle between AI predictions and performance analysis.
4. Interactive graphs like scatter plots, radar charts, and heatmaps provide insight into the car's performance metrics.

## Challenges Faced
- **Data Inconsistencies:** Some car data entries contained missing values, which required implementing AI predictions to fill the gaps.
- **Visualisation Issues:** Creating a seamless radar chart required adjusting background colours and ensuring readability in dark mode.
- **Large Deployment Size:** The project's size exceeded AWS limits, requiring dependency optimization.

## Future Improvements
- Enhance AI models for more accurate performance predictions.
- Expand the dataset to include additional car specifications.
- Implement caching for improved performance in the Streamlit app.

## License
This project is licensed under the MIT License.

## Contact
For any inquiries, please reach out via email at (enzo.wurtele@outlook.com).


