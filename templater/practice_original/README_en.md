# Introduction

This script uses 3 major packages :

- python-docx-template (https://github.com/elapouya/python-docx-template) for generating docx document from template
- secretary (https://github.com/christopher-ramirez/secretary) for generating docx document from template
- jinja2 for managing tags inserted into the template (used in both 2 packages above)

The tool will automatically fill out document templates (docx, odt) with data from the table (each column is a separate field to be inserted, each line is a new document).

### Input:
- CSV file with lookup values (delimiter ';' & encoding UTF-8)
- Template path in the format docx, odt
- Text file naming pattern

Example CSV file:

    FirstName, LastName, Address, City, State, ZIP-code
    John, Doe, 120 jefferson st., Riverside, NJ, 08075
    Jack, McGinnis, 220 hobo Av., Phila, PA, 09119
    "John" "Da Man" "", Repici, 120 Jefferson St., Riverside, NJ, 08075
    Stephen, Tyler, "7452 Terrace" "At the Plaza" "road", SomeTown, SD, 91234
    , Blankman ,, SomeTown, SD, 00298
    "Joan" "the bone" ", Anne", Jet, "9th, at Terrace plc", Desert City, CO, 00123

Accordingly, the fields for the substitution are: FirstName, LastName, Adress, City, State, ZIP-code.

The docx, odt, pptx, odp file contains the above substitution fields in the form of labels of the following form:

{{ Address }}

The text file naming pattern contains a combination of lookup fields:

{{FirstName}} {{LastName}}.docx

### Output: 

As a result of the work, 6 files should appear, one for each line of the CSV file.

---

# Install and usage

### Install manually

- Install Python3 and pip3

On Ubuntu:

    apt-get update
    apt-get install -y python3 python3-pip

On Windows better using provided installer on the homepage.

- Install dependencies:

    pip install -r app/requirements.txt

- Run the script:

    python app/main.py

### Install on docker

Build docker image

    docker build -t templater .

Run in the container (*)

    docker run --rm --volume PATH_TO_DOC_DIR_ON_HOST:/data templater
    
Pretty much just run the image in a container, mount a directory with template/csv file.

NOTE: the python /app/main.py is configured as ENTRYPOINT, so you just need to put in the parameter of the script after the command (*)

### Usage:

    main.py [-h] [--out-dir OUTPUT_DIR] [--out-name OUTPUT_NAME]
                [--delimiter DELIMITER] [--verify-only]
                csv_path template_path

    positional arguments:
    csv_path              The path to the csv file containing the data table
    template_path         The path to the template file (odt, docx)

    optional arguments:
    -h, --help            show this help message and exit
    --out-dir OUTPUT_DIR, -D OUTPUT_DIR
                            Path to output directory
    --out-name OUTPUT_NAME, -o OUTPUT_NAME
                            Template for the output file names (default = first
                            column's header in csv)
    --delimiter DELIMITER, -d DELIMITER
                            Delimiter used in the csv file (default = ',')
    --verify-only, -v     Verify the template against the csv without creating
                            the result files

### Example calling the scripts on test sets

Each test set contains a csv file and 1 or more templates (each provided in both odt and docx)

#### test0: 

Task provided example csv + business card template

    python app/main.py tests/test0/taskEg.csv tests/test0/bizCard.docx -o "{{ FirstName }}_{{ LastName }}" -D ./output

    python app/main.py tests/test0/taskEg.csv tests/test0/bizCard.odt -o "{{ FirstName }}_{{ LastName }}" -D ./output

#### test1: 

The template simple is very simple without styling

    python app/main.py tests/test1/simple.csv tests/test1/simple.docx -o "{{ first_name }}_{{ last_name }}" -D ./output

    python app/main.py tests/test1/simple.csv tests/test1/simple.odt -o "{{ first_name }}_{{ last_name }}" -D ./output

The template missing_param is same as the one above, but purposedly written with mismatch in fields compared to the csv file, in order to test the warning function of the script

    python app/main.py tests/test1/simple.csv tests/test1/missing_param.docx -o "{{ first_name }}_{{ last_name }}" -D ./output

    python app/main.py tests/test1/simple.csv tests/test1/missing_param.odt -o "{{ first_name }}_{{ last_name }}" -D ./output

#### test2:

Laboratory work's title list

    python app/main.py tests/test2/stud_teacher.csv tests/test2/title_page_temp.docx -o "{{ student_name }}_{{ lab_no }}" -D ./output

    python app/main.py tests/test2/stud_teacher.csv tests/test2/title_page_temp.odt -o "{{ student_name }}_{{ lab_no }}" -D ./output

#### test3:

A flyer with 4 fields

    python app/main.py tests/test3/flyer.csv tests/test3/flyer.docx -o "{{ event_name }}_{{ date }}" -D ./output

    python app/main.py tests/test3/flyer.csv tests/test3/flyer.odt -o "{{ event_name }}_{{ date }}" -D ./output

#### test4:

cover-letter template from office16

    python app/main.py tests/test4/info.csv tests/test4/cover_letter.docx -o "{{ name }}" -D ./output

    python app/main.py tests/test4/info.csv tests/test4/cover_letter.docx -o "{{ name }}" -D ./output