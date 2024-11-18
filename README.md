# CSE412-Project

## Installation and Setup

### Prerequisites
- Python 3.13: Download from [python.org](https://www.python.org/downloads/)
- PostgreSQL: Download from [postgresql.org](https://www.postgresql.org/download/)
- Ensure both are added to your Path

### Setup Instructions
1. **Clone the repository**:
    - Open a new terminal in your desired directory and run:
   ```bash
   git clone "https://github.com/evanjaram/CSE412-Project.git"
   cd CSE412-Project
   ```
2. **Install Backend Dependencies**:
    - Navigate to the Backend directory and run:
    ```bash
    pip install -r requirements.txt
    ```
3. **Set Up Backend Environment Variables**:
    1. Create new file ".env" inside the root of the Backend directory
    2. Copy contents of ".env.sample" into ".env"
    3. Replace placeholder values with your local PostrgeSQL values
