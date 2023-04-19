import glob

def main():
    folder_contents_output = ""
    cur_folder_index = 0

    for folder_filename in glob.glob("good_folders/*.txt"):
        folder_contents_output += f"Folder_{cur_folder_index}:\n"

        with open(folder_filename, "r") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue

                chip_name, chip_code = line.split(" ", maxsplit=1)
                constant_chip_name = chip_name.upper().replace("-", "_").replace("+", "_")
                constant_chip_code = f"CODE_{'ASTERISK' if chip_code == '*' else chip_code.upper()}"
                folder_contents_output += f"\tchip_and_code {constant_chip_name}, {constant_chip_code}\n"

        folder_contents_output += "\n"
        cur_folder_index += 1

    output = ""
    output += "FolderTable_NEW:\n"

    for i in range(cur_folder_index):
        output += f"\t.word Folder_{i}\n"

    for i in range(cur_folder_index, 60):
        output += f"\t.word StartingFolder ; {i}\n"

    output += "\n"
    output += folder_contents_output

    with open("folders.asm", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
