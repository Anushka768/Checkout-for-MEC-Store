# --------------------------
# Import required libraries
# --------------------------
import sqlite3    # Allows Python to connect and interact with SQLite databases
import difflib    # Helps suggest correct item names if the user makes a typo

# --------------------------
# Connect to SQLite database
# --------------------------
conn = sqlite3.connect("master_store.db")  # Connects to (or creates) a database file named 'store.db'
cur = conn.cursor()                 # Cursor object allows us to execute SQL commands

# --------------------------
# Create the purchases table if it doesn't exist
# --------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    visit_number INTEGER,
    items TEXT,
    total REAL,
    total_items INTEGER,
    total_spent REAL
)
""")

# --------------------------
# Define item prices
# --------------------------
item_prices = {               # Dictionary mapping item names to their price per unit
    "Rulers": 1.00,
    "Sharpies / markers (coloured variety)": 1.50,
    "Popsicle sticks": 0.25,
    "Wooden skewers": 0.25,
    "Toothpicks": 0.10,
    "Drinking straws": 0.15,
    "String & twine": 0.50,
    "Plastic bags / trash bags / cellophane bags": 0.20,
    "Bubble wrap": 0.30,
    "Newspaper / magazines": 0.10,
    "Tarp / plastic tablecloths": 1.50,
    "Aluminum foil (20cm x 30cm)": 0.40,
    "Cling wrap / parchment paper (20x30cm)": 0.40,
    "Cardboard sheets": 0.50,
    "Construction paper (colorful)": 0.20,
    "Shelf liner": 0.60,
    "Foam sheets": 0.75,
    "Binder clips / clothespins": 0.25,
    "Rubber bands": 0.10,
    "Twist ties": 0.10,
    "Zip ties": 0.15,
    "Pipe cleaners": 0.20,
    "Paper clips": 0.10,
    "Thumb tacks": 0.15,
    "Foam packing material": 0.20,
    "Cotton pads": 0.20,
    "Sponge pieces": 0.50,
    "Towels / old rags": 1.00,
    "Plastic cups (small and regular size)": 0.20,
    "Balloons": 0.15,
    "Labels": 0.10,
    "Ziplock bags": 0.20,
    "Syringes": 0.50,
    "Pasta shells": 0.10,
    "Plastic cutlery": 0.15,
    "Decorative tape": 0.75,
    "Jute rolls 20x30cm": 1.00,
    "Wrapping tissue": 0.30,
    "Velcro strips": 0.50,
    "Index cards / old greeting cards": 0.15

}

print("\n==== JUNIOR DESIGN STORE CHECKOUT ====\n")  # Header for the program

# --------------------------
# Main menu loop
# --------------------------
while True:  # Infinite loop to keep the menu running until the user chooses to exit
    print("\nMenu:")
    print("1. New purchase")          # Option to create a new purchase
    print("2. View team summary")    # Option to view past visits and totals for a team
    print("3. Exit")                  # Option to quit the program
    choice = input("Choose an option: ").strip()  # Get user input and remove extra spaces

    # --------------------------
    # Option 1: New Purchase
    # --------------------------
    if choice == "1":
        team = input("Enter team name: ").strip()  # Ask for team name

        # Automatically calculate next visit number
        cur.execute("SELECT MAX(visit_number) FROM purchases WHERE team_name=?", (team,))
        result = cur.fetchone()[0]                 # Get highest previous visit number
        visit = (result + 1) if result is not None else 1  # First visit = 1 if none exists
        print(f"\nAutomatically set Visit #{visit} for {team}")

        # Initialize visit details
        print("\nEnter items one by one (type 'done' when finished):")
        items = []         # List to store items bought in this visit with quantity
        visit_total = 0    # Total cost for this visit
        item_count = 0     # Sum of quantities for this visit

        # --------------------------
        # Loop to enter items and their quantities
        # --------------------------
        while True:
            item = input("Enter item (or 'done' to finish, 'exit' to cancel): ").strip().lower()
            
            if item == "done":
                break  # Finish this purchase normally
            elif item == "exit":
                print("Purchase canceled. Returning to main menu.")
                visit_total = 0  # Reset totals since they cancelled
                item_count = 0
                items = []
                break  # Exit the item input loop immediately

            # Check if item exists exactly in the price list
            if item in item_prices:
                while True:
                    qty_input = input(f"Enter quantity for '{item}' (or type 'exit' to cancel): ").strip().lower()
                    if qty_input == "exit":
                        print("Purchase cancelled. Returning to main menu.")
                        visit_total = 0
                        item_count = 0
                        items = []
                        break  # Exit quantity input and item loop
                    try:
                        quantity = int(qty_input)
                        if quantity <= 0:
                            print("Quantity must be at least 1. Try again.")
                            continue
                        break
                    except ValueError:
                        print("Invalid input. Enter a number.")

                visit_total += item_prices[item] * quantity  # Multiply price by quantity
                items.append(f"{item} x{quantity}")         # Store item and quantity as text
                item_count += quantity                      # Add to total items bought
                print(f"Added '{item}' x{quantity} - ${item_prices[item]*quantity:.2f}")
                continue  # Go back to ask for next item

            # Handle typos using difflib
            matches = difflib.get_close_matches(item, item_prices.keys(), n=1, cutoff=0.7)
            if matches:  # If a close match is found
                correct_item = matches[0]                     # Suggest closest item
                print(f"Did you mean '{correct_item}'? (y/n): ", end="")
                if input().lower() == "y":                    # If user agrees
                    while True:  # Loop until valid quantity is entered
                        try:
                            quantity = int(input(f"Enter quantity for '{correct_item}': "))
                            if quantity <= 0:
                                print("Quantity must be at least 1. Try again.")
                                continue
                            break
                        except ValueError:
                            print("Invalid input. Enter a number.")
                    item = correct_item
                    visit_total += item_prices[item] * quantity
                    items.append(f"{item} x{quantity}")
                    item_count += quantity
                    print(f"Added '{item}' x{quantity} - ${item_prices[item]*quantity:.2f}")
                else:
                    print("Let's try again. Please re-enter item name.")  # Ask again
                    continue
            else:
                # If no match found, show available items
                print("Item not found. Please check spelling.")
                print("Available items:", ", ".join(item_prices.keys()))

        # --------------------------
        # Extra charge for visits beyond first 5
        # --------------------------
        extra_charge = 5.0 if visit > 5 else 0.0  # Visits 1–5 free, 6+ = $5 extra
        if extra_charge > 0:
            print(f"Extra $5 charge applied for Visit #{visit} (beyond first 5 visits).")
        visit_total += extra_charge                 # Add extra charge to visit total

        # --------------------------
        # Calculate running total spent by this team
        # --------------------------
        cur.execute("SELECT MAX(total_spent) FROM purchases WHERE team_name=?", (team,))
        prev_total = cur.fetchone()[0]             # Previous total spent
        new_total = (prev_total or 0) + visit_total  # Add current visit total

        # --------------------------
        # Insert visit record into database
        # --------------------------
        cur.execute("""
            INSERT INTO purchases (team_name, visit_number, items, total, total_items, total_spent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (team, visit, ", ".join(items), visit_total, item_count, new_total))
        conn.commit()  # Save changes

        # --------------------------
        # Print receipt
        # --------------------------
        print(f"\n✅ Visit #{visit} recorded for {team}.")
        print(f"Items bought (sum of quantities): {item_count}")
        print(f"Total this visit: ${visit_total:.2f}")
        print(f"Total spent so far: ${new_total:.2f}")

    # --------------------------
    # Option 2: View team summary
    # --------------------------
    elif choice == "2":
        team = input("Enter team name to view: ").strip()
        cur.execute("SELECT * FROM purchases WHERE team_name=?", (team,))
        rows = cur.fetchall()  # Fetch all visits for this team

        if rows:  # If records exist
            print(f"\nSummary for {team}:")
            for row in rows:
                print(f"Visit #{row[2]} → Items: {row[3]} | Total: ${row[4]:.2f}")
            print(f"Overall total spent: ${rows[-1][6]:.2f}")  # Running total from last visit
        else:
            print("No records found for this team.")

    # --------------------------
    # Option 3: Exit program
    # --------------------------
    elif choice == "3":
        print("Exiting program. Goodbye!")
        break  # Exit the infinite menu loop

    # --------------------------
    # Handle invalid menu choices
    # --------------------------
    else:
        print("Invalid choice. Try again.")

# --------------------------
# Close database connection
# --------------------------
conn.close()  # Always close the database when done