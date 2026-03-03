from game import load_progress, reset_progress, run_python_round, run_sql_round, show_dashboard


def main() -> None:
    progress = load_progress()

    while True:
        show_dashboard(progress)
        print("Choose an option:")
        print("1) Play Python challenge")
        print("2) Play SQL challenge")
        print("3) Reset progress")
        print("4) Exit")

        choice = input("\nEnter choice (1-4): ").strip()
        print()

        if choice == "1":
            run_python_round(progress)
        elif choice == "2":
            run_sql_round(progress)
        elif choice == "3":
            reset_progress()
            progress = load_progress()
        elif choice == "4":
            print("Thanks for playing. Keep coding.")
            break
        else:
            print("Invalid choice. Pick 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()
