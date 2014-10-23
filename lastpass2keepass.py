"""lastpass2keepass - Convert a Lastpass Export to a Keepass XML Import File.

Supports:
Keepass XML - keepassxml

USAGE: python lastpass2keepass.py exportedTextFile

The LastPass Export format;
url,user,pass,1extra,name,grouping(\ delimited),last_touch,launch_count,fav

"""

import csv
import datetime
import re
import sys
import xml.etree.ElementTree as ET

# Global Strings
FILE_ERROR_MSG = "You either need more permissions or the file does not exist."
HORIZ_LINE = "____________________________________________________________\n"


def main():
    """Convert a Lastpass export to a valid CSV and that CSV to Keepass XML."""
    input_file_path, output_file_path = get_file_paths()
    parse_and_write_temp_csv(input_file_path, output_file_path)
    entries = read_temp_file(output_file_path)
    xml_document = generate_keepass_xml_document(entries)
    write_output(output_file_path, xml_document)
    formatted_print(
        "\n'{0}' has been succesfully converted to the KeePassXML format."
        "\nConverted data can be found in the '{1}' file.\n".format(
            input_file_path, output_file_path)
    )


def get_file_paths():
    """Get the input and output file paths, or print an error and exit."""
    try:
        input_file_path = sys.argv[1]
    except IndexError:
        print_and_exit("USAGE: python lastpass2keepass.py <lastpass-csv>")
    output_file_path = input_file_path + ".export.xml"
    return input_file_path, output_file_path


def parse_and_write_temp_csv(input_file_path, output_file_path):
    """Parse the input file and write it out as a standard CSV file.

    This takes care of lastpass idiosyncrasies such as multi line rows.

    """
    ROW_START_REGEX = re.compile('^http')
    DELIMITER_REGEX = re.compile(',\d\n')

    input_file, output_file = get_initial_file_handles(input_file_path,
                                                       output_file_path)

    for line in input_file.readlines():
        if ROW_START_REGEX.match(line):
            # Handle new rows
            output_file.write("\n" + line.strip())
        elif DELIMITER_REGEX.search(line):
            # Handle rows spanning multiple lines
            output_file.write(line.strip())
        else:
            # Replace new lines in fields with a placeholder we replace later.
            output_file.write(line.replace('\n', '|\t|'))

    input_file.close()
    output_file.close()


def get_initial_file_handles(input_file_path, output_file_path):
    """Get the input file and output file handles, exiting upon any IOErrors."""
    try:
        input_file = open(input_file_path)
    except IOError:
        print_and_exit("Cannot read file: '{0}' Error: '{1}'".format(
            input_file_path, FILE_ERROR_MSG))
    try:
        # Remove any content
        open(output_file_path, "w").close()
        output_file = open(output_file_path, "a")
    except IOError:
        print_and_exit("Cannot write to disk... exiting. Error: '{0}'".format(
            FILE_ERROR_MSG))
    return input_file, output_file


def read_temp_file(output_file_path):
    """Read a CSV file and return a list of it's rows.

    We require a list as Reader objects cannot be manipulated.

    """
    with open(output_file_path, "r") as output_file:
        reader = csv.reader(output_file, delimiter=',', quotechar='"')
        entries = [row for row in reader]
    entries.pop(0)      # Remove the CSV's Header row
    entries = sort_entries_by_category(entries)
    return entries


def sort_entries_by_category(entries):
    """Group a list of entries by category.

    Returns a list of tuples: [(category_name, entries)].

    """
    categories = {}
    for entry in entries:
        category = entry[5]
        if category in categories:
            categories[category].append(entry)
        else:
            categories[category] = [entry]
    sorted_categories = sorted(categories.items(), key=lambda x: x[1])
    return sorted_categories


def generate_keepass_xml_document(categories):
    """Generate a ElementTree XML Document from a list of grouped entries."""
    # Initialize tree
    page = ET.Element('database')
    doc = ET.ElementTree(page)
    _ = [add_category(page, category) for category in categories]
    return doc


def add_category(page, category_and_entries):
    """Create a Category XML tree appended to a page."""
    (category, entries) = category_and_entries

    head_element = ET.SubElement(page, "group")
    ET.SubElement(head_element, "title").text = str(category).decode("utf-8")
    ET.SubElement(head_element, "icon").text = "0"  # Lastpass has no icons

    _ = [add_entry(head_element, entry) for entry in entries]


def add_entry(parent_element, entry):
    """Add a Keepass XML entry to a parent element."""
    formatted_current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    entry_element = ET.SubElement(parent_element, "entry")
    element_name_to_element_text = {
        'title': str(entry[4]),
        'username': str(entry[1]),
        'password': str(entry[2]),
        'url': str(entry[0]),
        # Replace the newline placeholder we added earlier
        'comment': str(entry[3]).replace('|\t|', '\n').strip('"'),
        'icon': "0",
        'creation': formatted_current_time,
        'lastaccess': str(entry[5]),
        'lastmod': formatted_current_time,
        'expire': "Never"
    }
    for (name, text) in element_name_to_element_text.items():
        # Use decode for windows element appending errors
        ET.SubElement(entry_element, name).text = text.decode("utf-8")


def write_output(output_file_path, xml_document):
    """Write the final Keepass XML to an output file."""
    with open(output_file_path, "w") as output_file:
        output_file.write("<!DOCTYPE KEEPASSX_DATABASE>")
        xml_document.write(output_file)


def print_and_exit(error_message):
    """Print an error message then exit."""
    formatted_print(error_message)
    sys.exit()


def formatted_print(string):
    """Print a string between two horizontal lines."""
    print HORIZ_LINE
    print string
    print HORIZ_LINE


if __name__ == '__main__':
    main()
