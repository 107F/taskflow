import os

def consolidate_code_by_structure(output_file='all_code_structure.txt'):
    with open(output_file, 'w') as outfile:
        # Walk through the directory
        for root, dirs, files in os.walk('.'):
            # Exclude the .git directory and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Write the directory as a header
            outfile.write(f'\n--- Directory: {root} ---\n')
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue

                # Filter for specific file types
                if file.endswith(('.py', '.html', '.css', '.js', '.md', '.txt')):
                    file_path = os.path.join(root, file)
                    
                    # Write the file name as a sub-header
                    outfile.write(f'\nFile: {file}\n')
                    outfile.write('----------------------------\n')

                    # Write the content of the file
                    with open(file_path, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n\n')

# Run the function
consolidate_code_by_structure()
