""" pricing_gender.py

SUMMARY: Part 3 of a survey and analysis of tutors (the competition).
Fixes issues with highest_degree and gender from Parts 1 and 2.

Part 1: wyzant_pricing.py.
Part 2: wyzant_pricing_detail.py
Part 3: pricing_gender.py

REPOSITORY: https://github.com/DavidJLambert/Selenium

AUTHOR: David J. Lambert

VERSION: 0.6.0

DATE: May 31, 2023
"""
import sqlite3
import gender_guesser.detector as gender_guesser

# CONSTANTS.
DB_PATH = r'C:\Users\david\Desktop\Wyzant\Pricing\Pricing.sqlite3'

# Instantiate gender guesser
""" Output:
unknown (name not found), saved as Unk
andy (androgynous), saved as And
male, saved as M
female, saved as F
mostly_male, saved as M?
mostly_female, saved as F?
"""
guess = gender_guesser.Detector()
guess_dict = {'unknown': 'Unk',
              'andy': 'And',
              'male': 'M',
              'female': 'F',
              'mostly_male': 'M?',
              'mostly_female': 'F?'}

degree_dict = {'None': 0,
               'BS': 1,
               'MS': 2,
               'PhD': 3,
               'Dr': 3}


def main():
    """ Function main.

    Parameters:
    Returns:
    """
    # Connect to database.
    connection = sqlite3.connect(database=DB_PATH, timeout=10)
    cursor = connection.cursor()

    # Find tutors who need details from their profile added.
    sql = ("SELECT Name, ID, gender, highest_degree "
           "FROM Tutors")
    cursor.execute(sql)
    rows = cursor.fetchall()

    for row_number, row in enumerate(rows):
        tutor_name, tutor_id, prev_gender, prev_highest_degree = row
        name_parts = tutor_name.split()

        # Process multi-part names.
        new_degree = ""
        new_name_parts = []  # The items in name_parts that aren't titles, degrees, or single characters.
        gender_parts = []  # The gender of names in new_name_parts that are "M", "M?", "F", or "F?"
        for name_part in name_parts:
            name_part = name_part.replace(".", "").replace(")", "").replace("(", "")
            if name_part in ["Ms", "Miss", "Mrs"]:
                gender_parts.append("F")
            elif name_part == "Mr":
                gender_parts.append("M")
            elif name_part in ["Dr", "PhD", "Prof", "Md"]:
                if degree_dict[prev_highest_degree] < 3:
                    new_degree = "PhD"
            elif len(name_part) > 1:
                new_name_parts.append(name_part)
                gender_part = guess_dict[guess.get_gender(name_part)]
                if gender_part not in ["And", "Unk"]:
                    # "And" and "Unk" useless info, only use M, M?, F, F?.
                    gender_parts.append(gender_part)
            if len(gender_parts) > 2:
                print("MAXLEN: ", len(gender_parts))

        # Process gender info.
        new_gender = ""  # No change.
        if len(gender_parts) == 1:
            candidate_gender = gender_parts[0]
            if prev_gender in ["Unk", "And"]:
                new_gender = candidate_gender
                # print("Assign definite gender:", new_gender, prev_gender)
            elif prev_gender == candidate_gender + '?':
                new_gender = candidate_gender
                # print("Promote F? to F or M? to M:", new_gender, prev_gender)
            elif candidate_gender == prev_gender + '?':
                new_gender = ""  # Let's not demote F to F? or M to M?.
            elif candidate_gender == prev_gender:
                new_gender = ""  # No change.
            else:
                new_gender = ""  # Inconsistent results.  Leave old value.
        elif len(gender_parts) == 2:
            gender_parts.sort()
            if gender_parts[0][0] != gender_parts[1][0]:
                new_gender = ""  # Inconsistent results.  Leave old value.
            elif gender_parts[0][0] == gender_parts[1][0]:
                candidate_gender = gender_parts[0]
                if prev_gender in ["Unk", "And"] and candidate_gender[0] in ["M", "F"]:
                    new_gender = candidate_gender  # print("Assign definite gender:", new_gender, prev_gender)
                elif prev_gender == new_gender + '?':
                    new_gender = candidate_gender  # print("Promote F? to F or M? to M:", new_gender, prev_gender)
                else:
                    new_gender = ""  # Pass on other options.
            else:
                new_gender = ""  # Pass on other options.
        elif len(gender_parts) >= 3:
            new_gender = ""
            print("EXTRA LONG")

        if new_degree != "":
            sql = "UPDATE Tutors SET Highest_Degree = ? WHERE ID = ?"
            cursor.execute(sql, ["PhD", tutor_id])
        if new_gender != "":
            sql = "UPDATE Tutors SET Gender = ? WHERE ID = ?"
            cursor.execute(sql, [new_gender, tutor_id])

    # Final commit, disconnect from database.
    connection.commit()
    cursor.close()
    connection.close()
    print("ALL DONE.")
# End of function main.


if __name__ == '__main__':
    main()

