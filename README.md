## Green Hell Predictor

### Overview
The **Green Hell Predictor** is a powerful web application that predicts car performance and provides in-depth performance analysis based on various car specifications. Leveraging AI, the app can predict missing values in car data and estimate Nürburgring lap times with impressive accuracy.

### Features
- **AI-Powered Predictions:** Predict missing car performance values and estimate lap times using machine learning models.
- **Interactive Visualizations:** Explore acceleration curves, 3D performance plots, and correlation heatmaps.
- **Dynamic UI:** User-friendly interface built with Streamlit for seamless data exploration and insights.

### Live Demo
🔗 [**Try the Green Hell Predictor**](https://greenhellpredictor.streamlit.app/)

### Installation
To run the project locally, follow these steps:
1. Clone the repository:
   ```bash
   git clone <repository_link>
   cd GreenHellPredictor
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and include your API keys:
   ```plaintext
   MY_CAR_KEY=your_railway_key_here
   TOGETHER_API=your_together_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run GREEN_HELL_APP.py
   ```

### Technologies Used
- **Python** (Pandas, NumPy, Plotly, Requests)
- **Streamlit** (For interactive web interface)
- **PostgreSQL** (For database integration)
- **Together API** (For AI-based predictions)

### Usage
1. Select a car from the dropdown menu.
2. View detailed specifications, including AI-predicted missing values.
3. Explore visualizations for acceleration, power-to-weight ratio, and more.
4. Compare car performance metrics via interactive graphs.

### Future Improvements
- Enhanced AI model for improved lap time predictions.
- Expanded dataset with additional car models.
- Integration of user-uploaded data for customized analysis.

### License
This project is licensed under the **MIT License**.

### Contact
For questions or contributions, please reach out via GitHub or email.
