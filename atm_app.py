import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import smtplib
from email.mime.text import MIMEText
import random
from datetime import datetime
import re
import json

class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Learn-ATM")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a2a6c")

        # Email configuration
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 587
        self.SMTP_USERNAME = "aravind.kumar18118@gmail.com"
        self.SMTP_PASSWORD = "wzal zkno dkvp bhxd"

        # Admin PIN
        self.ADMIN_PIN = "9999"

        # In-memory storage
        self.verification_codes = {}
        self.account = {
            'cards': [
                {
                    'cardNumber': "1234567890123456",
                    'pin': "1234",
                    'balance': 1000,
                    'transactions': [],
                    'phoneNumber': "1234567890",
                    'expiryDate': "12/2025",
                    'cvv': "123",
                    'verified': True,
                    'blocked': False,
                    'email': "",
                    'emailVerified': False
                }
            ],
            'currentCardIndex': 0
        }
        self.exchange_rates = {'USD': 1.0, 'EUR': 0.95, 'GBP': 0.80, 'JPY': 150.0, 'INR': 84.0}
        self.tax_rates = {'USD': 0.02, 'EUR': 0.21, 'GBP': 0.20, 'JPY': 0.10, 'INR': 0.18}
        self.selected_currency = 'USD'
        self.current_input_field = None

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Poppins", 14, "bold"), padding=10)
        self.style.configure("TLabel", font=("Poppins", 16), background="#121212", foreground="#00ccff")
        self.style.configure("TEntry", font=("Poppins", 14), fieldbackground="#252525", foreground="#00ccff")

        # Main container
        self.container = tk.Frame(root, bg="#e8ecef", bd=5, relief="ridge")
        self.container.pack(pady=20, padx=20, fill="both", expand=True)

        # Header
        self.header = tk.Frame(self.container, bg="#2c2c2c")
        self.header.pack(fill="x", pady=10)
        tk.Label(self.header, text="ATM Center", font=("Poppins", 30, "bold"), bg="#2c2c2c", fg="white").pack(pady=10)
        tk.Button(self.header, text="Admin", font=("Poppins", 15, "bold"), bg="#d32f2f", fg="white",
                  command=self.show_admin_pin_screen).pack(side="right", padx=10)
        tk.Button(self.header, text="New Card", font=("Poppins", 15, "bold"), bg="#0288d1", fg="white",
                  command=self.show_new_card_screen).pack(side="right", padx=10)

        # Screen container
        self.screen_container = tk.Frame(self.container, bg="#1f1f1f", bd=4, relief="ridge")
        self.screen_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Function buttons
        self.left_buttons = tk.Frame(self.screen_container, bg="#1f1f1f")
        self.left_buttons.pack(side="left", padx=10)
        self.right_buttons = tk.Frame(self.screen_container, bg="#1f1f1f")
        self.right_buttons.pack(side="right", padx=10)

        self.left_btns = []
        self.right_btns = []
        for i, text in enumerate(["Deposit", "Transfer", "PIN Change", "Others"]):
            btn = tk.Button(self.left_buttons, text=text, font=("Poppins", 15, "bold"), bg="#ff4d4d", fg="white",
                            width=15, command=lambda x=text: self.handle_left_button(x), state="disabled")
            btn.pack(pady=10)
            self.left_btns.append(btn)
        for i, text in enumerate(["Fast Cash", "Cash Withdrawal", "Balance Enquiry", "Mini Statement"]):
            btn = tk.Button(self.right_buttons, text=text, font=("Poppins", 15, "bold"), bg="#ff4d4d", fg="white",
                            width=15, command=lambda x=text: self.handle_right_button(x), state="disabled")
            btn.pack(pady=10)
            self.right_btns.append(btn)

        # Screen
        self.screen = tk.Frame(self.screen_container, bg="#121212", bd=3, relief="ridge")
        self.screen.pack(fill="both", expand=True, padx=10)

        self.screens = {}
        self.create_screens()
        self.show_screen("welcome-screen")

    def create_screens(self):
        # Welcome Screen
        welcome = tk.Frame(self.screen, bg="#121212")
        tk.Label(welcome, text="Welcome to the ATM", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=50)
        tk.Label(welcome, text="Enter Card Number:", bg="#121212", fg="#00ccff", font="30").pack()
        card_number = ttk.Entry(welcome, width=30)
        card_number.pack(pady=5)
        tk.Button(welcome, text="Submit", font=("Poppins", 14, "bold"), command=lambda: self.submit_card_number(card_number.get())).pack(pady=10)
        self.screens["welcome-screen"] = welcome
        self.current_input_field = card_number

        # PIN Screen
        pin = tk.Frame(self.screen, bg="#121212")
        tk.Label(pin, text="Enter PIN", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=50)
        pin_input = ttk.Entry(pin, show="*", width=30)
        pin_input.pack(pady=5)
        tk.Button(pin, text="Enter", command=lambda: self.submit_pin(pin_input.get())).pack(pady=10)
        self.screens["pin-screen"] = pin

        # Main Menu
        main_menu = tk.Frame(self.screen, bg="#121212")
        tk.Label(main_menu, text="Select Your Transaction", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        tk.Label(main_menu, text="Use the buttons on the sides to select a transaction.", bg="#121212", fg="#e6e6e6").pack()
        self.screens["main-menu"] = main_menu

        # Balance Screen
        balance = tk.Frame(self.screen, bg="#121212")
        tk.Label(balance, text="Your Balance", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.balance_display = tk.Label(balance, text="", bg="#121212", fg="#e6e6e6")
        self.balance_display.pack()
        tk.Button(balance, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=10)
        self.screens["balance-screen"] = balance

        # Withdraw Screen
        withdraw = tk.Frame(self.screen, bg="#121212")
        tk.Label(withdraw, text="Cash Withdrawal", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        currency_frame = tk.Frame(withdraw, bg="#121212")
        currency_frame.pack()
        tk.Label(currency_frame, text="Select Currency:", bg="#121212", fg="#00ccff").pack()
        for currency in self.exchange_rates:
            tk.Button(currency_frame, text=currency, bg="#4caf50", fg="white",
                      command=lambda c=currency: self.select_currency(c)).pack(side="left", padx=5)
        self.currency_rate_display = tk.Label(withdraw, text="Selected Currency: USD (1 USD = 1 USD)", bg="#121212", fg="#e6e6e6")
        self.currency_rate_display.pack(pady=5)
        preset_frame = tk.Frame(withdraw, bg="#121212")
        preset_frame.pack()
        self.preset_btns = []
        for amount in [50, 100, 150]:
            btn = tk.Button(preset_frame, text=f"{amount} USD", bg="#ffca28", fg="white",
                            command=lambda a=amount: self.set_withdraw_amount(a))
            btn.pack(side="left", padx=5)
            self.preset_btns.append(btn)
        self.withdraw_amount = ttk.Entry(withdraw, width=30)
        self.withdraw_amount.pack(pady=5)
        tk.Button(withdraw, text="Withdraw", command=self.process_withdraw).pack(pady=5)
        tk.Button(withdraw, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["withdraw-screen"] = withdraw

        # Fast Cash Screen
        fast_cash = tk.Frame(self.screen, bg="#121212")
        tk.Label(fast_cash, text="Fast Cash", font=("Poppins", 14, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        for amount in [20, 50, 100]:
            tk.Button(fast_cash, text=f"${amount}", bg="#ffca28", fg="white",
                      command=lambda a=amount: self.process_fast_cash(a)).pack(pady=5)
        tk.Button(fast_cash, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["fast-cash-screen"] = fast_cash

        # Deposit Screen
        deposit = tk.Frame(self.screen, bg="#121212")
        tk.Label(deposit, text="Deposit Cash", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.deposit_amount = ttk.Entry(deposit, width=30)
        self.deposit_amount.pack(pady=5)
        tk.Button(deposit, text="Deposit", command=self.process_deposit).pack(pady=5)
        tk.Button(deposit, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["deposit-screen"] = deposit

        # Transfer Screen
        transfer = tk.Frame(self.screen, bg="#121212")
        tk.Label(transfer, text="Transfer Money", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.transfer_account = ttk.Entry(transfer, width=30)
        self.transfer_account.pack(pady=5)
        self.transfer_amount = ttk.Entry(transfer, width=30)
        self.transfer_amount.pack(pady=5)
        tk.Button(transfer, text="Transfer", command=self.process_transfer).pack(pady=5)
        tk.Button(transfer, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["transfer-screen"] = transfer

        # PIN Change Screen
        pin_change = tk.Frame(self.screen, bg="#121212")
        tk.Label(pin_change, text="Change PIN", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.old_pin = ttk.Entry(pin_change, show="*", width=30)
        self.old_pin.pack(pady=5)
        self.new_pin = ttk.Entry(pin_change, show="*", width=30)
        self.new_pin.pack(pady=5)
        tk.Button(pin_change, text="Change PIN", command=self.process_pin_change).pack(pady=5)
        tk.Button(pin_change, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["pin-change-screen"] = pin_change

        # Mini Statement Screen
        mini_statement = tk.Frame(self.screen, bg="#121212")
        tk.Label(mini_statement, text="Mini Statement", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.mini_statement_display = tk.Text(mini_statement, height=5, width=50, bg="#1c1c1c", fg="#ddd")
        self.mini_statement_display.pack(pady=5)
        tk.Button(mini_statement, text="Download", command=self.download_statement).pack(pady=5)
        tk.Button(mini_statement, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["mini-statement-screen"] = mini_statement

        # Others Screen
        others = tk.Frame(self.screen, bg="#121212")
        tk.Label(others, text="Other Services", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        services = [
            ("Bill Payment", self.show_bill_payment),
            ("Mobile Recharge", self.show_mobile_recharge),
            ("Request Cheque Book", self.show_cheque_book_request),
            ("Cardless Withdrawal", self.show_cardless_withdrawal),
            ("Exchange Phone", self.show_exchange_phone_number),
            ("Block/Unblock Card", self.update_block_unblock_button),
            ("Verify Email", self.show_verify_email),
            ("Apply New Card", self.show_apply_new_card)
        ]
        for text, cmd in services:
            tk.Button(others, text=text, bg="#ffca28", fg="white", command=cmd).pack(pady=5, fill="x")
        tk.Button(others, text="Back", font=("Poppins", 14, "bold"), command=self.back_to_menu).pack(pady=5)
        self.screens["others-screen"] = others

        # Bill Payment Screen
        bill_payment = tk.Frame(self.screen, bg="#121212")
        tk.Label(bill_payment, text="Bill Payment", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.bill_id = ttk.Entry(bill_payment, width=30)
        self.bill_id.pack(pady=5)
        self.bill_amount = ttk.Entry(bill_payment, width=30)
        self.bill_amount.pack(pady=5)
        tk.Button(bill_payment, text="Pay Bill", command=self.process_bill_payment).pack(pady=5)
        tk.Button(bill_payment, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["bill-payment-screen"] = bill_payment

        # Mobile Recharge Screen
        mobile_recharge = tk.Frame(self.screen, bg="#121212")
        tk.Label(mobile_recharge, text="Mobile Recharge", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.mobile_number = ttk.Entry(mobile_recharge, width=30)
        self.mobile_number.pack(pady=5)
        self.recharge_amount = ttk.Entry(mobile_recharge, width=30)
        self.recharge_amount.pack(pady=5)
        tk.Button(mobile_recharge, text="Recharge", command=self.process_mobile_recharge).pack(pady=5)
        tk.Button(mobile_recharge, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["mobile-recharge-screen"] = mobile_recharge

        # Cheque Book Request Screen
        cheque_book = tk.Frame(self.screen, bg="#121212")
        tk.Label(cheque_book, text="Request Cheque Book", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        tk.Label(cheque_book, text="Request a new cheque book (25 leaves) to be mailed to your address.",
                 bg="#121212", fg="#e6e6e6").pack()
        tk.Button(cheque_book, text="Confirm Request", command=self.process_cheque_book_request).pack(pady=5)
        tk.Button(cheque_book, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["cheque-book-screen"] = cheque_book

        # Cardless Withdrawal Screen
        cardless_withdrawal = tk.Frame(self.screen, bg="#121212")
        tk.Label(cardless_withdrawal, text="Cardless Withdrawal", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.cardless_code = ttk.Entry(cardless_withdrawal, width=30)
        self.cardless_code.pack(pady=5)
        self.cardless_amount = ttk.Entry(cardless_withdrawal, width=30)
        self.cardless_amount.pack(pady=5)
        tk.Button(cardless_withdrawal, text="Withdraw", command=self.process_cardless_withdrawal).pack(pady=5)
        tk.Button(cardless_withdrawal, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["cardless-withdrawal-screen"] = cardless_withdrawal

        # Exchange Phone Number Screen
        exchange_phone = tk.Frame(self.screen, bg="#121212")
        tk.Label(exchange_phone, text="Exchange Phone Number", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.current_phone = ttk.Entry(exchange_phone, width=30)
        self.current_phone.pack(pady=5)
        self.new_phone = ttk.Entry(exchange_phone, width=30)
        self.new_phone.pack(pady=5)
        tk.Button(exchange_phone, text="Change Number", command=self.process_exchange_phone_number).pack(pady=5)
        tk.Button(exchange_phone, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["exchange-phone-screen"] = exchange_phone

        # New Card Screen
        new_card = tk.Frame(self.screen, bg="#121212")
        tk.Label(new_card, text="Add New Card", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.new_card_number = ttk.Entry(new_card, width=30)
        self.new_card_number.pack(pady=5)
        frame = tk.Frame(new_card, bg="#121212")
        frame.pack()
        self.new_expiry_date = ttk.Entry(frame, width=30)
        self.new_expiry_date.pack(side="left", padx=5)
        self.new_cvv = ttk.Entry(frame, width=30)
        self.new_cvv.pack(side="left", padx=5)
        self.new_card_new_pin = ttk.Entry(new_card, show="*", width=30)
        self.new_card_new_pin.pack(pady=5)
        self.new_card_confirm_pin = ttk.Entry(new_card, show="*", width=30)
        self.new_card_confirm_pin.pack(pady=5)
        self.new_card_email = ttk.Entry(new_card, width=30)
        self.new_card_email.pack(pady=5)
        tk.Button(new_card, text="Add Card", command=self.add_new_card).pack(pady=5)
        tk.Button(new_card, text="Back", font=("Poppins", 14, "bold"), command=self.show_welcome_screen).pack(pady=5)
        self.screens["new-card-screen"] = new_card

        # Verify Email Screen
        verify_email = tk.Frame(self.screen, bg="#121212")
        tk.Label(verify_email, text="Verify Email", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.verify_email_input = ttk.Entry(verify_email, width=30)
        self.verify_email_input.pack(pady=5)
        tk.Button(verify_email, text="Send Code", command=self.send_verification_code).pack(pady=5)
        tk.Label(verify_email, text="Enter the verification code sent to your email:", bg="#121212", fg="#e6e6e6").pack()
        self.verification_code = ttk.Entry(verify_email, width=30)
        self.verification_code.pack(pady=5)
        tk.Button(verify_email, text="Verify", command=self.verify_email).pack(pady=5)
        tk.Button(verify_email, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["verify-email-screen"] = verify_email

        # Apply New Card Screen
        apply_new_card = tk.Frame(self.screen, bg="#121212")
        tk.Label(apply_new_card, text="Apply for New Card", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.old_card_number = ttk.Entry(apply_new_card, width=30)
        self.old_card_number.pack(pady=5)
        self.old_expiry_date = ttk.Entry(apply_new_card, width=30)
        self.old_expiry_date.pack(pady=5)
        self.old_cvv = ttk.Entry(apply_new_card, width=30)
        self.old_cvv.pack(pady=5)
        self.apply_new_card_email = ttk.Entry(apply_new_card, width=30)
        self.apply_new_card_email.pack(pady=5)
        tk.Button(apply_new_card, text="Submit", command=self.apply_new_card).pack(pady=5)
        tk.Button(apply_new_card, text="Back", font=("Poppins", 14, "bold"), command=self.show_others).pack(pady=5)
        self.screens["apply-new-card-screen"] = apply_new_card

        # Admin PIN Screen
        admin_pin = tk.Frame(self.screen, bg="#121212")
        tk.Label(admin_pin, text="Enter Admin PIN", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.admin_pin_input = ttk.Entry(admin_pin, show="*", width=30)
        self.admin_pin_input.pack(pady=5)
        tk.Button(admin_pin, text="Submit", command=self.verify_admin_pin).pack(pady=5)
        tk.Button(admin_pin, text="Back", font=("Poppins", 14, "bold"), command=self.show_welcome_screen).pack(pady=5)
        self.screens["admin-pin-screen"] = admin_pin

        # Admin Screen
        admin = tk.Frame(self.screen, bg="#121212")
        tk.Label(admin, text="Admin Dashboard", font=("Poppins", 20, "bold"), bg="#121212", fg="#00ccff").pack(pady=10)
        self.admin_display = scrolledtext.ScrolledText(admin, height=20, width=80, bg="#1c1c1c", fg="#ddd", font=("Poppins", 12))
        self.admin_display.pack(pady=10)
        tk.Button(admin, text="Export Data", command=self.export_admin_data).pack(pady=5)
        tk.Button(admin, text="Back", font=("Poppins", 14, "bold"), command=self.show_welcome_screen).pack(pady=5)
        self.screens["admin-screen"] = admin

    def show_screen(self, screen_id):
        for screen in self.screens.values():
            screen.pack_forget()
        self.screens[screen_id].pack(fill="both", expand=True)
        if screen_id != "main-menu":
            for btn in self.left_btns + self.right_btns:
                btn.config(state="disabled")
        else:
            self.update_function_buttons()
        if screen_id == "balance-screen":
            current_card = self.account['cards'][self.account['currentCardIndex']]
            self.balance_display.config(text=f"${current_card['balance']:.2f} USD")
        elif screen_id == "verify-email-screen":
            current_card = self.account['cards'][self.account['currentCardIndex']]
            self.verify_email_input.delete(0, tk.END)
            self.verify_email_input.insert(0, current_card['email'] or '')
            self.current_input_field = self.verify_email_input
        elif screen_id == "apply-new-card-screen":
            current_card = self.account['cards'][self.account['currentCardIndex']]
            self.old_card_number.delete(0, tk.END)
            self.old_card_number.insert(0, current_card['cardNumber'])
            self.old_expiry_date.delete(0, tk.END)
            self.old_expiry_date.insert(0, current_card['expiryDate'])
            self.old_cvv.delete(0, tk.END)
            self.old_cvv.insert(0, current_card['cvv'])
            self.apply_new_card_email.delete(0, tk.END)
            self.apply_new_card_email.insert(0, current_card['email'] or '')
            self.current_input_field = self.old_card_number
        elif screen_id == "admin-screen":
            self.display_admin_data()
        elif screen_id == "admin-pin-screen":
            self.admin_pin_input.delete(0, tk.END)
            self.current_input_field = self.admin_pin_input

    def update_function_buttons(self):
        for btn in self.left_btns + self.right_btns:
            btn.config(state="normal")
        self.left_btns[0].config(command=self.show_deposit)
        self.left_btns[1].config(command=self.show_transfer)
        self.left_btns[2].config(command=self.show_pin_change)
        self.left_btns[3].config(command=self.show_others)
        self.right_btns[0].config(command=self.show_fast_cash)
        self.right_btns[1].config(command=self.show_withdraw)
        self.right_btns[2].config(command=self.show_balance)
        self.right_btns[3].config(command=self.show_mini_statement)

    def handle_left_button(self, text):
        if text == "Deposit": self.show_deposit()
        elif text == "Transfer": self.show_transfer()
        elif text == "PIN Change": self.show_pin_change()
        elif text == "Others": self.show_others()

    def handle_right_button(self, text):
        if text == "Fast Cash": self.show_fast_cash()
        elif text == "Cash Withdrawal": self.show_withdraw()
        elif text == "Balance Enquiry": self.show_balance()
        elif text == "Mini Statement": self.show_mini_statement()

    def is_card_expired(self, expiry_date):
        month, year = map(int, expiry_date.split('/'))
        expiry = datetime(year, month, 1)
        return datetime.now() > expiry

    def send_email(self, to_email, subject, body):
        if not to_email:
            return False
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = f"Learn-Atm <{self.SMTP_USERNAME}>"
        msg['To'] = to_email
        try:
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(self.SMTP_USERNAME, to_email, msg.as_string())
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_verification_code(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        email = self.verify_email_input.get()
        if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        current_card['email'] = email
        verification_code = str(random.randint(100000, 999999))
        self.verification_codes[email] = verification_code
        subject = "ATM Email Verification Code"
        body = f"Your verification code is: {verification_code}\nPlease enter this code in the ATM to verify your email."
        if self.send_email(email, subject, body):
            messagebox.showinfo("Success", f"Verification code sent to {email}")
            self.current_input_field = self.verification_code
        else:
            messagebox.showerror("Error", "Failed to send verification code.")

    def verify_email(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        code = self.verification_code.get()
        if not code:
            messagebox.showerror("Error", "Please enter a verification code!")
            return
        if current_card['email'] in self.verification_codes and self.verification_codes[current_card['email']] == code:
            current_card['emailVerified'] = True
            del self.verification_codes[current_card['email']]
            messagebox.showinfo("Success", "Email verified successfully!")
            self.show_others()
        else:
            messagebox.showerror("Error", "Invalid verification code!")

    def send_transaction_notification(self, email, message):
        if not email:
            return False
        subject = "ATM Transaction Notification"
        body = f"Transaction Notification:\n{message}\nDate: {datetime.now()}"
        return self.send_email(email, subject, body)

    def submit_card_number(self, card_number):
        current_card = next((c for c in self.account['cards'] if c['cardNumber'] == card_number and c['verified'] and not c['blocked']), None)
        if current_card:
            self.account['currentCardIndex'] = self.account['cards'].index(current_card)
            self.show_screen("pin-screen")
            self.current_input_field = self.screens["pin-screen"].winfo_children()[1]
        else:
            messagebox.showerror("Error", "Invalid, unverified, or blocked card number!")

    def submit_pin(self, pin):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if pin == current_card['pin']:
            if self.is_card_expired(current_card['expiryDate']):
                messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
                self.show_others()
                self.root.after(100, self.show_apply_new_card)
            else:
                self.show_screen("main-menu")
                self.current_input_field = None
        else:
            messagebox.showerror("Error", "Invalid PIN!")

    def select_currency(self, currency):
        self.selected_currency = currency
        rate = self.exchange_rates[currency]
        self.currency_rate_display.config(text=f"Selected Currency: {currency} (1 USD = {rate} {currency})")
        self.update_preset_buttons()

    def update_preset_buttons(self):
        for btn, amount in zip(self.preset_btns, [50, 100, 150]):
            btn.config(text=f"{amount} {self.selected_currency}")

    def set_withdraw_amount(self, amount):
        self.withdraw_amount.delete(0, tk.END)
        self.withdraw_amount.insert(0, str(amount))

    def show_balance(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.show_screen("balance-screen")

    def show_withdraw(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.withdraw_amount.delete(0, tk.END)
        self.select_currency("USD")
        self.show_screen("withdraw-screen")
        self.current_input_field = self.withdraw_amount

    def show_fast_cash(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.show_screen("fast-cash-screen")

    def show_deposit(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.deposit_amount.delete(0, tk.END)
        self.show_screen("deposit-screen")
        self.current_input_field = self.deposit_amount

    def show_transfer(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.transfer_account.delete(0, tk.END)
        self.transfer_amount.delete(0, tk.END)
        self.show_screen("transfer-screen")
        self.current_input_field = self.transfer_account

    def show_pin_change(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.old_pin.delete(0, tk.END)
        self.new_pin.delete(0, tk.END)
        self.show_screen("pin-change-screen")
        self.current_input_field = self.old_pin

    def show_mini_statement(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.mini_statement_display.delete(1.0, tk.END)
        if not current_card['transactions']:
            self.mini_statement_display.insert(tk.END, "No transactions available.")
        else:
            for t in current_card['transactions'][-5:]:
                self.mini_statement_display.insert(tk.END, f"{t}\n")
        self.show_screen("mini-statement-screen")

    def show_others(self):
        self.show_screen("others-screen")

    def back_to_menu(self):
        self.show_screen("main-menu")
        self.current_input_field = None

    def show_welcome_screen(self):
        self.screens["welcome-screen"].winfo_children()[1].delete(0, tk.END)
        self.show_screen("welcome-screen")
        self.current_input_field = self.screens["welcome-screen"].winfo_children()[1]

    def process_withdraw(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        try:
            amount = float(self.withdraw_amount.get())
            if amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount!")
                return
            amount_in_usd = amount / self.exchange_rates[self.selected_currency]
            tax_rate = self.tax_rates[self.selected_currency]
            tax_in_selected_currency = amount * tax_rate
            tax_in_usd = tax_in_selected_currency / self.exchange_rates[self.selected_currency]
            total_in_usd = amount_in_usd + tax_in_usd
            if total_in_usd > current_card['balance']:
                messagebox.showerror("Error", "Insufficient funds including tax!")
                return
            current_card['balance'] -= total_in_usd
            transaction_details = f"Withdrew {amount:.2f} {self.selected_currency} (Tax: {tax_in_selected_currency:.2f} {self.selected_currency}, Total: {total_in_usd:.2f} USD) on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            current_card['transactions'].append(transaction_details)
            if self.send_transaction_notification(current_card['email'], transaction_details):
                messagebox.showinfo("Success", f"Successfully withdrew:\n{total_in_usd:.2f} USD (Total)\n{amount:.2f} {self.selected_currency} (Withdrawal)\n+ {tax_in_selected_currency:.2f} {self.selected_currency} (Tax)\nNotification sent to {current_card['email']}")
            else:
                messagebox.showinfo("Success", f"Successfully withdrew:\n{total_in_usd:.2f} USD (Total)\n{amount:.2f} {self.selected_currency} (Withdrawal)\n+ {tax_in_selected_currency:.2f} {self.selected_currency} (Tax)")
            self.back_to_menu()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def process_fast_cash(self, amount):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        if amount > current_card['balance']:
            messagebox.showerror("Error", "Insufficient funds!")
        else:
            current_card['balance'] -= amount
            transaction_details = f"Fast Cash: Withdrew ${amount:.2f} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            current_card['transactions'].append(transaction_details)
            if self.send_transaction_notification(current_card['email'], transaction_details):
                messagebox.showinfo("Success", f"Successfully withdrew ${amount:.2f}\nNotification sent to {current_card['email']}")
            else:
                messagebox.showinfo("Success", f"Successfully withdrew ${amount:.2f}")
            self.back_to_menu()

    def process_deposit(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        try:
            amount = float(self.deposit_amount.get())
            if amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount!")
            else:
                current_card['balance'] += amount
                transaction_details = f"Deposited ${amount:.2f} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                current_card['transactions'].append(transaction_details)
                if self.send_transaction_notification(current_card['email'], transaction_details):
                    messagebox.showinfo("Success", f"Successfully deposited ${amount:.2f}\nNotification sent to {current_card['email']}")
                else:
                    messagebox.showinfo("Success", f"Successfully deposited ${amount:.2f}")
                self.back_to_menu()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def process_transfer(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        account_number = self.transfer_account.get()
        try:
            amount = float(self.transfer_amount.get())
            if not account_number or len(account_number) < 8:
                messagebox.showerror("Error", "Please enter a valid account number!")
            elif amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount!")
            elif amount > current_card['balance']:
                messagebox.showerror("Error", "Insufficient funds!")
            else:
                current_card['balance'] -= amount
                transaction_details = f"Transferred ${amount:.2f} to {account_number} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                current_card['transactions'].append(transaction_details)
                if self.send_transaction_notification(current_card['email'], transaction_details):
                    messagebox.showinfo("Success", f"Successfully transferred ${amount:.2f} to account {account_number}\nNotification sent to {current_card['email']}")
                else:
                    messagebox.showinfo("Success", f"Successfully transferred ${amount:.2f} to account {account_number}")
                self.back_to_menu()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def process_pin_change(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        old_pin = self.old_pin.get()
        new_pin = self.new_pin.get()
        if old_pin != current_card['pin']:
            messagebox.showerror("Error", "Incorrect old PIN!")
        elif len(new_pin) != 4 or not new_pin.isdigit():
            messagebox.showerror("Error", "New PIN must be a 4-digit number!")
        else:
            current_card['pin'] = new_pin
            transaction_details = f"PIN changed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            current_card['transactions'].append(transaction_details)
            if self.send_transaction_notification(current_card['email'], transaction_details):
                messagebox.showinfo("Success", f"PIN successfully changed!\nNotification sent to {current_card['email']}")
            else:
                messagebox.showinfo("Success", "PIN successfully changed!")
            self.back_to_menu()

    def show_bill_payment(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.bill_id.delete(0, tk.END)
        self.bill_amount.delete(0, tk.END)
        self.show_screen("bill-payment-screen")
        self.current_input_field = self.bill_id

    def process_bill_payment(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        bill_id = self.bill_id.get()
        try:
            amount = float(self.bill_amount.get())
            if not bill_id:
                messagebox.showerror("Error", "Please enter a valid bill ID!")
            elif amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount!")
            elif amount > current_card['balance']:
                messagebox.showerror("Error", "Insufficient funds!")
            else:
                current_card['balance'] -= amount
                transaction_details = f"Bill Payment of ${amount:.2f} for Bill ID {bill_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                current_card['transactions'].append(transaction_details)
                if self.send_transaction_notification(current_card['email'], transaction_details):
                    messagebox.showinfo("Success", f"Successfully paid ${amount:.2f} for bill ID {bill_id}\nNotification sent to {current_card['email']}")
                else:
                    messagebox.showinfo("Success", f"Successfully paid ${amount:.2f} for bill ID {bill_id}")
                self.show_others()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def show_mobile_recharge(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.mobile_number.delete(0, tk.END)
        self.recharge_amount.delete(0, tk.END)
        self.show_screen("mobile-recharge-screen")
        self.current_input_field = self.mobile_number

    def process_mobile_recharge(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        mobile_number = self.mobile_number.get()
        try:
            amount = float(self.recharge_amount.get())
            if not mobile_number or len(mobile_number) != 10:
                messagebox.showerror("Error", "Please enter a valid 10-digit mobile number!")
            elif amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount!")
            elif amount > current_card['balance']:
                messagebox.showerror("Error", "Insufficient funds!")
            else:
                current_card['balance'] -= amount
                transaction_details = f"Mobile Recharge of ${amount:.2f} for {mobile_number} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                current_card['transactions'].append(transaction_details)
                if self.send_transaction_notification(current_card['email'], transaction_details):
                    messagebox.showinfo("Success", f"Successfully recharged ${amount:.2f} for mobile number {mobile_number}\nNotification sent to {current_card['email']}")
                else:
                    messagebox.showinfo("Success", f"Successfully recharged ${amount:.2f} for mobile number {mobile_number}")
                self.show_others()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def show_cheque_book_request(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.show_screen("cheque-book-screen")

    def process_cheque_book_request(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        transaction_details = f"Cheque Book requested on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        current_card['transactions'].append(transaction_details)
        if self.send_transaction_notification(current_card['email'], transaction_details):
            messagebox.showinfo("Success", f"Cheque book request successful! It will be mailed to your registered address.\nNotification sent to {current_card['email']}")
        else:
            messagebox.showinfo("Success", "Cheque book request successful! It will be mailed to your registered address.")
        self.show_others()

    def show_cardless_withdrawal(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.cardless_code.delete(0, tk.END)
        self.cardless_amount.delete(0, tk.END)
        self.show_screen("cardless-withdrawal-screen")
        self.current_input_field = self.cardless_code

    def process_cardless_withdrawal(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        code = self.cardless_code.get()
        try:
            amount = float(self.cardless_amount.get())
            if code != "XYZ123":
                messagebox.showerror("Error", "Invalid withdrawal code!")
            elif amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount!")
            elif amount > current_card['balance']:
                messagebox.showerror("Error", "Insufficient funds!")
            else:
                current_card['balance'] -= amount
                transaction_details = f"Cardless Withdrawal of ${amount:.2f} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                current_card['transactions'].append(transaction_details)
                if self.send_transaction_notification(current_card['email'], transaction_details):
                    messagebox.showinfo("Success", f"Successfully withdrew ${amount:.2f} using cardless withdrawal\nNotification sent to {current_card['email']}")
                else:
                    messagebox.showinfo("Success", f"Successfully withdrew ${amount:.2f} using cardless withdrawal")
                self.show_others()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def show_exchange_phone_number(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        self.current_phone.delete(0, tk.END)
        self.current_phone.insert(0, current_card['phoneNumber'])
        self.new_phone.delete(0, tk.END)
        self.show_screen("exchange-phone-screen")
        self.current_input_field = self.new_phone

    def process_exchange_phone_number(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        current_phone = self.current_phone.get()
        new_phone = self.new_phone.get()
        if current_phone != current_card['phoneNumber']:
            messagebox.showerror("Error", "Current phone number does not match!")
        elif not new_phone or len(new_phone) != 10:
            messagebox.showerror("Error", "Please enter a valid 10-digit new phone number!")
        else:
            current_card['phoneNumber'] = new_phone
            transaction_details = f"Phone number changed to {new_phone} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            current_card['transactions'].append(transaction_details)
            if self.send_transaction_notification(current_card['email'], transaction_details):
                messagebox.showinfo("Success", f"Phone number successfully changed!\nNotification sent to {current_card['email']}")
            else:
                messagebox.showinfo("Success", "Phone number successfully changed!")
            self.back_to_menu()

    def show_new_card_screen(self):
        self.new_card_number.delete(0, tk.END)
        self.new_expiry_date.delete(0, tk.END)
        self.new_cvv.delete(0, tk.END)
        self.new_card_new_pin.delete(0, tk.END)
        self.new_card_confirm_pin.delete(0, tk.END)
        self.new_card_email.delete(0, tk.END)
        self.show_screen("new-card-screen")
        self.current_input_field = self.new_card_number

    def add_new_card(self):
        new_card_number = self.new_card_number.get()
        new_expiry_date = self.new_expiry_date.get()
        new_cvv = self.new_cvv.get()
        new_pin = self.new_card_new_pin.get()
        confirm_pin = self.new_card_confirm_pin.get()
        new_email = self.new_card_email.get()
        if not new_card_number or len(new_card_number) != 16:
            messagebox.showerror("Error", "Please enter a valid 16-digit card number!")
            return
        if not new_expiry_date or not re.match(r'^\d{2}/\d{4}$', new_expiry_date):
            messagebox.showerror("Error", "Please enter a valid expiry date in MM/YYYY format!")
            return
        if not new_cvv or len(new_cvv) != 3 or not new_cvv.isdigit():
            messagebox.showerror("Error", "Please enter a valid 3-digit CVV!")
            return
        if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
            messagebox.showerror("Error", "Please enter a valid 4-digit PIN!")
            return
        if new_pin != confirm_pin:
            messagebox.showerror("Error", "PIN and Confirm PIN do not match!")
            return
        if new_email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', new_email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        new_card = {
            'cardNumber': new_card_number,
            'expiryDate': new_expiry_date,
            'cvv': new_cvv,
            'pin': new_pin,
            'balance': 0,
            'transactions': [],
            'phoneNumber': "1234567890",
            'verified': True,
            'blocked': False,
            'email': new_email,
            'emailVerified': False
        }
        self.account['cards'].append(new_card)
        message = f"New card added successfully!\nCard Number: {new_card_number}\nExpiry Date: {new_expiry_date}\nCVV: {new_cvv}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if new_email and self.send_transaction_notification(new_email, message):
            messagebox.showinfo("Success", f"New card added successfully!\nNotification sent to {new_email}")
        else:
            messagebox.showinfo("Success", "New card added successfully! Email notification failed.")
        self.show_welcome_screen()

    def download_statement(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        transactions = "No transactions available." if not current_card['transactions'] else "\n".join(current_card['transactions'])
        with open(f"transaction_history_{current_card['cardNumber']}.txt", "w") as f:
            f.write(transactions)
        messagebox.showinfo("Success", "Transaction history downloaded!")

    def update_block_unblock_button(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if current_card['blocked']:
            self.screens["others-screen"].winfo_children()[6].config(text="Unblock Card",
                command=lambda: self.process_block_unblock(False))
        else:
            self.screens["others-screen"].winfo_children()[6].config(text="Block Card",
                command=lambda: self.process_block_unblock(True))
        self.show_others()

    def process_block_unblock(self, block):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        if self.is_card_expired(current_card['expiryDate']):
            messagebox.showwarning("Warning", "Your card is expired! Redirecting to apply for a new card.")
            self.show_others()
            self.root.after(100, self.show_apply_new_card)
            return
        current_card['blocked'] = block
        action = "blocked" if block else "unblocked"
        transaction_details = f"Card {action} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        current_card['transactions'].append(transaction_details)
        if self.send_transaction_notification(current_card['email'], transaction_details):
            messagebox.showinfo("Success", f"Card has been {action}!\nNotification sent to {current_card['email']}")
        else:
            messagebox.showinfo("Success", f"Card has been {action}!")
        if block:
            self.show_welcome_screen()
        else:
            self.show_others()

    def show_verify_email(self):
        self.show_screen("verify-email-screen")
        self.current_input_field = self.verify_email_input

    def show_apply_new_card(self):
        current_card = self.account['cards'][self.account['currentCardIndex']]
        self.old_card_number.delete(0, tk.END)
        self.old_card_number.insert(0, current_card['cardNumber'])
        self.old_expiry_date.delete(0, tk.END)
        self.old_expiry_date.insert(0, current_card['expiryDate'])
        self.old_cvv.delete(0, tk.END)
        self.old_cvv.insert(0, current_card['cvv'])
        self.apply_new_card_email.delete(0, tk.END)
        self.apply_new_card_email.insert(0, current_card['email'] or '')
        self.show_screen("apply-new-card-screen")
        self.current_input_field = self.old_card_number

    def apply_new_card(self):
        old_card_number = self.old_card_number.get()
        old_expiry_date = self.old_expiry_date.get()
        old_cvv = self.old_cvv.get()
        new_email = self.apply_new_card_email.get()
        if not old_card_number or len(old_card_number) != 16:
            messagebox.showerror("Error", "Please enter a valid 16-digit old card number!")
            return
        if not old_expiry_date or not re.match(r'^\d{2}/\d{4}$', old_expiry_date):
            messagebox.showerror("Error", "Please enter a valid old expiry date in MM/YYYY format!")
            return
        if not old_cvv or len(old_cvv) != 3 or not old_cvv.isdigit():
            messagebox.showerror("Error", "Please enter a valid 3-digit old CVV!")
            return
        if new_email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', new_email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        old_card = next((c for c in self.account['cards'] if c['cardNumber'] == old_card_number and c['expiryDate'] == old_expiry_date and c['cvv'] == old_cvv), None)
        if not old_card:
            messagebox.showerror("Error", "Old card details do not match any existing card!")
            return
        if not self.is_card_expired(old_card['expiryDate']):
            messagebox.showerror("Error", "This card is not expired yet!")
            return
        current_date = datetime.now()
        new_expiry_year = current_date.year + 5
        new_expiry_month = str(current_date.month).zfill(2)
        new_expiry_date = f"{new_expiry_month}/{new_expiry_year}"
        first_digit = random.randint(1, 9)
        remaining_digits = str(random.randint(0, 99999999999999)).zfill(15)
        new_card_number = f"{first_digit}{remaining_digits}"
        new_cvv = str(random.randint(100, 999))
        new_card = {
            'cardNumber': new_card_number,
            'expiryDate': new_expiry_date,
            'cvv': new_cvv,
            'pin': old_card['pin'],
            'balance': old_card['balance'],
            'transactions': old_card['transactions'],
            'phoneNumber': old_card['phoneNumber'],
            'verified': True,
            'blocked': False,
            'email': new_email or old_card['email'],
            'emailVerified': old_card['emailVerified'] and new_email == old_card['email']
        }
        self.account['cards'].append(new_card)
        self.account['cards'] = [c for c in self.account['cards'] if c['cardNumber'] != old_card_number]
        message = f"New card applied successfully!\nNew Card Number: {new_card_number}\nNew Expiry Date: {new_expiry_date}\nNew CVV stainless steel is made of iron, chromium, and sometimes nickel and other metals. Steel is an alloy and it is the combination of multiple metals that lends it its strength and durability. Stainless steel is corrosion resistant because of the chromium it contains, which forms a protective oxide layer on the surface of the metal that prevents rust from forming. The addition of nickel improves corrosion resistance in acidic environments and increases durability.: {new_cvv}\nOld Card Number: {old_card_number} has been replaced.\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if new_card['email'] and self.send_transaction_notification(new_card['email'], message):
            messagebox.showinfo("Success", f"New card applied successfully!\nNew Card Number: {new_card_number}\nExpiry Date: {new_expiry_date}\nCVV: {new_cvv}\nNotification sent to {new_card['email']}")
        else:
            messagebox.showinfo("Success", f"New card applied successfully!\nNew Card Number: {new_card_number}\nExpiry Date: {new_expiry_date}\nCVV: {new_cvv}\nFailed to send notification to {new_card['email']}")
        self.show_welcome_screen()

    def show_admin_pin_screen(self):
        self.show_screen("admin-pin-screen")
        self.current_input_field = self.admin_pin_input

    def verify_admin_pin(self):
        pin = self.admin_pin_input.get()
        if pin == self.ADMIN_PIN:
            self.show_screen("admin-screen")
            self.current_input_field = None
        else:
            messagebox.showerror("Error", "Invalid Admin PIN!")
            self.show_welcome_screen()

    def display_admin_data(self):
        self.admin_display.delete(1.0, tk.END)
        self.admin_display.insert(tk.END, "Customer Accounts Overview\n")
        self.admin_display.insert(tk.END, "=" * 80 + "\n\n")
        for idx, card in enumerate(self.account['cards']):
            status = "Blocked" if card['blocked'] else "Active"
            email_status = "Verified" if card['emailVerified'] else "Not Verified"
            expired = "Expired" if self.is_card_expired(card['expiryDate']) else "Valid"
            self.admin_display.insert(tk.END, f"Account {idx + 1}:\n")
            self.admin_display.insert(tk.END, f"  Card Number: {card['cardNumber']}\n")
            self.admin_display.insert(tk.END, f"  Balance: ${card['balance']:.2f} USD\n")
            self.admin_display.insert(tk.END, f"  Status: {status}\n")
            self.admin_display.insert(tk.END, f"  Expiry Date: {card['expiryDate']} ({expired})\n")
            self.admin_display.insert(tk.END, f"  Email: {card['email'] or 'Not Provided'} ({email_status})\n")
            self.admin_display.insert(tk.END, f"  Phone Number: {card['phoneNumber']}\n")
            self.admin_display.insert(tk.END, f"  CVV: {card['cvv']}\n")
            self.admin_display.insert(tk.END, "  Transactions:\n")
            if not card['transactions']:
                self.admin_display.insert(tk.END, "    No transactions available.\n")
            else:
                for t in card['transactions'][-5:]:
                    self.admin_display.insert(tk.END, f"    {t}\n")
            self.admin_display.insert(tk.END, "-" * 80 + "\n\n")

    def export_admin_data(self):
        data = {
            "cards": [
                {
                    "cardNumber": card['cardNumber'],
                    "balance": card['balance'],
                    "status": "Blocked" if card['blocked'] else "Active",
                    "expiryDate": card['expiryDate'],
                    "expired": self.is_card_expired(card['expiryDate']),
                    "email": card['email'] or "Not Provided",
                    "emailVerified": card['emailVerified'],
                    "phoneNumber": card['phoneNumber'],
                    "cvv": card['cvv'],
                    "transactions": card['transactions'][-5:]
                }
                for card in self.account['cards']
            ]
        }
        with open("admin_customer_data.json", "w") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Success", "Customer data exported to admin_customer_data.json!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ATMApp(root)
    root.mainloop()