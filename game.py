# Tic Tac Toe Game
# Two Player Mode

# Create the board
def create_board():
    return [" "] * 9


# Display the board
def display_board(board):
    print()
    for i in range(9):
        if board[i] == " ":
            print(i + 1, end="")
        else:
            print(board[i], end="")

        if i % 3 != 2:
            print(" | ", end="")
        else:
            print()
            if i < 6:
                print("--+---+--")
    print()


# Check the winner
def check_winner(board, symbol):
    wins = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ]

    for line in wins:
        if all(board[i] == symbol for i in line):
            return True
    return False


# Check if the board is full
def check_draw(board):
    return " " not in board


# Get player move
def get_move(board, name):
    while True:
        try:
            move = int(input(name + ", enter position (1-9): "))

            if move < 1 or move > 9:
                print("Enter a number from 1 to 9.")

            elif board[move - 1] != " ":
                print("Position already taken.")

            else:
                return move - 1

        except ValueError:
            print("Please enter a valid number.")


# Main game
def main():
    print("Welcome to Tic Tac Toe")
    print("Two Player Game")

    player1 = input("Enter Player 1 name: ")
    player2 = input("Enter Player 2 name: ")

    score1 = 0
    score2 = 0
    draws = 0

    while True:
        board = create_board()
        current = 1

        while True:
            display_board(board)

            if current == 1:
                name = player1
                symbol = "X"
            else:
                name = player2
                symbol = "O"

            move = get_move(board, name)
            board[move] = symbol

            if check_winner(board, symbol):
                display_board(board)
                print(name, "wins!")

                if current == 1:
                    score1 += 1
                else:
                    score2 += 1
                break

            if check_draw(board):
                display_board(board)
                print("Game is a draw!")
                draws += 1
                break

            if current == 1:
                current = 2
            else:
                current = 1

        print("\nScoreboard")
        print(player1, ":", score1)
        print(player2, ":", score2)
        print("Draws:", draws)

        again = input("\nPlay again? (y/n): ").lower()

        if again != "y":
            print("Thank you for playing!")
            break


# Start the game
main()