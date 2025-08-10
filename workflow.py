from agents.general_secretary import GeneralSecretary

def main():
    general_secretary = GeneralSecretary()
    
    print("=== MULTI-AGENT WORKFLOW ===")
    
    # Task 1: Calendar and YouTrack management
    print("\n--- Task 1: Calendar to YouTrack Sync ---")
    response = general_secretary.execute_task(
        "Check today's calendar events and create appropriate work items in YouTrack"
    )
    print(f"Result: {response['output']}")
    
    # Task 2: Financial analysis
    print("\n--- Task 2: Daily Financial Report ---")
    response = general_secretary.execute_task(
        "Provide today's portfolio performance and financial news summary"
    )
    print(f"Result: {response['output']}")

if __name__ == "__main__":
    main()