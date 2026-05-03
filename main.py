import sys
from datetime import date
from dotenv import load_dotenv

load_dotenv()

from src.crews.debate.crew import Debate
from src.crews.financial_researcher.crew import FinancialResearcher
from src.crews.stock_picker.crew import StockPicker
from src.crews.coder.crew import Coder
from src.crews.engineering_team.crew import EngineeringTeam


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <crew>")
        print("Available crews: debate, financial_researcher, stock_picker, coder, engineering_team")
        sys.exit(1)

    crew_name = sys.argv[1]

    if crew_name == "debate":
        inputs = {"motion": "AI will do more harm than good"}
        Debate().crew().kickoff(inputs=inputs)
    elif crew_name == "financial_researcher":
        inputs = {
            "company": "Apple",
            "current_date": date.today().strftime("%B %d, %Y"),
        }
        FinancialResearcher().crew().kickoff(inputs=inputs)
    elif crew_name == "stock_picker":
        inputs = {
            "sector": "Technology",
            "current_date": date.today().strftime("%B %d, %Y"),
        }
        StockPicker().crew().kickoff(inputs=inputs)
    elif crew_name == "coder":
        inputs = {
            "assignment": "Write a python program to calculate the first 10,000 terms "
                          "of this series, multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ...",
            "python_version": "3.12",
        }
        Coder().crew().kickoff(inputs=inputs)
    elif crew_name == "engineering_team":
        inputs = {
            "requirements": (
                "A simple account management system for a trading simulation platform. "
                "The system should allow users to create an account, deposit funds, and withdraw funds. "
                "The system should allow users to record that they have bought or sold shares, providing a quantity. "
                "The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit. "
                "The system should be able to report the holdings of the user at any point in time. "
                "The system should be able to report the profit or loss of the user at any point in time. "
                "The system should be able to list the transactions that the user has made over time. "
                "The system should prevent the user from withdrawing funds that would leave them with a negative balance, "
                "or from buying more shares than they can afford, or selling shares that they don't have. "
                "The system has access to a function get_share_price(symbol) which returns the current price of a share, "
                "and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL."
            ),
            "module_name": "accounts.py",
            "class_name": "Account",
        }
        EngineeringTeam().crew().kickoff(inputs=inputs)
    else:
        print(f"Unknown crew: {crew_name}")
        print("Available crews: debate, financial_researcher, stock_picker, coder, engineering_team")
        sys.exit(1)


if __name__ == "__main__":
    main()
