# CareerSaathi: AI-Driven Career Guidance for Job Seekers

**CareerSaathi** is an AI-powered ecosystem designed to assist job seekers by providing personalized career guidance, skill assessments, resume building, and job matching. It uses multiple intelligent agents working in harmony to help users advance their careers, particularly in the AI/tech industry.

## Key Features:
- **Resume Expert**: Provides personalized feedback and optimization for resumes, ensuring they stand out to recruiters.
- **Skill Assessment**: Analyzes and evaluates technical and soft skills, helping users understand their strengths and areas for improvement.
- **Demand Analysis**: Analyzes real-time job market trends to help users align their career goals with industry demands.
- **Training Resource**: Recommends relevant courses, certifications, and resources to enhance the user's skills.
- **Job Matching**: Matches users with job opportunities based on their skills, experience, and preferences.

## How It Works
The **CareerSaathi** system is powered by **uAgents**, a framework built on Fetch.ai, enabling dynamic interaction between specialized agents. The system uses **OpenAI's GPT models** for natural language processing to provide personalized responses. 

### Components:
- **Commander Agent**: Coordinates all sub-agents and handles user interactions. [Agent Address `test-agent://agent1qtjjk3xfvel6qkqk48n2he4kwqmytwcc6tplvszvwty9qp38nfs4w3r3xme`]
- **Worker Agents**: Specialized agents responsible for different aspects of career guidance (Resume Expert, Skill Assessment, Demand Analysis, Training Resource, Job Matching).
- **Search & Discovery**: Dynamically discovers agents based on user queries via the **Agentverse** marketplace.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/careersaathi.git](https://github.com/dhruvagrawal27/InnovateLab-FetchAI.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python testagent.py
   ```

## Usage
1. Enter a career-related query in the provided text box (e.g., "What are the job opportunities for AI engineers in Indore?").
2. The system will analyze the query, extract relevant keywords, and search for the best-suited agents.
3. The selected agent will respond with detailed advice or recommendations based on the query.

### Agents:
- **Resume Expert**: `test-agent://agent1qvpk7cwgjfdtzfsxv092gcdu0sdsu43z6p0z8nrfckxmcmzd532dgxuy0x5`
- **Skill Assessment**: `test-agent://agent1qgys89d7tr5rxxamvdhkdg80z9q99jf7sfq08kx0yftt59yjggpsk4ewgm4`
- **Demand Analysis**: `test-agent://agent1qfvyd3y9qf9cmsl2waatsdchumu8gjj2fl6ynuzy0mlqcjwpge6ekp74qen`
- **Training Resource**: `test-agent://agent1qvfed9rmxdz4j488gqvannjs6fatpl3u0ehk2kelez6pz8tr2u8nyxjg5kc`
- **Job Matching**: `test-agent://agent1qv4xn6kxtylzyvf5zc4ywx4qcq2g3q6cp2mpvz8twkwmtnm27gl6xp9x7av`

## Challenges Faced
- **Agent Coordination**: Ensuring smooth communication between multiple agents, especially when queries involved overlapping domains (e.g., resume optimization and skill assessment).
- **Dynamic Agent Discovery**: Implementing the **Search and Discovery** feature to dynamically select agents based on keywords extracted from user queries.
- **OpenAI Integration**: Fine-tuning GPT models for generating meaningful responses that are accurate and actionable for career guidance.

- **Functionality**: The agents perform their tasks effectively by assessing user skills, suggesting training resources, improving resumes, and matching jobs.
- **Agentverse Integration**: The agents are registered and interact dynamically using **Agentverse**.
- **Quantity of Agents Created**: Five distinct agents were developed for different career guidance tasks.
- **Personal Assistant Development**: The personalized assistant intelligently manages tasks, ensuring user needs are met by the right agent at the right time.
- **Innovation and Impact**: **CareerSaathi** addresses the real-world challenge of career navigation for job seekers, focusing on the high-demand AI industry.

## License
Distributed under the MIT License. See `LICENSE` for more information.

---

![tag : innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
