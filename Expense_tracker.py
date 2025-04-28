"""
    It is a Python script for an Expense Tracker-cli program that allows users to add,
    view, update, and delete expenses stored in a JSON file.

    Usage(tested-options):
    python Expense_tracker.py --help
    python Expense_tracker.py --add --expense "description" --amount value
    python Expense_tracker.py --view
    python Expense_tracker.py --update --id <expense-id> --expense "new description" --amount new-value
    python Expense_tracker.py --delete --id <expense-id>
"""

import argparse
import os
import json
import uuid
from tabulate import tabulate


parser = argparse.ArgumentParser(
    prog="Expense Tracker",
    description="Track your expenses and income",
    epilog="Thank you for using Expense Tracker!",
)

parser.add_argument("-d", "--delete", action="store_true", help="Delete an expense (requires --id)")
parser.add_argument("-v", "--view", action="store_true", help="View all expenses")
parser.add_argument("-u", "--update", action="store_true", help="Update an expense (requires --id, --expense, and --amount)")
parser.add_argument("-i", "--id", help="ID of the expense (required for --delete and --update)")
parser.add_argument("-e", "--expense", help="Expense description")
parser.add_argument("-a", "--amount", type=float, help="Amount of the expense (required for --add and --update)")
parser.add_argument("--add", action="store_true", help="Add a new expense")


args = parser.parse_args()


def load_data(file_path="expenses.json"):
    """Load data from a JSON file"""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

def save_data(data, file_path="expenses.json", update_entry=None):
    """Save data to a JSON file with optimization for updates"""
    if update_entry:
        existing_data = load_data(file_path)
        for index, entry in enumerate(existing_data):
            if entry["id"] == update_entry["id"]:
                existing_data[index] = update_entry
                break
        else:
            existing_data.append(update_entry)
        data = existing_data

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def add_expense(expense, amount, file_path="expenses.json"):

    """Add a new expense"""
    if not expense or not isinstance(expense, str):
        print("Error in add_expense: Expense description must be a non-empty string.")
        return
    if amount is None or not isinstance(amount, (int, float)) or amount <= 0:
        print("Error: Amount must be a positive number.")
        return

    data = load_data(file_path)
    new_expense = {
        "expense": expense, 
        "id": str(uuid.uuid4()),  # Generate a unique ID for the expense
        "amount": amount,}
    [expense for expense in data if expense["id"] != new_expense["id"]]
    data = [expense for expense in data if expense["id"] != new_expense["id"]]
    # Append the new expense to the filtered data
    data.append(new_expense)
    save_data(data, file_path)      


def view_expenses(file_path="expenses.json"):
    """View all expenses in a formatted table"""
    data = load_data(file_path)
    if not data:
        print("No expenses found.")
        return
    
    # Prepare data for tabulate
    headers = ["ID", "Expense", "Amount"]
    table_data = [[exp["id"], exp["expense"], f"${exp['amount']:.2f}"] for exp in data]
    
    # Calculate total
    total = sum(exp["amount"] for exp in data)
    
    # Print the table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\nTotal Expenses: ${total:.2f}")


def delete_expense(expense_id, file_path="expenses.json"):
    """Delete an expense by ID"""
    data = load_data(file_path)
    if not any(expense["id"] == expense_id for expense in data):
        print(f"No expense found with ID: {expense_id}")
        return

    filtered_data = (expense for expense in data if expense["id"] != expense_id)
    save_data(list(filtered_data), file_path)
    print(f"Deleted expense with ID: {expense_id}")


def update_expense(expense_id, new_expense, new_amount, file_path="expenses.json"):
    """Update an existing expense"""
    if not new_expense or not isinstance(new_expense, str):
        print("Error: New expense description must be a non-empty string.")
        return
    if new_amount is None or not isinstance(new_amount, (int, float)) or new_amount <= 0:
        print("Error: New amount must be a positive number.")
        return

    data = load_data(file_path)
    for expense in data:
        if expense["id"] == expense_id:
            expense["expense"] = new_expense
            expense["amount"] = new_amount
            break
    else:
        print(f"No expense found with ID: {expense_id}")
        return
    save_data(data, file_path)
    print(f"Updated expense with ID: {expense_id} to {new_expense} - ${new_amount}")

def main():
    try:
        operations = [args.add, args.delete, args.update, args.view]
        if sum(bool(op) for op in operations) > 1:
            print("Error: Please specify only one operation at a time (--add, --delete, --update, or --view).")
            return

        if args.add:
            if args.amount is None or args.expense is None:
                print("Error: --amount and --expense are required for --add.")
                return
            add_expense(args.expense, args.amount)
        elif args.delete:
            if not args.id:
                print("Error: --id is required for --delete operation.")
                return
            delete_expense(args.id)
        elif args.update:
            if args.amount is None or args.expense is None or args.id is None:
                print("Error: --id, --amount, and --expense are required for --update.")
                return
            update_expense(args.id, args.expense, args.amount)
        elif args.view:
            view_expenses()
        else:
            parser.print_help()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()




