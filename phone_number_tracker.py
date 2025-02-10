import tkinter as tk
from tkinter import StringVar, Label, Entry, Button, Frame, Listbox, Scrollbar, END, messagebox, Menu
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from datetime import datetime
import pytz
import csv
import webbrowser
import pyperclip

# Function to validate phone number
def validate_phone_number(number):
    try:
        parsed_number = phonenumbers.parse(number)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

# Function to track phone number
def Track():
    enter_number = entry.get()
    if not validate_phone_number(enter_number):
        messagebox.showerror("Invalid Number", "Please enter a valid phone number")
        return

    number = phonenumbers.parse(enter_number)

    # Add number to history listbox
    if enter_number not in history_listbox.get(0, END):
        history_listbox.insert(END, enter_number)

    display_information(number)

# Function to display information based on phone number
def display_information(number):
    try:
        # Country
        locate = geocoder.description_for_number(number, 'en')
        country_value.set(f"Country: {locate}")

        # Operator
        operator = carrier.name_for_number(number, 'en')
        sim_value.set(f"SIM: {operator}")

        # Timezone
        time_zones = timezone.time_zones_for_number(number)
        zone_value.set(f"Timezone: {', '.join(time_zones)}")

        # Longitude and Latitude
        geolocator = Nominatim(user_agent='geoapiExercises')
        location = geolocator.geocode(locate)
        if location:
            longitude_value.set(f"Longitude: {location.longitude}")
            latitude_value.set(f"Latitude: {location.latitude}")

            # Additional geographical information
            address_parts = location.address.split(',')
            city_value.set(f"City: {address_parts[-5].strip() if len(address_parts) > 4 else 'Unknown'}")
            state_value.set(f"State: {address_parts[-3].strip() if len(address_parts) > 2 else 'Unknown'}")

            # Phone time
            obj = TimezoneFinder()
            result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
            if result:
                home = pytz.timezone(result)
                local_time = datetime.now(home)
                phone_time_value.set(f"Phone Time: {local_time.strftime('%I:%M %p')}")
            else:
                phone_time_value.set("Phone Time: Unknown")

            # Enable map button
            show_on_map_button.config(state="normal", command=lambda: webbrowser.open(f"https://www.google.com/maps?q={location.latitude},{location.longitude}"))
        else:
            # Reset values if location is unknown
            longitude_value.set("Longitude: Unknown")
            latitude_value.set("Latitude: Unknown")
            city_value.set("City: Unknown")
            state_value.set("State: Unknown")
            phone_time_value.set("Phone Time: Unknown")
            show_on_map_button.config(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to load number from history listbox
def load_from_history(event):
    # Check if an item is selected
    if history_listbox.curselection():
        selected_number = history_listbox.get(history_listbox.curselection())
        entry.set(selected_number)
        number = phonenumbers.parse(selected_number)
        display_information(number)
    else:
        messagebox.showerror("Selection Error", "No phone number selected from history.")

# Function to clear history listbox
def clear_history():
    history_listbox.delete(0, END)

# Function to export history to a CSV file
def export_history():
    try:
        with open("phone_number_history.csv", "w", newline="") as file:
            writer = csv.writer(file)
            for number in history_listbox.get(0, END):
                writer.writerow([number])
        messagebox.showinfo("Export History", "History exported successfully as phone_number_history.csv")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while exporting history: {str(e)}")

# Function to copy details to clipboard
def copy_to_clipboard():
    details = "\n".join([
        country_value.get(), sim_value.get(), zone_value.get(),
        phone_time_value.get(), longitude_value.get(),
        latitude_value.get(), city_value.get(), state_value.get()
    ])
    pyperclip.copy(details)
    messagebox.showinfo("Copied", "Phone number details copied to clipboard")

# Initialize Tkinter window
root = tk.Tk()
root.title("Phone Number Tracker")
root.geometry("600x700+300+50")
root.configure(bg="#f0f0f0")
root.resizable(False, False)

# Menu
menu = Menu(root)
root.config(menu=menu)
file_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Export History", command=export_history)
file_menu.add_command(label="Clear History", command=clear_history)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Entry Frame
entry_frame = Frame(root, bg="#34495e", padx=10, pady=10)
entry_frame.pack(fill=tk.X)

entry_label = Label(entry_frame, text="Enter phone number (with country code):", bg="#34495e", fg="white", font=("Arial", 12, "bold"))
entry_label.pack(side=tk.LEFT, padx=10)

entry = Entry(entry_frame, width=30, font=("Arial", 14), bd=2, relief=tk.GROOVE)
entry.pack(side=tk.LEFT, padx=10)

search_button = Button(entry_frame, text="Search", bg="#3498db", fg="white", font=("Arial", 12, "bold"), bd=2, relief=tk.RAISED, cursor="hand2", command=Track)
search_button.pack(side=tk.LEFT, padx=10)

# History Frame
history_frame = Frame(root, bg="#34495e", padx=10, pady=10)
history_frame.pack(fill=tk.BOTH, expand=True)

history_label = Label(history_frame, text="History", bg="#34495e", fg="white", font=("Arial", 12, "bold"))
history_label.pack(pady=(10, 5))

history_listbox = Listbox(history_frame, height=6, width=60, bg="#ecf0f1", font=("Arial", 12), selectbackground="#3498db", selectforeground="white")
history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(history_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

history_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=history_listbox.yview)

history_listbox.bind('<<ListboxSelect>>', load_from_history)

clear_history_button = Button(history_frame, text="Clear History", bg="red", fg="white", font=("Arial", 12, "bold"), bd=2, relief=tk.RAISED, cursor="hand2", command=clear_history)
clear_history_button.pack(pady=10, anchor=tk.E)

# Information Frame
info_frame = Frame(root, bg="#34495e", padx=20, pady=20)
info_frame.pack(fill=tk.BOTH, expand=True)

country_value = StringVar()
sim_value = StringVar()
zone_value = StringVar()
phone_time_value = StringVar()
longitude_value = StringVar()
latitude_value = StringVar()
city_value = StringVar()
state_value = StringVar()

labels = [
    Label(info_frame, textvariable=country_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=sim_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=zone_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=phone_time_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=longitude_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=latitude_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=city_value, bg="#34495e", fg="white", font=("Arial", 12, "bold")),
    Label(info_frame, textvariable=state_value, bg="#34495e", fg="white", font=("Arial", 12, "bold"))
]

for i, label in enumerate(labels):
    label.grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)

show_on_map_button = Button(info_frame, text="Show on Map", bg="#3498db", fg="white", font=("Arial", 12, "bold"), bd=2, relief=tk.RAISED, cursor="hand2", state=tk.DISABLED)
show_on_map_button.grid(row=8, column=0, columnspan=2, pady=(20, 10))

copy_to_clipboard_button = Button(info_frame, text="Copy to Clipboard", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), bd=2, relief=tk.RAISED, cursor="hand2", command=copy_to_clipboard)
copy_to_clipboard_button.grid(row=9, column=0, columnspan=2, pady=10)

root.mainloop()
