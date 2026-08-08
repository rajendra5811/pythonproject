
class Member:
    def __init__(self, member_id, name, membership_type, session_rate, is_active=True):
        self.member_id = member_id
        self.name = name
        self.membership_type = membership_type
        self.session_rate = session_rate
        self.is_active = is_active

    def display_member_info(self):
        active_status = "Yes" if self.is_active else "No"
        print(f"Member ID: {self.member_id}")
        print(f"Name: {self.name}")
        print(f"Membership Type: {self.membership_type}")
        print(f"Session Rate: ${self.session_rate}")
        print(f"Active Member: {active_status}\n")

    def update_session_rate(self, new_rate):
        self.session_rate = new_rate
        print("Session rate updated successfully.")
        print(f"New Session Rate: ${self.session_rate}/session\n")



class TrainingSession(Member):
    def schedule_session(self, session_count):
        if self.is_active:
            total_cost = session_count * self.session_rate
            self.is_active = False  # Deactivate to prevent double-booking
            print("Training session scheduled successfully.\n")
            print(f"Sessions Scheduled: {session_count}")
            print(f"Rate Per Session: ${self.session_rate}")
            print(f"Total Cost: ${total_cost}\n")
        else:
            print("Sorry! Membership is currently inactive or already scheduled.\n")

    def complete_training_cycle(self):
        self.is_active = True  # Reactivate status
        print("Training cycle completed successfully.")
        print("Member status is now active for scheduling.\n")


if __name__ == "__main__":
  
    member1 = TrainingSession(
        member_id="M-805", 
        name="Sarah Jenkins", 
        membership_type="Premium", 
        session_rate=50
    )

    # 1. Display initial member information
    print("--- 1. Initial Member Info ---")
    member1.display_member_info()

    # 2. Update session rate to $65
    print("--- 2. Updating Session Rate ---")
    member1.update_session_rate(65)

    # 3. Display updated member information
    print("--- 3. Updated Member Info ---")
    member1.display_member_info()

    # 4. Schedule 5 training sessions
    print("--- 4. Scheduling 5 Sessions ---")
    member1.schedule_session(5)

    # 5. Try scheduling another session before completing cycle
    print("--- 5. Attempting Double Booking ---")
    member1.schedule_session(2)

    # 6. Complete the training cycle
    print("--- 6. Completing Training Cycle ---")
    member1.complete_training_cycle()

    # 7. Schedule 3 training sessions
    print("--- 7. Scheduling 3 Sessions ---")
    member1.schedule_session(3)