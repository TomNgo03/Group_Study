# StudyHub - Study with me!

The Study Group Assistant is a web application developed using Django framework that serves as an interactive study companion for users. It leverages the power of OpenAI API to provide a conversational interface where users can ask questions and receive responses from the AI-powered bot.

## Table of Contents

- [Project Overview](#project-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The StudyHub aims to enhance the learning experience by offering a virtual assistant that can answer queries related to various subjects and topics. It utilizes the OpenAI API, which leverages state-of-the-art natural language processing models to generate human-like responses.

Key features of the Study Group Assistant project include:
- Django-based web application for user interactions
- Integration with the OpenAI API for conversational capabilities
- User-friendly interface for asking questions and receiving bot responses
- Support for multiple study topics and customizable knowledge base
- Interactive and dynamic user experience

## Installation

1. Clone the repository or download the source code.
   ```bash
   git clone https://github.com/TomNgo03/Group_Study.git
2. Create a virtual environment (optional but recommended).
    ```bash
    python3 -m venv myenv
3. Activate the virtual environment.

- On Linux/macOS:
    ```bash
    source myenv/bin/activate

- On Windows:
    ```bash
    myenv\Scripts\activate

4. Install the dependencies.
    ```bash
    pip install -r requirements.txt

5. Perform any additional setup steps required, such as setting up a database or configuring environment variables.

## Usage

To run the Study Group Assistant, follow these steps:

1. Make sure your virtual environment is activated.

2. Apply database migrations.
    ```bash
    python manage.py migrate
3. Run the development server.
    ```bash
    python manage.py runserver
4. Open a web browser and visit http://localhost:8000 to access the application.

5. Ask questions to the bot by typing them in the provided input field and click on the "Submit" button to receive responses.

## Configuration
- The StudyHub project utilizes the OpenAI API for generating responses. To use the OpenAI API, you need to obtain an API key from OpenAI and configure it in the project.

- Obtain an API key from OpenAI by following their documentation.

- Configure the API key in the project's settings. Open the settings.py file and update the OPENAI_API_KEY variable with your API key.

- Optionally, you can customize other project settings such as the knowledge base or chatbot behavior to suit your study group's specific needs.

## Contributing
- Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request. For major changes, please discuss them first in the project's issue tracker.

## License
- This project is licensed under the MIT License. You can find the full license text in the LICENSE file.
