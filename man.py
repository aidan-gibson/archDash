import os, sqlite3, subprocess

# Ensure directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Base directory for .docset
base_dir = os.path.join(os.getcwd(), 'Arch-manpages.docset')
docpath = os.path.join(base_dir, 'Contents/Resources/Documents')
ensure_dir(docpath)

# Connect to the database and set up a cursor
db_path = os.path.join(base_dir, 'Contents/Resources/docSet.dsidx')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Recreate the searchIndex table
try:
    cur.execute('DROP TABLE searchIndex;')
except sqlite3.OperationalError:
    pass

cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

# MANPATH directories to scan
man_paths = os.environ.get('MANPATH', '/usr/share/man:/usr/local/share/man').split(':')
man_paths.extend(['/usr/share/man', '/usr/local/share/man'])

# Iterate over MANPATH directories and convert man pages
for man_path in man_paths:
    for root, dirs, files in os.walk(man_path):
        for file in files:
            input_path = os.path.join(root, file)
            name = os.path.splitext(file)[0]
            output_filename = f"{name}.html"
            output_path = os.path.join(docpath, output_filename)

            # Correctly handling output redirection within Python
            with open(output_path, 'w') as output_file:
                subprocess.run(['mandoc', '-T', 'html', input_path], stdout=output_file)
            
            # Insert into the database, skipping if conversion fails or file is 'index.html'
            if os.path.exists(output_path) and file != 'index.html':
                rel_path = os.path.relpath(output_path, docpath)
                cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'func', rel_path))
                print(f'name: {name}, path: {rel_path}')

# Commit changes and close the database connection
conn.commit()
conn.close()


# copy to /home/bruh/.local/share/Zeal/Zeal/docsets 
# cp -r Arch-manpages.docset/ /home/bruh/.local/share/Zeal/Zeal/docsets/ (for local arch zeal). btw ftp-ing this shit to mac came out fucked up; rsync -avz Arch-manpages.docset aidangibson@10.0.0.14:/Users/aidangibson/Downloads
# tar --exclude='.DS_Store' -cvzf Arch-manpages.tgz Arch-manpages.docset (for feed)